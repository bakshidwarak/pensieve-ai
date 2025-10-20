from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from models.schemas import (
    ChatRequest, ChatResponse, DocumentIngestRequest, DocumentIngestResponse,
    ClearAndIngestRequest, StatsResponse
)
# Defer AgentSystem import to avoid hard failure if LLM deps are missing
# Try Graph Agent first, then fallback to original
try:
    from agents.graph_agent import GraphAgentSystem  # type: ignore
    AgentSystem = GraphAgentSystem  # Use Graph version
    print("✅ Using Graph AgentSystem")
except Exception as e:
    print(f"⚠️ Graph AgentSystem failed: {e}")
    try:
        from agents.agent_system import AgentSystem  # type: ignore
        print("✅ Using original AgentSystem as fallback")
    except Exception as e2:
        print(f"⚠️ Original AgentSystem also failed: {e2}")
        AgentSystem = None  # type: ignore
from services.document_ingestion import DocumentIngestionService

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
agent_system = None  # Will be initialized in startup_event
document_ingestion = DocumentIngestionService()

# Initialize on startup
@router.on_event("startup")
async def startup_event():
    global agent_system
    
    # Load API key from config file if available
    try:
        import json
        import os
        config_file = "./data/config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                if config.get("openai_api_key"):
                    os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
                    logger.info("✅ API key loaded from config file")
    except Exception as e:
        logger.warning(f"⚠️ Could not load API key from config: {e}")
    
    # Initialize agent system after API key is loaded
    try:
        if AgentSystem:
            agent_system = AgentSystem()
            logger.info("✅ Agent system initialized successfully")
        else:
            logger.warning("⚠️ AgentSystem not available - RAG features disabled")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent system: {e}")
        agent_system = None
    
    await document_ingestion.initialize()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message through RAG system"""
    try:
        if not agent_system:
            return ChatResponse(
                success=False,
                response="Chat is temporarily unavailable due to configuration issues. Please try again later.",
                error="RAG agent system not initialized"
            )
        logger.info(f"💬 Processing chat message: {request.message}")
        
        # Process query through agent system
        result = await agent_system.process_query(request.message, request.context or "")
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to process query"))
        
        return ChatResponse(
            success=True,
            response=result["response"],
            sources={
                "meeting_notes": len(result.get("meeting_results", [])),
                "web_results": len(result.get("web_results", []))
            },
            analysis=result.get("analysis")
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        return ChatResponse(
            success=False,
            response="Sorry, there was an error processing your request. Please try again.",
            error=str(e)
        )

@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(request: DocumentIngestRequest):
    """Ingest a document for processing"""
    try:
        logger.info("📄 Ingesting document...")
        
        result = await document_ingestion.ingest_document(
            request.content, 
            request.metadata or {}
        )
        
        return DocumentIngestResponse(
            success=result["success"],
            message=result["message"],
            chunk_count=None,
            backup_path=None,
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"❌ Document ingestion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest document")

@router.post("/clear-and-ingest", response_model=DocumentIngestResponse)
async def clear_and_ingest(request: ClearAndIngestRequest):
    """Clear screen and ingest content immediately"""
    try:
        logger.info("🧹 Clearing and ingesting content...")
        
        result = await document_ingestion.clear_and_ingest(
            request.content,
            request.metadata or {}
        )
        
        return DocumentIngestResponse(
            success=result["success"],
            message=result["message"],
            chunk_count=result.get("chunk_count"),
            backup_path=result.get("backup_path"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"❌ Clear and ingest error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear and ingest content")

@router.post("/force-process")
async def force_process():
    """Force process all pending documents"""
    try:
        logger.info("🚀 Force processing all pending documents...")
        
        result = await document_ingestion.force_process_all()
        return result
        
    except Exception as e:
        logger.error(f"❌ Force process error: {e}")
        raise HTTPException(status_code=500, detail="Failed to force process documents")

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get ingestion statistics"""
    try:
        stats = await document_ingestion.get_ingestion_stats()
        return StatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"❌ Get stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

@router.delete("/clear-all")
async def clear_all_data():
    """Clear all data"""
    try:
        logger.info("🗑️ Clearing all data...")
        
        result = await document_ingestion.clear_all_data()
        return result
        
    except Exception as e:
        logger.error(f"❌ Clear all data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear all data")

@router.get("/health")
async def health_check():
    """RAG system health check"""
    try:
        stats = await document_ingestion.get_ingestion_stats()
        
        return {
            "success": True,
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

