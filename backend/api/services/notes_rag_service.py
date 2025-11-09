"""RAG service specifically for querying user notes."""

from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI  # Changed from Together to OpenAI
from backend.core.vector_store import get_vector_store
from backend.core.config import settings


class NotesRAGService:
    """Service for RAG operations on user notes."""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Using OpenAI instead of Together
            temperature=0,
            max_retries=2,
        )

    def query_notes(
        self,
        query: str,
        tag_filter: Optional[List[str]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Query user notes and generate an answer.

        Args:
            query: User's question
            tag_filter: Optional tags to filter notes
            top_k: Number of notes to retrieve

        Returns:
            Dict with answer and source notes
        """
        # Retrieve relevant notes
        results = self.vector_store.search_notes(
            query=query,
            tag_filter=tag_filter,
            limit=top_k
        )

        if not results:
            return {
                "answer": "I couldn't find any relevant notes to answer your question.",
                "sources": [],
                "note_ids": []
            }

        # Build context from retrieved notes
        context_parts = []
        for idx, result in enumerate(results, 1):
            context_parts.append(
                f"Note {idx} (score: {result['score']:.3f}):\n"
                f"Title: {result['metadata'].get('title', 'Untitled')}\n"
                f"Tags: {', '.join(result['metadata'].get('tags', []))}\n"
                f"Content: {result['content']}\n"
            )

        context = "\n\n".join(context_parts)

        # Create prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are Pensieve.ai, an AI assistant that helps users find information in their personal notes."),
            ("human", """Based on the following notes from the user's Pensieve, answer their question.

NOTES:
{context}

QUESTION: {query}

Provide a helpful, concise answer based ONLY on the information in the notes above. If the notes don't contain enough information to fully answer the question, say so. Always cite which note(s) you're referencing (e.g., "According to Note 1..." or "Your meeting notes mention...").""")
        ])

        # Generate answer
        chain = prompt_template | self.llm | StrOutputParser()

        answer = chain.invoke({
            "context": context,
            "query": query
        })

        # Format sources
        sources = [
            {
                "note_id": result["note_id"],
                "title": result["metadata"].get("title", "Untitled"),
                "tags": result["metadata"].get("tags", []),
                "score": result["score"],
                "snippet": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
            }
            for result in results
        ]

        return {
            "answer": answer,
            "sources": sources,
            "note_ids": [r["note_id"] for r in results]
        }

    def chat_with_notes(
        self,
        messages: List[Dict[str, str]],
        tag_filter: Optional[List[str]] = None
    ) -> str:
        """
        Chat with context from notes.

        Args:
            messages: Conversation history
            tag_filter: Optional tag filter

        Returns:
            AI response
        """
        # Get the last user message as query
        last_user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break

        if not last_user_message:
            return "I need a question to search your notes."

        # Query notes
        result = self.query_notes(
            query=last_user_message,
            tag_filter=tag_filter,
            top_k=3
        )

        return result["answer"]


# Singleton
_notes_rag_service = None


def get_notes_rag_service() -> NotesRAGService:
    """Get or create notes RAG service."""
    global _notes_rag_service
    if _notes_rag_service is None:
        _notes_rag_service = NotesRAGService()
    return _notes_rag_service
