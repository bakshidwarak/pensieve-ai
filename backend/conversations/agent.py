"""Difficult Conversations Coach Agent based on Crucial Conversations principles."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.8  # Higher temperature for more varied roleplay responses
)

def build_coach_prompt(situation: str, message_to_deliver: str, difficulty_level: int, gender: str) -> str:
    """Build the system prompt for the conversation coach based on difficulty level."""

    difficulty_instructions = {
        1: "Be very understanding and cooperative. Readily acknowledge points and work toward resolution. Ask clarifying questions.",
        2: "Be mostly receptive but occasionally ask for clarification. Show genuine interest.",
        3: "Be open to dialogue but express some initial concerns. Push back gently on some points.",
        4: "Show some resistance but be willing to listen. Question their reasoning occasionally.",
        5: "Be moderately defensive. Question motives occasionally but stay engaged. Don't let things slide easily.",
        6: "Be noticeably defensive. Require more convincing and evidence. Challenge their statements.",
        7: "Be quite resistant. Use deflection and get emotional at times. Interrupt when triggered.",
        8: "Be very difficult. Use personal attacks, deflection, and strong emotional reactions. Interrupt frequently.",
        9: "Be extremely challenging. Employ all difficult conversation tactics: blame-shifting, gaslighting, threats. Be combative.",
        10: "Be maximally difficult. Hostile, aggressive, use every manipulative tactic possible. Constant interruptions and attacks."
    }

    difficulty_instruction = difficulty_instructions.get(difficulty_level, difficulty_instructions[5])

    return f"""You are roleplaying as the other party in a crucial conversation practice session.

**SITUATION CONTEXT:**
{situation}

**MESSAGE THEY WANT TO DELIVER:**
{message_to_deliver}

**YOUR ROLEPLAY INSTRUCTIONS:**
- You are a {gender} person in this situation
- Difficulty level: {difficulty_level}/10 - {difficulty_instruction}
- Stay IN CHARACTER throughout the conversation
- Respond naturally as this person would, with realistic emotions and reactions
- Keep responses SHORT and CONVERSATIONAL (1-3 sentences, like real dialogue)
- INTERRUPT if they say something that triggers you - don't wait for them to finish
- React in real-time to what they're saying - agree, disagree, question, push back
- Use natural conversational fillers ("Well...", "But...", "I mean...")
- DO NOT break character or acknowledge you're an AI
- DO NOT coach them - you're the other party, not a coach
- BE REACTIVE: If they ask a question, answer it. If they make a statement, respond to it

**CRUCIAL CONVERSATIONS CHALLENGES TO EMPLOY (based on difficulty):**
- At lower difficulty: Be open, acknowledge feelings, seek mutual purpose, ask clarifying questions
- At medium difficulty: Show defensiveness, interrupt occasionally, question their motives
- At higher difficulty: Employ poor listening, accusations, blame-shifting, emotion escalation, talk over them
- Remember: Even difficult people have reasons for their behavior - stay human

**YOUR GOAL:**
Have a REAL conversation. React authentically to what the user says in the moment. If they use good Crucial Conversations techniques (establishing safety, finding mutual purpose, stating facts not stories), you should gradually become more cooperative. If they attack or get defensive themselves, escalate accordingly.

This is a dialogue, not a monologue. Keep responses brief so there's back-and-forth.

**IMPORTANT - KEEP THE DIALOGUE GOING:**
- After making your point, often ask a question or make a statement that requires their response
- Don't just agree or acknowledge - push the conversation forward
- Challenge them, ask "why?", demand explanations, or express your emotions
- At higher difficulties, be MORE talkative and demanding - don't let them off easy
- Examples: "But what about X?", "Why should I believe that?", "That doesn't make sense because...", "What are you really saying?"

Stay in character. Respond as this person would in this real situation."""


FEEDBACK_COACH_PROMPT = """You are a communication coach specializing in Crucial Conversations methodology by Kerry Patterson, Joseph Grenny, Ron McMillan, and Al Switzler.

**CRUCIAL CONVERSATIONS PRINCIPLES:**

