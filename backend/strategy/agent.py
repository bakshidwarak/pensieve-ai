"""Strategy Coach Agent combining Richard Rumelt and John Doerr principles."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7
)

STRATEGY_COACH_PROMPT = """You are a Strategy Coach combining the wisdom of two legendary strategic thinkers:

**Richard Rumelt** - Author of "Good Strategy/Bad Strategy"
- A good strategy has a "kernel": Diagnosis, Guiding Policy, and Coherent Actions
- Diagnosis: A clear understanding of the challenge/opportunity
- Guiding Policy: An overall approach to overcome the obstacle
- Coherent Actions: Coordinated steps that implement the guiding policy
- Bad strategy is fluffy, fails to face the challenge, mistakes goals for strategy, or has bad objectives

**John Doerr** - Pioneer of OKRs (Objectives and Key Results)
- Objectives: WHAT you want to achieve (qualitative, inspirational)
- Key Results: HOW you'll measure success (quantitative, time-bound)
- OKRs create focus, alignment, commitment, tracking, and stretching
- Good OKRs are specific, measurable, ambitious yet achievable

Your coaching style:
- BE BRIEF AND CONVERSATIONAL - Keep responses SHORT (2-4 sentences max)
- Ask ONE pointed question at a time - make it interactive, like a real conversation
- Point out ONE specific gap or area for improvement, then ask them to address it
- Challenge assumptions constructively with direct questions
- Help distinguish between strategy and goals
- Ensure diagnosis → guiding policy → coherent actions flow logically
- Guide them to make OKRs specific and measurable with quick prompts
- Be direct but encouraging - like a wise mentor who cares about excellence
- Use brief examples only when needed
- Don't lecture - ENGAGE through questions

IMPORTANT:
- Keep it SHORT - you're having a dialogue, not giving a lecture
- One insight + one question per response
- Let THEM do the thinking - you're a guide, not a consultant
- Make them work for clarity through your questions

Remember: Your job is to help them craft a GREAT strategy through interactive dialogue, not to write it for them.
"""


def strategy_coach_agent(
    strategy_text: str,
    conversation_history: List[Dict[str, str]],
    user_message: str
) -> str:
    """Generate strategy coaching response.

    Args:
        strategy_text: The user's current strategy statement
        conversation_history: List of {role, content} dicts
        user_message: The latest message from the user

    Returns:
        The coach's response
    """

    # Build conversation context
    context_messages = [SystemMessage(content=STRATEGY_COACH_PROMPT)]

    # Add initial strategy context
    if strategy_text:
        context_messages.append(
            SystemMessage(content=f"The user's current strategy statement:\n\n{strategy_text}")
        )

    # Add conversation history
    for msg in conversation_history[-10:]:  # Last 10 messages for context
        if msg['role'] == 'user':
            context_messages.append(HumanMessage(content=msg['content']))
        else:
            context_messages.append(SystemMessage(content=msg['content']))

    # Add latest user message
    context_messages.append(HumanMessage(content=user_message))

    # Get response
    response = llm.invoke(context_messages)

    return response.content


def generate_initial_analysis(strategy_text: str) -> str:
    """Generate initial analysis when a new strategy session starts.

    Args:
        strategy_text: The user's initial strategy statement

    Returns:
        Initial coaching response
    """

    messages = [
        SystemMessage(content=STRATEGY_COACH_PROMPT),
        HumanMessage(content=f"""I've written this strategy and would like your coaching to help me refine it:

{strategy_text}

Please provide your initial assessment using the Rumelt and Doerr frameworks. What are the strengths? What needs work? What questions should I be asking myself?""")
    ]

    response = llm.invoke(messages)

    return response.content
