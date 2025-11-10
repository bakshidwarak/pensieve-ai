# Pensieve.ai Agent Architecture Graph

## Overview
Pensieve.ai uses multiple specialized AI agent systems, each designed for specific leadership coaching tasks. This document visualizes the agent architectures and their interactions.

---

## 1. Simple Tool-Using Agent (LangGraph Platform)
**Location:** `app/graphs/simple_agent.py`

```
┌─────────────────────────────────────────────────────┐
│                  ENTRY POINT                        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │     AGENT      │
        │   (LLM Call)   │
        │  with Tools    │
        └───────┬────────┘
                │
                │ should_continue()
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
   ┌─────────┐      ┌────────┐
   │ ACTION  │      │  END   │
   │(ToolNode)│      └────────┘
   └────┬────┘
        │
        │ (loop back)
        ▼
   ┌─────────┐
   │  AGENT  │
   └─────────┘
```

**Flow:**
1. **AGENT** - Calls LLM with tool bindings
2. **Routing** - If LLM requests tool calls → ACTION, else → END
3. **ACTION** - Executes tools via ToolNode
4. **Loop** - Returns to AGENT with tool results

**Tools:** Configurable tool belt from `app/tools`

---

## 2. Agent with Helpfulness Loop (LangGraph Platform)
**Location:** `app/graphs/agent_with_helpfulness.py`

```
┌─────────────────────────────────────────────────────┐
│                  ENTRY POINT                        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │     AGENT      │
        │   (LLM Call)   │
        │  with Tools    │
        └───────┬────────┘
                │
                │ route_to_action_or_helpfulness()
                │
        ┌───────┴────────────┐
        │                    │
        ▼                    ▼
   ┌─────────┐      ┌──────────────┐
   │ ACTION  │      │ HELPFULNESS  │
   │(ToolNode)│      │   CHECK      │
   └────┬────┘      │(GPT-4.1-mini)│
        │           └──────┬───────┘
        │                  │
        │                  │ helpfulness_decision()
        │                  │
        │          ┌───────┴────────┐
        │          │                │
        │          ▼                ▼
        │    ┌─────────┐      ┌────────┐
        │    │CONTINUE │      │  END   │
        │    │(to AGENT)│      └────────┘
        │    └────┬────┘
        │         │
        └─────────┴──────► AGENT (loop)
```

**Flow:**
1. **AGENT** - Calls LLM with tool bindings
2. **Routing** - If tool calls → ACTION, else → HELPFULNESS
3. **ACTION** - Executes tools, loops back to AGENT
4. **HELPFULNESS** - Evaluates if response is helpful (Y/N)
5. **Decision** - If helpful (Y) → END, if not (N) → continue to AGENT
6. **Safety** - Max 10 message limit to prevent infinite loops

**Special Feature:** Quality control loop ensuring helpful responses

---

## 3. Interview Wizard Multi-Agent System
**Location:** `backend/interview/agents.py`

```
┌───────────────────────────────────────────────────────────┐
│                     USER REQUEST                          │
└──────────────────────┬────────────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  ENTRY POINT    │
              │ INTERVIEW_EXPERT│
              └────────┬────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │   INTERVIEW EXPERT      │
         │  (Question Suggester)   │
         │                         │
         │  • Analyzes transcript  │
         │  • Reacts to what was   │
         │    JUST said            │
         │  • Suggests 1-2 follow- │
         │    up questions         │
         │  • References rubric    │
         └────────┬────────────────┘
                  │
                  ▼
             ┌────────┐
             │  END   │
             └────────┘


┌───────────────────────────────────────────────────────────┐
│            ADDITIONAL SPECIALIST AGENTS                   │
│           (Called via separate endpoints)                 │
└───────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   NOTE TAKER     │    │ INTERVIEW MENTOR │    │INTERVIEW SHEPHERD│
│                  │    │                  │    │                  │
│ • Captures key   │    │ • Observes       │    │ • Guides         │
│   points         │    │   technique      │    │   brainstorming  │
│ • Maintains      │    │ • Provides       │    │ • Asks probing   │
│   structured     │    │   coaching tips  │    │   questions      │
│   notes          │    │ • Suggests       │    │ • Challenges     │
│ • Extracts       │    │   improvements   │    │   assumptions    │
│   quotes         │    │                  │    │ • Helps decide   │
└──────────────────┘    └──────────────────┘    │   hire/no-hire   │
                                                 └──────────────────┘

┌──────────────────────────────────────────┐
│      INTERVIEW FEEDBACK AGENT            │
│                                          │
│ • Generates scorecard                    │
│ • Organizes by rubric aspects            │
│ • Includes specific examples             │
│ • Incorporates brainstorm insights       │
│ • Creates markdown-formatted output      │
│                                          │
│ Input:                                   │
│  - Full transcript                       │
│  - Rubric aspects                        │
│  - Brainstorm conversation               │
│  - Hire decision                         │
│                                          │
│ Output: Comprehensive Markdown scorecard │
└──────────────────────────────────────────┘
```

