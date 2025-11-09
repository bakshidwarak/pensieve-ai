# app/embeddings_store.py
import os
from typing import Optional, Dict, List
from app.config import settings

# Use the official OpenAI client directly to avoid LangChain embedding wrapper issues
import openai

# Ensure API key is set
openai.api_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")

# Small wrapper class that provides the two methods LangChain vectorstores expect:
# - embed_documents(list[str]) -> list[list[float]]
# - embed_query(str) -> list[float]
class OpenAIEmbedder:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model

    def embed_query(self, text: str) -> List[float]:
        # Synchronous call to OpenAI embeddings endpoint
        resp = openai.Embedding.create(model=self.model, input=text)
        return resp["data"][0]["embedding"]

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        if not isinstance(documents, list):
            documents = [documents]
        resp = openai.Embedding.create(model=self.model, input=documents)
        # returns a list of embeddings in the same order
        return [r["embedding"] for r in resp["data"]]

# Instantiate a single embedder instance
EMBEDDER = OpenAIEmbedder(model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))

# Vector store logic — keep Pinecone option and FAISS fallback.
try:
    import pinecone
except Exception:
    pinecone = None

from langchain.vectorstores import Pinecone, FAISS
from langchain.docstore.document import Document

class VectorStore:
    def __init__(self):
        self.use_pinecone = bool(settings.USE_PINECONE and settings.PINECONE_API_KEY and pinecone)
        if self.use_pinecone:
            # initialize pinecone client
            pinecone.init(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENV)
            if settings.PINECONE_INDEX not in pinecone.list_indexes():
                pinecone.create_index(settings.PINECONE_INDEX, dimension=settings.VECTOR_DIM)
            self.index = pinecone.Index(settings.PINECONE_INDEX)
            # For Pinecone via LangChain, pass a callable that takes a single text string and returns embedding vector
            self.store = Pinecone(self.index, EMBEDDER.embed_query, "id")
        else:
            # FAISS local
            os.makedirs(os.path.dirname(settings.FAISS_PATH) or ".", exist_ok=True)
            self.store_path = settings.FAISS_PATH
            try:
                # if already persisted, load it
                self.store = FAISS.load_local(self.store_path, EMBEDDER)
            except Exception:
                # create empty store
                self.store = FAISS.from_documents([], EMBEDDER)

    async def add_note(self, doc_id: str, text: str, metadata: Optional[Dict] = None):
        # Create a LangChain Document with the note text; metadata includes id and tags
        doc = Document(page_content=text, metadata={"id": doc_id, **(metadata or {})})
        # LangChain FAISS/Pinecone expects synchronous operations here (LangChain v0.x)
        self.store.add_documents([doc])
        if not self.use_pinecone:
            # persist local FAISS index
            self.store.save_local(self.store_path)

    async def similarity_search(self, query: str, k: int = 4, filters: Optional[Dict] = None):
        results = self.store.similarity_search(query, k=k)
        return results

# single instance
vector_store = VectorStore()
