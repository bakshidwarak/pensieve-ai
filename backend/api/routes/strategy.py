"""API routes for Strategy Coach."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid

from backend.strategy import strategy_coach_agent, generate_initial_analysis

router = APIRouter()

# In-memory session storage (in production, use Redis or database)
strategy_sessions: Dict[str, Dict] = {}


class StartStrategyRequest(BaseModel):
    """Request to start a new strategy coaching session."""
    strategy_text: str


class StrategyMessageRequest(BaseModel):
    """Request to send a message in a strategy session."""
    message: str
    current_strategy: Optional[str] = None


class StrategyResponse(BaseModel):
    """Response from the strategy coach."""
    session_id: str
    response: str


@router.post("/start", response_model=StrategyResponse)
async def start_strategy_session(request: StartStrategyRequest):
    """Start a new strategy coaching session."""
    session_id = str(uuid.uuid4())

    # Generate initial analysis
    initial_response = generate_initial_analysis(request.strategy_text)

    # Store session
    strategy_sessions[session_id] = {
        "strategy_text": request.strategy_text,
        "conversation_history": [
            {"role": "assistant", "content": initial_response}
        ]
    }

    return StrategyResponse(
        session_id=session_id,
        response=initial_response
    )


@router.post("/message/{session_id}", response_model=StrategyResponse)
async def send_strategy_message(session_id: str, request: StrategyMessageRequest):
    """Send a message in an ongoing strategy session."""
    if session_id not in strategy_sessions:
        raise HTTPException(status_code=404, detail="Strategy session not found")

    session = strategy_sessions[session_id]

    # Update strategy text if provided
    if request.current_strategy:
        session["strategy_text"] = request.current_strategy

    # Add user message to history
    session["conversation_history"].append({
        "role": "user",
        "content": request.message
    })

    # Get coach response
    response = strategy_coach_agent(
        strategy_text=session["strategy_text"],
        conversation_history=session["conversation_history"],
        user_message=request.message
    )

    # Add coach response to history
    session["conversation_history"].append({
        "role": "assistant",
        "content": response
    })

    return StrategyResponse(
        session_id=session_id,
        response=response
    )


@router.get("/session/{session_id}")
async def get_strategy_session(session_id: str):
    """Get the current state of a strategy session."""
    if session_id not in strategy_sessions:
        raise HTTPException(status_code=404, detail="Strategy session not found")

    return {
        "session_id": session_id,
        "strategy_text": strategy_sessions[session_id]["strategy_text"],
        "conversation_history": strategy_sessions[session_id]["conversation_history"]
    }


@router.delete("/session/{session_id}")
async def end_strategy_session(session_id: str):
    """End a strategy session and clean up."""
    if session_id not in strategy_sessions:
        raise HTTPException(status_code=404, detail="Strategy session not found")

    del strategy_sessions[session_id]

    return {"message": "Strategy session ended successfully"}