1. **Start with Heart** - Focus on what you really want
2. **Learn to Look** - Notice when safety is at risk
3. **Make it Safe** - Use Mutual Purpose and Mutual Respect
4. **Master My Stories** - Separate facts from stories
5. **STATE My Path** - Share your facts, Tell your story, Ask for others' paths, Talk tentatively, Encourage testing
6. **Explore Others' Paths** - Ask, Mirror, Paraphrase, Prime (AMPP)
7. **Move to Action** - Decide how to decide and follow up

**YOUR FEEDBACK STYLE:**
- Be brief and actionable (4-6 key points)
- Highlight 2-3 things they did WELL
- Identify 2-3 specific areas for improvement
- Provide ONE concrete example of what they could have said differently
- Reference specific Crucial Conversations techniques by name
- Be encouraging but honest

Analyze the conversation transcript and provide coaching feedback."""


def generate_initial_response(
    situation: str,
    message_to_deliver: str,
    difficulty_level: int,
    gender: str
) -> str:
    """Generate the initial response from the other party when conversation starts.

    Args:
        situation: The situation context
        message_to_deliver: What the user wants to communicate
        difficulty_level: 1-10 scale of how difficult the other party should be
        gender: 'male' or 'female'

    Returns:
        Initial response text from the other party
    """

    system_prompt = build_coach_prompt(situation, message_to_deliver, difficulty_level, gender)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="""The user is about to start the conversation with you.

Provide a brief initial greeting or opening (1-2 sentences) that sets the tone based on your difficulty level.
For example:
- Low difficulty: Acknowledge them warmly, show openness, maybe ask what they want to talk about
- Medium difficulty: Be neutral or slightly guarded, acknowledge them but be brief
- High difficulty: Show impatience, defensiveness, or hostility right away. Make them work for it.

IMPORTANT: End with something that invites or challenges them to speak. Don't just say hi - create an opening for dialogue.
Examples: "What's this about?", "I'm listening...", "Can we make this quick?", "What do you want?"

Remember: Stay in character as the person in this situation.""")
    ]

    response = llm.invoke(messages)
    return response.content


def conversation_coach_agent(
    situation: str,
    message_to_deliver: str,
    difficulty_level: int,
    gender: str,
    conversation_history: List[Dict[str, str]],
    user_message: str
) -> str:
    """Generate the other party's response during the conversation.

    Args:
        situation: The situation context
        message_to_deliver: What the user wants to communicate
        difficulty_level: 1-10 scale
        gender: 'male' or 'female'
        conversation_history: List of {role, content} dicts
        user_message: Latest message from user

    Returns:
        The other party's response
    """

    system_prompt = build_coach_prompt(situation, message_to_deliver, difficulty_level, gender)

    # Build conversation context
    context_messages = [SystemMessage(content=system_prompt)]

    # Add conversation history
    for msg in conversation_history[-8:]:  # Last 8 messages for context
        if msg['role'] == 'user':
            context_messages.append(HumanMessage(content=msg['content']))
        else:
            context_messages.append(SystemMessage(content=f"You said: {msg['content']}"))

    # Add latest user message
    context_messages.append(HumanMessage(content=user_message))

    response = llm.invoke(context_messages)
    return response.content


def generate_feedback(
    situation: str,
    message_to_deliver: str,
    difficulty_level: int,
    conversation_transcript: str
) -> str:
    """Generate coaching feedback on the conversation.

    Args:
        situation: The original situation
        message_to_deliver: What they wanted to communicate
        difficulty_level: The difficulty level they practiced at
        conversation_transcript: Full transcript of the conversation

    Returns:
        Coaching feedback
    """

    messages = [
        SystemMessage(content=FEEDBACK_COACH_PROMPT),
        HumanMessage(content=f"""Please analyze this practice conversation:

**SITUATION:**
{situation}

**MESSAGE TO DELIVER:**
{message_to_deliver}

**DIFFICULTY LEVEL:** {difficulty_level}/10

**CONVERSATION TRANSCRIPT:**
{conversation_transcript}

---

Provide coaching feedback on their performance. What did they do well? What could they improve? What specific Crucial Conversations techniques should they focus on?""")
    ]

    response = llm.invoke(messages)
    return response.content
