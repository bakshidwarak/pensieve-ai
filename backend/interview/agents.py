"""Interview Wizard Agent System.

This module contains the Interview Genie supervisor and all specialist agents:
- Note Taker: Scribes the interview
- Interview Expert: Suggests questions based on rubric
- Interview Mentor: Coaches the interviewer in real-time
- Interview Feedback: Helps create structured feedback
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import Literal
import os
from dotenv import load_dotenv

from backend.interview.state import InterviewState

# Load environment variables
load_dotenv()

# Initialize the LLM - use GPT-4o (latest OpenAI model)
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7
)


# ============================================================================
# AGENT NODES
# ============================================================================

def note_taker_agent(state: InterviewState) -> InterviewState:
    """Note Taker Agent: Scribes the interview and maintains structured notes.

    Responsibilities:
    - Capture key points from the conversation
    - Maintain structured, organized notes
    - Extract important quotes and observations
    """
    system_prompt = """You are a professional Note Taker for interviews.

Your role is to:
1. Capture key points and important quotes from the interview
2. Organize information in a structured format
3. Note behavioral observations and responses
4. Keep track of questions asked and answers given

Keep notes concise, organized, and professional.
Focus on facts and observations, not interpretations.
"""

    # Get the latest messages
    recent_messages = state["messages"][-5:] if state["messages"] else []

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Please update the interview notes based on the recent conversation.

Current structured notes:
{state.get('structured_notes', 'No notes yet.')}

Recent conversation:
{[msg.content for msg in recent_messages]}

Provide updated structured notes.""")
    ]

    response = llm.invoke(messages)

    return {
        "structured_notes": response.content,
        "next_agent": "interview_expert"
    }


def interview_expert_agent(state: InterviewState) -> InterviewState:
    """Interview Expert Agent: Suggests next questions based on rubric and progress.

    Responsibilities:
    - Analyze the interview rubric
    - Track which areas have been covered
    - Suggest relevant follow-up questions
    - Keep the interview on track
    """
    system_prompt = """You are the Interview Buddy - a helpful sidekick whispering suggestions in the interviewer's ear during a LIVE conversation.

CRITICAL MINDSET: You're listening to a REAL conversation happening RIGHT NOW. React to what's ACTUALLY being discussed.

Your job:
1. Listen to what the candidate JUST said in the last 1-2 exchanges
2. Think: "What would I naturally ask next if I were having this conversation?"
3. Suggest 1-2 conversational follow-ups that feel organic to THIS moment

Rules for being a good conversation buddy:
✅ DO:
- React to specific things they JUST mentioned ("They just said X - ask about Y")
- Suggest natural conversational probes ("Oh interesting - ask them to elaborate on...")
- Help dig into vague answers with specific follow-ups
- Notice when they've given a complete answer and suggest moving on
- Reference actual details from what they said

❌ DON'T:
- Suggest generic questions that could be asked at any time
- Act like a question bank with random rubric items
- Ignore what was just discussed
- Suggest questions already answered
- Be formal or robotic

Think of it like this: You're sitting next to the interviewer, listening to the same conversation, and you lean over to whisper: "Hey, they just mentioned managing conflict - you should ask them to walk through a specific example of how they handled that"

Your suggestions should feel like you're actively engaged in THIS conversation, not reading from a script."""

    # Get more context for dynamic suggestions
    recent_transcript = state.get('interview_transcript', [])[-5:] if state.get('interview_transcript') else []
    all_transcript = state.get('interview_transcript', [])

    # Analyze what's been covered
    transcript_text = '\n'.join(all_transcript) if all_transcript else 'Interview just started'

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""You're listening to a live interview. Here's what just happened:

WHAT WAS JUST SAID (last 2-3 exchanges):
{chr(10).join(recent_transcript[-3:]) if len(recent_transcript) >= 3 else chr(10).join(recent_transcript) if recent_transcript else 'Interview just started - no conversation yet.'}

