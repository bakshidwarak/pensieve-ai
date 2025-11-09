"""AI-specific endpoints for RAG, agents, and specialized tools."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.api.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


class RAGRequest(BaseModel):
    """RAG query request."""

    query: str
    top_k: int = 5


class RAGResponse(BaseModel):
    """RAG query response."""

    answer: str
    sources: List[dict]


class AgentRequest(BaseModel):
    """Agent execution request."""

    task: str
    agent_type: str = "simple"


class AgentResponse(BaseModel):
    """Agent execution response."""

    result: str
    steps: List[dict]
    tool_calls: Optional[List[dict]] = None


@router.post("/rag", response_model=RAGResponse)
async def query_rag(request: RAGRequest):
    """
    Query the RAG system.

    Retrieves relevant documents and generates a contextual answer.
    """
    try:
        response = await ai_service.query_rag(
            query=request.query,
            top_k=request.top_k,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """
    Execute an AI agent.

    Supports:
    - simple: Basic tool-using agent
    - helpfulness: Agent with evaluation loop
    """
    try:
        response = await ai_service.run_agent(
            task=request.task,
            agent_type=request.agent_type,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def list_tools():
    """List available AI tools."""
    return {
        "tools": [
            {"name": "tavily_search", "description": "Web search"},
            {"name": "arxiv", "description": "Academic paper search"},
            {"name": "retrieve_information", "description": "RAG-based document Q&A"},
        ]
    }
