"""State management for Interview Wizard agents."""

from typing import TypedDict, List, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator


class InterviewState(TypedDict):
    """State for the Interview Wizard multi-agent system.

    This state is shared across all agents in the interview system:
    - Interview Genie (supervisor)
    - Note Taker
    - Interview Expert
    - Interview Mentor
    - Interview Feedback
    """

    # Conversation messages
    messages: Annotated[List[BaseMessage], operator.add]

    # Interview session data
    interview_rubric: Optional[str]  # The rubric/criteria for the interview
    candidate_name: Optional[str]
    position: Optional[str]

    # Interview transcript and notes
    interview_transcript: Annotated[List[str], operator.add]  # Raw transcript entries
    structured_notes: Optional[str]  # Structured notes from Note Taker

    # Expert suggestions
    suggested_questions: Annotated[List[str], operator.add]  # Questions suggested by Interview Expert
    current_topic: Optional[str]  # Current topic being discussed

    # Mentor coaching
    coaching_feedback: Annotated[List[str], operator.add]  # Real-time coaching from Interview Mentor

    # Brainstorm conversation (for Interview Shepherd)
    brainstorm_messages: Annotated[List[dict], operator.add]  # Chat history with shepherd

    # Final feedback
    strengths: Annotated[List[str], operator.add]
    areas_of_improvement: Annotated[List[str], operator.add]
    hire_decision: Optional[str]  # "hire", "no_hire", or None (pending)
    final_feedback: Optional[str]

    # Agent routing
    next_agent: Optional[str]  # Which agent should act next