**Agent Roles:**

1. **Interview Expert** (Main Flow)
   - Reacts to conversation in real-time
   - Suggests contextual follow-up questions
   - References rubric dynamically

2. **Note Taker** (On-demand)
   - Maintains structured interview notes
   - Captures key quotes and observations

3. **Interview Mentor** (On-demand)
   - Coaches on interview technique
   - Provides actionable feedback

4. **Interview Shepherd** (Brainstorm Phase)
   - Guides reflective thinking about candidate
   - Asks probing questions
   - Helps arrive at hire/no-hire decision

5. **Interview Feedback** (Final Phase)
   - Creates comprehensive scorecard
   - Organized by rubric aspects
   - Includes evidence from transcript

**Key Innovation:** Conversational, reactive question suggestions based on what candidate JUST said, not generic question banks.

---

## 4. Strategy Coach Agent
**Location:** `backend/strategy/agent.py`

```
┌──────────────────────────────────────────────────┐
│              USER'S STRATEGY TEXT                │
└─────────────────┬────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │ INITIAL REQUEST│
         └────────┬───────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │   STRATEGY COACH AGENT      │
    │   (GPT-4o, temp=0.7)        │
    │                             │
    │ Frameworks:                 │
    │ • Richard Rumelt            │
    │   - Diagnosis               │
    │   - Guiding Policy          │
    │   - Coherent Actions        │
    │                             │
    │ • John Doerr OKRs           │
    │   - Objectives (WHAT)       │
    │   - Key Results (HOW)       │
    │                             │
    │ Coaching Style:             │
    │ • Brief (2-4 sentences)     │
    │ • ONE question at a time    │
    │ • Interactive dialogue      │
    │ • Challenges assumptions    │
    └──────────┬──────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  CONVERSATIONAL LOOP │
    │                      │
    │  User ──► Coach      │
    │   ▲        │         │
    │   │        │         │
    │   └────────┘         │
    │                      │
    │ Coach asks ONE       │
    │ pointed question     │
    │ per turn             │
    └──────────────────────┘
```

**Flow:**
1. User submits strategy text
2. Coach provides initial analysis using Rumelt + Doerr frameworks
3. Interactive dialogue loop:
   - Coach identifies ONE gap
   - Asks ONE specific question
   - User responds
   - Coach follows up
4. Continues until strategy is refined

**Key Feature:** Short, conversational turns - like a real coaching session

---

## 5. Difficult Conversations Coach Agent
**Location:** `backend/conversations/agent.py`

```
┌────────────────────────────────────────────────────────────┐
│                    USER SETUP                              │
│  • Situation context                                       │
│  • Message to deliver                                      │
│  • Difficulty level (1-10)                                 │
│  • Other party gender                                      │
└─────────────────────┬──────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │  INITIAL RESPONSE AGENT    │
         │  (GPT-4o, temp=0.8)        │
         │                            │
         │  • Generates opening based │
         │    on difficulty level     │
         │  • Sets conversation tone  │
         │  • Invites dialogue        │
         └────────┬───────────────────┘
                  │
                  │ ┌──► TTS (OpenAI)
                  │ │    • Gender-aware voices
                  │ │    • onyx (male)
                  │ │    • nova (female)
                  ▼ ▼
         ┌────────────────┐
         │  USER HEARS    │
         │  AI GREETING   │
         └────────┬───────┘
                  │
                  ▼
      ┌───────────────────────────┐
      │  REAL-TIME DIALOGUE LOOP  │
      │                           │
      │  User speaks (2s chunks)  │
      │        │                  │
      │        ▼                  │
      │  ┌──────────────┐        │
      │  │ Transcription│        │
      │  │  (Whisper)   │        │
      │  └──────┬───────┘        │
      │         │                 │
      │         ▼                 │
      │  ┌────────────────────┐  │
      │  │ PAUSE DETECTION    │  │
      │  │                    │  │
      │  │ • Question? 500ms  │  │
      │  │ • Statement? 1-2s  │  │
      │  │ • Long? 2.5s       │  │
      │  └────────┬───────────┘  │
      │           │               │
      │           ▼               │
      │  ┌──────────────────┐    │
      │  │ ROLEPLAY AGENT   │    │
      │  │ (GPT-4o)         │    │
      │  │                  │    │
      │  │ Behavior by      │    │
      │  │ difficulty:      │    │
      │  │                  │    │
      │  │ Lvl 1-2: Very    │    │
      │  │  cooperative     │    │
      │  │                  │    │
      │  │ Lvl 3-4: Some    │    │
      │  │  pushback        │    │
      │  │                  │    │
      │  │ Lvl 5-6: Modera- │    │
      │  │  tely defensive  │    │
      │  │                  │    │
      │  │ Lvl 7-8: Quite   │    │
      │  │  resistant       │    │
      │  │                  │    │
      │  │ Lvl 9-10: Very   │    │
      │  │  hostile         │    │
      │  │                  │    │
      │  │ Response style:  │    │
      │  │ • 1-3 sentences  │    │
      │  │ • Ends with      │    │
      │  │   question       │    │
      │  │ • Challenges     │    │
      │  │   user           │    │
      │  │ • Reacts to      │    │
      │  │   specifics      │    │
      │  └────────┬─────────┘    │
      │           │               │
      │           ▼               │
      │      TTS ──► User hears   │
      │           │               │
      │           ▼               │
      │    User responds...       │
      │           │               │
      │           └───────────────┘
      │                           │
      └───────────────────────────┘
                  │
                  │ (When user ends)
                  ▼
         ┌────────────────────┐
         │  FEEDBACK AGENT    │
         │  (GPT-4o)          │
         │                    │
         │  Analyzes using:   │
         │  • Crucial         │
         │    Conversations   │
         │    principles      │
         │                    │
         │  Feedback covers:  │
         │  • What they did   │
         │    well (2-3)      │
         │  • Areas to        │
         │    improve (2-3)   │
         │  • Specific        │
         │    techniques      │
         │  • Example of      │
         │    what to say     │
         │    differently     │
         └────────────────────┘
```