CONTEXT - Full conversation so far:
{transcript_text if len(all_transcript) > 3 else 'Just beginning...'}

Rubric areas to eventually cover: {state.get('interview_rubric', 'No specific rubric')}

Now think: Based on what the candidate JUST said, what would you naturally ask next?

Your response should be 1-2 questions that:
- Build directly on what they JUST mentioned
- Dig deeper into vague or interesting points
- Feel like a natural continuation of THIS conversation
- Reference specific details from their answer

If the conversation just started, suggest a good opening question.
If they just gave a shallow answer, probe for specifics.
If they mentioned something interesting, follow that thread.
If a topic is exhausted, smoothly transition to a new rubric area.

Return ONLY the questions, one per line.""")
    ]

    response = llm.invoke(messages)

    # Extract questions from response
    questions = response.content.split('\n')
    questions = [q.strip() for q in questions if q.strip() and ('?' in q or q.startswith('-'))]

    # Clean up question formatting - limit to 2 questions max for conversational feel
    cleaned_questions = []
    for q in questions[:2]:
        # Remove leading "- " or bullet points
        q = q.lstrip('- •*').strip()
        if q:
            cleaned_questions.append(q)

    return {
        "suggested_questions": cleaned_questions,
        "next_agent": "interview_mentor"
    }


def interview_mentor_agent(state: InterviewState) -> InterviewState:
    """Interview Mentor Agent: Coaches the interviewer on technique.

    Responsibilities:
    - Observe interviewing technique
    - Provide real-time coaching tips
    - Suggest improvements in questioning style
    - Help maintain professionalism and fairness
    """
    system_prompt = """You are an Interview Mentor coaching someone on interview technique.

Your role is to:
1. Observe the interviewer's questioning style
2. Provide constructive coaching on technique
3. Suggest ways to probe deeper or redirect
4. Ensure fair, unbiased interviewing practices
5. Help the interviewer avoid common pitfalls

Be supportive and constructive.
Focus on actionable tips.
Keep feedback brief and specific.
"""

    recent_messages = state["messages"][-3:] if state["messages"] else []

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Provide coaching feedback on the interviewer's recent approach.

Recent conversation:
{[msg.content for msg in recent_messages]}

Suggested questions they could have used:
{state.get('suggested_questions', [])}

Provide 1-2 brief coaching tips.""")
    ]

    response = llm.invoke(messages)

    return {
        "coaching_feedback": [response.content],
        "next_agent": "supervisor"
    }


def interview_shepherd_agent(state: InterviewState, user_message: str) -> dict:
    """Interview Shepherd Agent: Guides brainstorming and decision-making.

    Responsibilities:
    - Act as a thoughtful guide through the decision process
    - Ask probing questions about the candidate
    - Help identify strengths and concerns
    - Challenge assumptions constructively
    - Guide toward a well-reasoned hire/no-hire decision
    """
    system_prompt = """You are an Interview Shepherd - a wise, experienced hiring manager helping another interviewer think through their candidate assessment.

Your role is to:
1. Guide the interviewer through reflective brainstorming about the candidate
2. Ask probing questions to uncover insights they might have missed
3. Help them identify both strengths AND concerns objectively
4. Challenge their thinking constructively when needed
5. Keep the discussion grounded in the rubric and evidence from the interview
6. Eventually help them arrive at a confident hire/no-hire decision

Your style:
- Be conversational and supportive, like a trusted mentor
- Ask thoughtful follow-up questions
- Point out patterns or gaps in their thinking
- Use examples from the transcript to ground the discussion
- Don't rush to judgment - let them explore their thoughts
- When they're ready, help them articulate a clear decision with reasoning

Remember: You're guiding them to THEIR decision, not making it for them.
"""

    # Get brainstorm conversation history from state
    brainstorm_history = state.get('brainstorm_messages', [])

    # Build conversation context
    conversation_context = ""
    for msg in brainstorm_history[-10:]:  # Last 10 messages
        role = "Interviewer" if msg.get('role') == 'user' else "Shepherd"
        conversation_context += f"{role}: {msg.get('content', '')}\n"

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Continue the brainstorming conversation with the interviewer.

