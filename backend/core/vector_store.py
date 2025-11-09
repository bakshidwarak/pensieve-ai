"""Vector store management for note embeddings."""

import os
import uuid
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from langchain_openai import OpenAIEmbeddings  # Changed from Together to OpenAI
from backend.core.config import settings


class VectorStore:
    """Persistent Qdrant vector store for notes."""

    def __init__(self):
        """Initialize Qdrant client with in-memory storage (to avoid lock issues with --reload)."""
        # Use in-memory Qdrant to avoid file locking issues during development
        self.client = QdrantClient(location=":memory:")
        self.collection_name = "pensieve_notes"

        # Initialize embedding model (using OpenAI instead of Together for now)
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        # Get embedding dimension
        self.embedding_dim = 1536  # text-embedding-3-small dimension

        # Create collection if it doesn't exist
        self._init_collection()

    def _init_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                ),
            )

    def add_note(
        self,
        note_id: int,
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Add a note to the vector store.

        Args:
            note_id: Database ID of the note
            content: Text content to embed
            metadata: Additional metadata (tags, title, etc.)

        Returns:
            vector_id: Unique ID for the vector
        """
        # Generate vector ID
        vector_id = str(uuid.uuid4())

        # Generate embedding
        embedding = self.embedding_model.embed_query(content)

        # Create point
        point = PointStruct(
            id=vector_id,
            vector=embedding,
            payload={
                "note_id": note_id,
                "content": content[:1000],  # Store snippet for retrieval
                "metadata": metadata,
            }
        )

        # Upsert to collection
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return vector_id

    def update_note(
        self,
        vector_id: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        """Update an existing note in the vector store."""
        # Get note_id from existing point
        existing = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[vector_id]
        )

        if not existing:
            raise ValueError(f"Vector ID {vector_id} not found")

        note_id = existing[0].payload["note_id"]

        # Re-embed with new content
        embedding = self.embedding_model.embed_query(content)

        # Update point
        point = PointStruct(
            id=vector_id,
            vector=embedding,
            payload={
                "note_id": note_id,
                "content": content[:1000],
                "metadata": metadata,
            }
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def delete_note(self, vector_id: str):
        """Delete a note from the vector store."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[vector_id]
        )

    def search_notes(
        self,
        query: str,
        tag_filter: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search notes by semantic similarity.

        Args:
            query: Search query
            tag_filter: Optional list of tags to filter by
            limit: Maximum number of results

        Returns:
            List of matching notes with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)

        # Build filter if tags specified
        search_filter = None
        if tag_filter:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="metadata.tags",
                        match=MatchValue(any=tag_filter)
                    )
                ]
            )

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=limit
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "note_id": result.payload["note_id"],
                "content": result.payload["content"],
                "metadata": result.payload.get("metadata", {}),
                "score": result.score,
            })

        return formatted_results

    def get_all_notes(self) -> List[Dict[str, Any]]:
        """Retrieve all notes from vector store."""
        # This is for admin purposes - in production, implement pagination
        # For now, we'll use scroll API
        results = self.client.scroll(
            collection_name=self.collection_name,
            limit=1000  # Adjust as needed
        )

        formatted_results = []
        for point in results[0]:  # results is a tuple (points, next_offset)
            formatted_results.append({
                "vector_id": point.id,
                "note_id": point.payload["note_id"],
                "content": point.payload["content"],
                "metadata": point.payload.get("metadata", {}),
            })

        return formatted_results


# Singleton instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
