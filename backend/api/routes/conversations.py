"""API routes for Difficult Conversations Practice Coach."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid

from backend.conversations import (
    conversation_coach_agent,
    generate_initial_response,
    generate_feedback
)
from backend.conversations.tts import generate_speech

router = APIRouter()

# In-memory session storage (in production, use Redis or database)
conversation_sessions: Dict[str, Dict] = {}


class StartConversationRequest(BaseModel):
    """Request to start a new conversation practice session."""
    situation: str
    message_to_deliver: str
    other_party_gender: str  # 'male' or 'female'
    difficulty_level: int  # 1-10


class RespondRequest(BaseModel):
    """Request to get other party's response."""
    user_message: str


class FeedbackRequest(BaseModel):
    """Request to get coaching feedback."""
    conversation_transcript: str


class ConversationResponse(BaseModel):
    """Response from the conversation system."""
    session_id: str
    response: str
    audio_url: str


class FeedbackResponse(BaseModel):
    """Coaching feedback response."""
    feedback: str


@router.post("/start", response_model=ConversationResponse)
async def start_conversation(request: StartConversationRequest):
    """Start a new difficult conversation practice session."""
    session_id = str(uuid.uuid4())

    # Generate initial response from other party
    initial_response = generate_initial_response(
        situation=request.situation,
        message_to_deliver=request.message_to_deliver,
        difficulty_level=request.difficulty_level,
        gender=request.other_party_gender
    )

    # Generate audio for initial response
    audio_url = generate_speech(
        text=initial_response,
        gender=request.other_party_gender
    )

    # Store session
    conversation_sessions[session_id] = {
        "situation": request.situation,
        "message_to_deliver": request.message_to_deliver,
        "difficulty_level": request.difficulty_level,
        "gender": request.other_party_gender,
        "conversation_history": [
            {"role": "other_party", "content": initial_response}
        ]
    }

    return ConversationResponse(
        session_id=session_id,
        response=initial_response,
        audio_url=audio_url
    )


@router.post("/respond/{session_id}", response_model=ConversationResponse)
async def get_response(session_id: str, request: RespondRequest):
    """Get the other party's response to user's message."""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    session = conversation_sessions[session_id]

    # Add user message to history
    session["conversation_history"].append({
        "role": "user",
        "content": request.user_message
    })

    # Get other party's response
    response = conversation_coach_agent(
        situation=session["situation"],
        message_to_deliver=session["message_to_deliver"],
        difficulty_level=session["difficulty_level"],
        gender=session["gender"],
        conversation_history=session["conversation_history"],
        user_message=request.user_message
    )

    # Generate audio
    audio_url = generate_speech(
        text=response,
        gender=session["gender"]
    )

    # Add response to history
    session["conversation_history"].append({
        "role": "other_party",
        "content": response
    })

    return ConversationResponse(
        session_id=session_id,
        response=response,
        audio_url=audio_url
    )


@router.post("/feedback/{session_id}", response_model=FeedbackResponse)
async def get_feedback(session_id: str, request: FeedbackRequest):
    """Generate coaching feedback on the conversation."""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    session = conversation_sessions[session_id]

    # Generate feedback
    feedback = generate_feedback(
        situation=session["situation"],
        message_to_deliver=session["message_to_deliver"],
        difficulty_level=session["difficulty_level"],
        conversation_transcript=request.conversation_transcript
    )

    return FeedbackResponse(feedback=feedback)


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get the current state of a conversation session."""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    return {
        "session_id": session_id,
        **conversation_sessions[session_id]
    }


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """End a conversation session and clean up."""
    if session_id not in conversation_sessions:
        raise HTTPException(status_code=404, detail="Conversation session not found")

    del conversation_sessions[session_id]

    return {"message": "Conversation session ended successfully"}