Candidate: {state.get('candidate_name', 'Unknown')}
Position: {state.get('position', 'Unknown')}

Interview Rubric:
{state.get('interview_rubric', 'No rubric provided.')}

Full Interview Transcript:
{chr(10).join(state.get('interview_transcript', []))}

Previous brainstorm conversation:
{conversation_context if conversation_context else '(Starting the brainstorm)'}

Interviewer's latest message:
{user_message}

Respond as the Interview Shepherd. Be conversational, ask probing questions, and help them think deeply about the candidate. Use specific examples from the transcript when relevant.""")
    ]

    response = llm.invoke(messages)

    return {
        "response": response.content
    }


def interview_feedback_agent(state: InterviewState) -> InterviewState:
    """Interview Feedback Agent: Generates structured scorecard feedback.

    Responsibilities:
    - Analyze all interview data comprehensively
    - Generate scorecard organized by rubric aspects
    - Provide specific examples from transcript for each aspect
    - Incorporate insights from brainstorm conversation
    - Create professional markdown-formatted output
    """
    system_prompt = """You are an Interview Feedback Specialist creating a comprehensive interview scorecard.

Your task is to generate a PROFESSIONAL, STRUCTURED interview scorecard in Markdown format.

Structure your scorecard as follows:

# Interview Scorecard

## Candidate Information
- Name, Position, Date

## Overall Recommendation
[HIRE / NO HIRE] - with brief justification

## Rubric Assessment

For EACH aspect mentioned in the rubric, create a section with:
### [Aspect Name] - Rating: [Strong/Adequate/Needs Development/Not Assessed]

**Assessment:**
[Your evaluation of this aspect]

**Evidence from Interview:**
- Quote or specific example from transcript that supports your assessment
- Another relevant example if available

**Key Observations:**
- Bullet points with specific observations

## Strengths
- List 3-5 key strengths with specific examples

## Areas for Development
- List 2-4 areas with specific examples

## Additional Notes
- Any other relevant observations from the brainstorm discussion
- Cultural fit notes
- Other considerations

---

IMPORTANT:
- Use the ACTUAL rubric aspects as section headers
- Quote SPECIFIC examples from the transcript
- Reference insights from the brainstorm conversation
- Keep it professional and evidence-based
- Use proper markdown formatting (## for headers, - for bullets, ** for bold)
"""

    # Get brainstorm conversation
    brainstorm_history = state.get('brainstorm_messages', [])
    brainstorm_text = ""
    for msg in brainstorm_history:
        role = "Interviewer" if msg.get('role') == 'user' else "Shepherd"
        brainstorm_text += f"{role}: {msg.get('content', '')}\n\n"

    # Get hire decision and reason
    hire_decision = state.get('hire_decision', 'Not decided')

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Generate a comprehensive interview scorecard for this candidate.

CANDIDATE: {state.get('candidate_name', 'Unknown')}
POSITION: {state.get('position', 'Unknown')}

INTERVIEW RUBRIC (use these aspects as scorecard sections):
{state.get('interview_rubric', 'No rubric provided.')}

FULL INTERVIEW TRANSCRIPT (use for specific examples):
{chr(10).join(state.get('interview_transcript', []))}

BRAINSTORM CONVERSATION (incorporate insights):
{brainstorm_text if brainstorm_text else 'No brainstorm discussion recorded.'}

INTERVIEWER'S DECISION: {hire_decision}

Generate the complete scorecard in Markdown format following the structure above. Make sure to:
1. Create a section for EACH aspect in the rubric
2. Include SPECIFIC quotes or examples from the transcript
3. Incorporate insights from the brainstorm conversation
4. Provide the interviewer's decision with supporting reasoning
5. Use proper Markdown formatting""")
    ]

    response = llm.invoke(messages)

    # Parse response for strengths and areas (for legacy compatibility)
    content = response.content
    strengths_section = []
    areas_section = []

    # Extract strengths
    if "## Strengths" in content:
        lines = content.split("## Strengths")[1].split("##")[0].split('\n')
        strengths_section = [line.strip() for line in lines if line.strip() and line.strip().startswith(('-', '•', '*'))]

    # Extract areas for development
    if "## Areas for Development" in content or "## Areas of Concern" in content:
        marker = "## Areas for Development" if "## Areas for Development" in content else "## Areas of Concern"
        lines = content.split(marker)[1].split("##")[0].split('\n')
        areas_section = [line.strip() for line in lines if line.strip() and line.strip().startswith(('-', '•', '*'))]

    return {
        "strengths": strengths_section,
        "areas_of_improvement": areas_section,
        "final_feedback": response.content,
        "next_agent": "END"
    }


