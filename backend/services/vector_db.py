import os
from typing import List, Dict, Any, Optional
import logging
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
import requests
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self):
        self.collection_name = "pensieve_documents"
        # Qdrant can be used via HTTP if a server is running, or in embedded mode if available
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.use_remote = True
        self.client: Optional[QdrantClient] = None
        self.vector_size = int(os.getenv("EMBEDDING_DIM", "1536"))
        self.distance = qmodels.Distance.COSINE
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings()
    
    async def initialize(self):
        """Initialize Qdrant client and collection"""
        try:
            # Ensure server is reachable
            try:
                requests.get(self.qdrant_url + "/")
            except Exception:
                logger.warning("⚠️ Qdrant server not reachable at %s. Make sure Qdrant is running.", self.qdrant_url)
            
            self.client = QdrantClient(url=self.qdrant_url)
            
            if not self.client.collection_exists(self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(size=self.vector_size, distance=self.distance)
                )
            
            logger.info("✅ Qdrant initialized (collection: %s)", self.collection_name)
            return True
        except Exception as e:
            logger.error(f"❌ Qdrant initialization failed: {e}")
            raise e

    async def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add documents to Qdrant with real embeddings."""
        try:
            if not self.client:
                await self.initialize()

            points = []
            for doc in documents:
                # Generate real embeddings using OpenAI
                content = doc.get("content", "")
                if content:
                    try:
                        embedding = self.embeddings.embed_query(content)
                        payload = {**doc.get("metadata", {}), "content": content}
                        points.append(qmodels.PointStruct(id=doc["id"], vector=embedding, payload=payload))
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to generate embedding for doc {doc['id']}: {e}")
                        # Fallback to placeholder vector
                        payload = {**doc.get("metadata", {}), "content": content}
                        points.append(qmodels.PointStruct(id=doc["id"], vector=[0.0] * self.vector_size, payload=payload))
                else:
                    # Empty content, use placeholder
                    payload = {**doc.get("metadata", {}), "content": content}
                    points.append(qmodels.PointStruct(id=doc["id"], vector=[0.0] * self.vector_size, payload=payload))

            if points:
                self.client.upsert(collection_name=self.collection_name, points=points)
                logger.info("✅ Added %d documents to Qdrant with embeddings", len(points))
            else:
                logger.warning("⚠️ No valid documents to add")

            return {"success": True, "count": len(points)}
        except Exception as e:
            logger.error(f"❌ Error adding documents to Qdrant: {e}")
            raise e

    async def search_documents(
        self,
        query: str,
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search similar documents using Qdrant with real embeddings."""
        try:
            if not self.client:
                await self.initialize()

            # Generate query embedding
            try:
                query_embedding = self.embeddings.embed_query(query)
            except Exception as e:
                logger.error(f"❌ Failed to generate query embedding: {e}")
                return {"success": False, "documents": [], "error": "Failed to generate query embedding"}

            # Search in Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True
            )

            # Convert results to our format
            documents = []
            for point in search_result:
                documents.append({
                    "id": str(point.id),
                    "content": point.payload.get("content", ""),
                    "metadata": {k: v for k, v in point.payload.items() if k != "content"},
                    "score": point.score
                })

            logger.info("✅ Found %d similar documents", len(documents))
            return {"success": True, "documents": documents}
        except Exception as e:
            logger.error(f"❌ Error searching Qdrant: {e}")
            raise e

    async def delete_document(self, document_id: str) -> Dict[str, Any]:
        try:
            if not self.client:
                await self.initialize()
            self.client.delete(collection_name=self.collection_name, points_selector=qmodels.PointIdsList(points=[document_id]))
            logger.info("✅ Deleted document %s from Qdrant", document_id)
            return {"success": True}
        except Exception as e:
            logger.error(f"❌ Error deleting document from Qdrant: {e}")
            raise e

    async def get_collection_stats(self) -> Dict[str, Any]:
        try:
            if not self.client:
                await self.initialize()
            info = self.client.get_collection(self.collection_name)
            # Get the points count from the collection info
            points_count = getattr(info, "points_count", 0)
            return {
                "success": True,
                "count": points_count,
                "collection_name": self.collection_name,
                "engine": "qdrant"
            }
        except Exception as e:
            logger.error(f"❌ Error getting Qdrant stats: {e}")
            raise e