**Crucial Conversations Principles Applied:**
1. Start with Heart
2. Learn to Look
3. Make it Safe
4. Master My Stories
5. STATE My Path
6. Explore Others' Paths
7. Move to Action

**Key Innovation:**
- Natural dialogue with smart pause detection
- AI responds contextually during conversation (not just at the end)
- Difficulty scaling from cooperative to hostile
- Real-time audio interaction with TTS

---

## Agent Comparison Matrix

| Agent System | Type | Framework | Tools | Conversation Style |
|-------------|------|-----------|-------|-------------------|
| Simple Agent | Tool-using | LangGraph | Custom tool belt | Reactive |
| Helpfulness Agent | Tool-using + QA | LangGraph | Custom + evaluation | Quality-checked |
| Interview Wizard | Multi-agent | LangGraph | Specialized agents | Collaborative |
| Strategy Coach | Single-agent | LangChain | None | Interactive coaching |
| Conversations Coach | Roleplay + Feedback | LangChain | TTS, STT | Immersive dialogue |

---

## Technology Stack

### LLMs Used:
- **GPT-4o** - Main models for all agents (except helpfulness check)
- **GPT-4.1-mini** - Helpfulness evaluation only

### Frameworks:
- **LangGraph** - Multi-agent orchestration (app/graphs, interview)
- **LangChain** - Single-agent flows (strategy, conversations)

### External Services:
- **OpenAI Whisper** - Speech-to-text (conversations)
- **OpenAI TTS** - Text-to-speech (conversations)

### State Management:
- **AgentState** - Base state for simple agents
- **InterviewState** - Complex state with transcript, notes, coaching
- **In-memory sessions** - Conversations feature
- **Conversational history** - Strategy coaching

---

## Data Flow Patterns

### Pattern 1: Linear Flow (Strategy Coach)
```
User Input → Agent → Response → User Input → Agent → ...
```

### Pattern 2: Conditional Loop (Simple Agent)
```
Agent → [Has tool calls?] → Yes → Tools → Agent
                          → No → END
```

### Pattern 3: Quality Loop (Helpfulness Agent)
```
Agent → [Has tool calls?] → Yes → Tools → Agent
                          → No → Helpfulness → [Helpful?] → Yes → END
                                                           → No → Agent
```

### Pattern 4: Specialist Routing (Interview Wizard)
```
Entry → Expert → END
      ↓
   [Separate endpoints]
      ↓
   Note Taker / Mentor / Shepherd / Feedback
```

### Pattern 5: Real-time Dialogue (Conversations)
```
User Audio → Transcribe → Pause Detect → Agent → TTS → User Hears
                                          ↑              │
                                          └──────────────┘
```

---

## Future Extension Points

1. **Tool Integration**
   - Add more specialized tools to simple agent
   - Calendar integration for interview scheduling
   - CRM integration for candidate tracking

2. **Multi-modal Inputs**
   - Video analysis for interview body language
   - Document analysis for strategy review
   - Screen sharing for real-time coaching

3. **Persistent Memory**
   - Long-term candidate profiles
   - Historical strategy versions
   - Conversation practice progression tracking

4. **Collaborative Features**
   - Multi-interviewer coordination
   - Peer strategy review
   - Team conversation practice

---

## Architecture Principles

1. **Separation of Concerns**
   - Each agent has a specific, well-defined role
   - No overlap in responsibilities

2. **Conversational Design**
   - Short turns, not lectures
   - Interactive, not prescriptive
   - Human remains in control

3. **Framework Selection**
   - LangGraph for complex multi-agent coordination
   - LangChain for simpler conversational flows
   - Right tool for the job

4. **State Management**
   - Explicit state definitions
   - Refs for closure-safe callbacks
   - Session management for multi-turn

5. **Quality Control**
   - Helpfulness loops
   - Framework-based coaching (Rumelt, Doerr, Crucial Conversations)
   - Evidence-based feedback

---

*Generated: 2025*
*Project: Pensieve.ai - IDE for Leaders*