# ============================================================================
# SUPERVISOR NODE
# ============================================================================

def supervisor_agent(state: InterviewState) -> InterviewState:
    """Interview Genie Supervisor: Routes to appropriate specialist agents.

    Responsibilities:
    - Understand user intent
    - Route to appropriate specialist agent
    - Coordinate the overall interview process
    - Decide when to end or continue
    """
    system_prompt = """You are the Interview Genie, a supervisor coordinating an interview assistance system.

You have 4 specialist agents at your disposal:
1. note_taker - Maintains structured notes from the interview
2. interview_expert - Suggests questions based on the rubric
3. interview_mentor - Coaches the interviewer on technique
4. interview_feedback - Creates final interview feedback

Your role is to:
- Understand what the user needs right now
- Route to the appropriate agent
- Coordinate the workflow

When to use each agent:
- note_taker: After user shares interview dialogue or needs notes updated
- interview_expert: When user needs question suggestions or is stuck
- interview_mentor: When user wants coaching on their interview technique
- interview_feedback: When interview is complete and feedback is needed
- END: When user explicitly ends the session or feedback is delivered

Respond with ONLY the agent name: note_taker, interview_expert, interview_mentor, interview_feedback, or END
"""

    recent_messages = state["messages"][-2:] if state["messages"] else []

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Based on the user's recent message, which agent should handle this?

Recent messages:
{[msg.content for msg in recent_messages]}

Current state:
- Has rubric: {bool(state.get('interview_rubric'))}
- Has notes: {bool(state.get('structured_notes'))}
- Has transcript: {len(state.get('interview_transcript', []))} entries

Respond with one agent name: note_taker, interview_expert, interview_mentor, interview_feedback, or END
""")
    ]

    response = llm.invoke(messages)
    next_agent = response.content.strip().lower()

    # Validate agent name
    valid_agents = ["note_taker", "interview_expert", "interview_mentor", "interview_feedback", "END"]
    if next_agent not in valid_agents:
        next_agent = "note_taker"  # Default

    return {"next_agent": next_agent}


# ============================================================================
# ROUTING FUNCTION
# ============================================================================

def route_to_agent(state: InterviewState) -> Literal["note_taker", "interview_expert", "interview_mentor", "interview_feedback", END]:
    """Route to the next agent based on state."""
    next_agent = state.get("next_agent", "supervisor")

    if next_agent == "END":
        return END

    return next_agent


# ============================================================================
# BUILD THE GRAPH
# ============================================================================

def create_interview_graph():
    """Create the Interview Wizard agent graph."""
    workflow = StateGraph(InterviewState)

    # Add nodes
    workflow.add_node("interview_expert", interview_expert_agent)
    workflow.add_node("interview_feedback", interview_feedback_agent)

    # Simple flow: start -> interview_expert -> end
    # The feedback agent is called separately via the feedback endpoint
    workflow.set_entry_point("interview_expert")
    workflow.add_edge("interview_expert", END)
    workflow.add_edge("interview_feedback", END)

    return workflow.compile()
