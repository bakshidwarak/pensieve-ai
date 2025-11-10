"""API routes for Interview Wizard."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from langchain_core.messages import HumanMessage
import PyPDF2
import io

from backend.interview import create_interview_graph, InterviewState


router = APIRouter()

# In-memory session storage (in production, use Redis or database)
interview_sessions = {}


class StartInterviewRequest(BaseModel):
    """Request to start a new interview session."""
    candidate_name: str
    position: str
    interview_rubric: str
    resume_text: Optional[str] = None  # Extracted resume text


class InterviewMessageRequest(BaseModel):
    """Request to send a message in an interview session."""
    session_id: str
    message: str
    transcript_entry: Optional[str] = None  # Optional transcript entry


class FeedbackRequest(BaseModel):
    """Request to generate final feedback."""
    hire_decision: str  # "hire" or "no-hire"
    decision_reason: str  # Interviewer's final remarks


class InterviewResponse(BaseModel):
    """Response from the interview system."""
    session_id: str
    response: str
    suggested_questions: Optional[List[str]] = None
    coaching_feedback: Optional[List[str]] = None
    structured_notes: Optional[str] = None
    strengths: Optional[List[str]] = None
    areas_of_improvement: Optional[List[str]] = None


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract text from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


@router.post("/start", response_model=InterviewResponse)
async def start_interview(
    candidate_name: str = Form(...),
    position: str = Form(...),
    interview_rubric: str = Form(...),
    resume: Optional[UploadFile] = File(None)
):
    """Start a new interview session."""
    import uuid

    session_id = str(uuid.uuid4())

    # Extract resume text if provided
    resume_text = ""
    if resume:
        pdf_content = await resume.read()
        resume_text = extract_text_from_pdf(pdf_content)

    # Initialize the interview graph
    graph = create_interview_graph()

    # Build initial message with resume context
    initial_message = f"Starting interview for {candidate_name} for {position} position. Here is the rubric: {interview_rubric}"
    if resume_text:
        initial_message += f"\n\nCandidate's Resume:\n{resume_text}"

    # Create initial state
    initial_state: InterviewState = {
        "messages": [
            HumanMessage(content=initial_message)
        ],
        "interview_rubric": interview_rubric,
        "candidate_name": candidate_name,
        "position": position,
        "interview_transcript": [],
        "structured_notes": None,
        "suggested_questions": [],
        "current_topic": None,
        "coaching_feedback": [],
        "brainstorm_messages": [],
        "strengths": [],
        "areas_of_improvement": [],
        "hire_decision": None,
        "final_feedback": None,
        "next_agent": None
    }

    # Run the graph to get initial suggestions
    result = graph.invoke(initial_state)

    # Store session
    interview_sessions[session_id] = {
        "graph": graph,
        "state": result
    }

    return InterviewResponse(
        session_id=session_id,
        response="Interview session started! I'm Interview Genie, and I'm here to help you conduct an excellent interview. I have your rubric and I'm ready to assist with questions, note-taking, and coaching.",
        suggested_questions=result.get("suggested_questions", []),
        structured_notes=result.get("structured_notes")
    )


@router.post("/message", response_model=InterviewResponse)
async def send_message(request: InterviewMessageRequest):
    """Send a message in an ongoing interview session."""
    if request.session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")

    session = interview_sessions[request.session_id]
    graph = session["graph"]
    current_state = session["state"]

    # Add new message to state
    new_messages = [HumanMessage(content=request.message)]

    # Add transcript entry if provided
    new_transcript = []
    if request.transcript_entry:
        new_transcript = [request.transcript_entry]

    # Update state
    updated_state = {
        **current_state,
        "messages": current_state.get("messages", []) + new_messages,
        "interview_transcript": current_state.get("interview_transcript", []) + new_transcript
    }

    # Run the graph
    result = graph.invoke(updated_state)

    # Update session
    interview_sessions[request.session_id]["state"] = result

    # Get the last assistant message
    assistant_messages = [msg for msg in result.get("messages", []) if msg.type == "ai"]
    response_text = assistant_messages[-1].content if assistant_messages else "Processed."

    return InterviewResponse(
        session_id=request.session_id,
        response=response_text,
        suggested_questions=result.get("suggested_questions", []),
        coaching_feedback=result.get("coaching_feedback", []),
        structured_notes=result.get("structured_notes"),
        strengths=result.get("strengths", []),
        areas_of_improvement=result.get("areas_of_improvement", [])
    )


@router.get("/session/{session_id}", response_model=InterviewResponse)
async def get_session_state(session_id: str):
    """Get the current state of an interview session."""
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")

    state = interview_sessions[session_id]["state"]

    return InterviewResponse(
        session_id=session_id,
        response="Session state retrieved",
        suggested_questions=state.get("suggested_questions", []),
        coaching_feedback=state.get("coaching_feedback", []),
        structured_notes=state.get("structured_notes"),
        strengths=state.get("strengths", []),
        areas_of_improvement=state.get("areas_of_improvement", [])
    )


@router.post("/suggestions/{session_id}")
async def get_suggestions(session_id: str, request: Optional[InterviewMessageRequest] = None):
    """Get real-time AI suggestions based on current transcript."""
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")

    session = interview_sessions[session_id]
    current_state = session["state"]

    # Update transcript if provided
    if request and request.transcript_entry:
        current_state = {
            **current_state,
            "interview_transcript": current_state.get("interview_transcript", []) + [request.transcript_entry]
        }

    # Import the expert and mentor agents
    from backend.interview.agents import interview_expert_agent, interview_mentor_agent

    # Call expert agent for questions
    expert_result = interview_expert_agent(current_state)

    # Call mentor agent for coaching
    mentor_result = interview_mentor_agent(current_state)

    # Update session state with new transcript and suggestions
    updated_state = {
        **current_state,
        "suggested_questions": expert_result.get("suggested_questions", []),
        "coaching_feedback": mentor_result.get("coaching_feedback", [])
    }
    interview_sessions[session_id]["state"] = updated_state

    return InterviewResponse(
        session_id=session_id,
        response="Suggestions updated",
        suggested_questions=expert_result.get("suggested_questions", []),
        coaching_feedback=mentor_result.get("coaching_feedback", [])
    )


@router.post("/brainstorm/{session_id}")
async def brainstorm_chat(session_id: str, request: InterviewMessageRequest):
    """Chat with Interview Shepherd during brainstorm phase."""
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")

    session = interview_sessions[session_id]
    current_state = session["state"]

    # Import the shepherd agent function
    from backend.interview.agents import interview_shepherd_agent

    # Add user message to brainstorm history
    user_msg = {"role": "user", "content": request.message}
    brainstorm_messages = current_state.get("brainstorm_messages", []) + [user_msg]

    # Update state with user message
    updated_state = {**current_state, "brainstorm_messages": brainstorm_messages}

    # Call shepherd agent
    result = interview_shepherd_agent(updated_state, request.message)

    # Add shepherd response to history
    shepherd_msg = {"role": "assistant", "content": result["response"]}
    brainstorm_messages.append(shepherd_msg)

    # Update session state
    final_state = {**updated_state, "brainstorm_messages": brainstorm_messages}
    interview_sessions[session_id]["state"] = final_state

    return InterviewResponse(
        session_id=session_id,
        response=result["response"]
    )


@router.post("/feedback/{session_id}")
async def generate_feedback(session_id: str, request: FeedbackRequest):
    """Generate final interview feedback scorecard."""
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")

    session = interview_sessions[session_id]
    current_state = session["state"]

    # Update state with hire decision and reason
    updated_state = {
        **current_state,
        "hire_decision": request.hire_decision,
        "decision_reason": request.decision_reason
    }

    # Import the feedback agent function directly
    from backend.interview.agents import interview_feedback_agent

    # Call feedback agent with updated state
    result = interview_feedback_agent(updated_state)

    # Update session with final state
    final_state = {**updated_state, **result}
    interview_sessions[session_id]["state"] = final_state

    return InterviewResponse(
        session_id=session_id,
        response=result.get("final_feedback") or "Interview feedback has been generated based on the conversation.",
        strengths=result.get("strengths", []),
        areas_of_improvement=result.get("areas_of_improvement", [])
    )


@router.delete("/session/{session_id}")
async def end_interview(session_id: str):
    """End an interview session and clean up."""
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")

    del interview_sessions[session_id]

    return {"message": "Interview session ended successfully"}
