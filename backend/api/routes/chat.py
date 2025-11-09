"""Chat endpoints for conversational AI."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.api.services.chat_service import ChatService
from backend.api.services.notes_rag_service import get_notes_rag_service

router = APIRouter()
chat_service = ChatService()


class Message(BaseModel):
    """Chat message model."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""

    messages: List[Message]
    use_rag: bool = False
    use_notes: bool = True  # Query user's notes by default
    tag_filter: Optional[List[str]] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat response model."""

    message: Message
    tool_calls: Optional[List[dict]] = None
    sources: Optional[List[dict]] = None  # For notes sources


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.

    Supports:
    - Simple conversational chat
    - RAG-enhanced responses from documents
    - Query user's notes (default)
    - Tool calling (search, arxiv, etc.)
    """
    try:
        # If using notes, query the notes RAG system
        if request.use_notes:
            notes_rag = get_notes_rag_service()

            # Convert messages to dict format
            messages_dict = [msg.model_dump() for msg in request.messages]

            # Get response from notes
            answer = notes_rag.chat_with_notes(
                messages=messages_dict,
                tag_filter=request.tag_filter
            )

            return ChatResponse(
                message=Message(role="assistant", content=answer),
                tool_calls=None,
                sources=None  # TODO: Return sources
            )

        # Otherwise use the regular chat service
        response = await chat_service.process_chat(
            messages=request.messages,
            use_rag=request.use_rag,
        )
        return ChatResponse(**response, sources=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notes/query")
async def query_notes(
    query: str,
    tag_filter: Optional[List[str]] = None,
    top_k: int = 5
):
    """
    Query notes directly without chat context.

    Returns answer and source notes.
    """
    try:
        notes_rag = get_notes_rag_service()
        result = notes_rag.query_notes(
            query=query,
            tag_filter=tag_filter,
            top_k=top_k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint (to be implemented)."""
    raise HTTPException(status_code=501, detail="Streaming not yet implemented")
