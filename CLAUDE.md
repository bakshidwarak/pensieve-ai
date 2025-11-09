# Claude Code Instructions for Pensieve.ai

## Project Overview

**Pensieve.ai** is an "IDE for Leaders" - an intelligent development environment that helps leaders navigate complexity, make informed decisions, and drive strategic outcomes using AI-powered insights.

### Architecture
- **Frontend**: React 18 + TypeScript (Vite)
- **Backend**: FastAPI (Python 3.13)
- **AI Engine**: LangGraph + LangChain (reusing existing components from `app/`)
- **Models**: Together AI (open-source), OpenAI (fallback)
- **Vector DB**: Qdrant (in-memory)

## Project Structure

```
pensieve-ai/
├── backend/                      # FastAPI backend
│   ├── api/
│   │   ├── routes/              # API endpoint definitions
│   │   │   ├── health.py        # Health check endpoints
│   │   │   ├── chat.py          # Conversational AI endpoints
│   │   │   └── ai.py            # RAG and agent endpoints
│   │   └── services/            # Business logic layer
│   │       ├── chat_service.py  # Chat orchestration
│   │       └── ai_service.py    # RAG and agent logic
│   ├── core/
│   │   └── config.py            # Centralized configuration (Pydantic)
│   ├── tests/                   # Backend tests
│   ├── Dockerfile               # Backend Docker image
│   └── main.py                  # FastAPI application entry point
│
├── frontend/                    # React + TypeScript frontend
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   └── ChatInterface.tsx
│   │   ├── pages/               # Page-level components
│   │   │   ├── HomePage.tsx     # Landing page
│   │   │   └── ChatPage.tsx     # Chat interface page
│   │   ├── services/            # API client
│   │   │   └── api.ts           # Axios-based API calls
│   │   ├── hooks/               # Custom React hooks
│   │   │   └── useChat.ts       # Chat state management
│   │   ├── types/               # TypeScript type definitions
│   │   │   └── chat.ts
│   │   ├── utils/               # Utility functions
│   │   ├── App.tsx              # Root component with routing
│   │   └── main.tsx             # Application entry point
│   ├── public/                  # Static assets
│   ├── Dockerfile               # Frontend Docker image
│   ├── vite.config.ts           # Vite configuration
│   ├── tsconfig.json            # TypeScript configuration
│   └── package.json             # NPM dependencies
│
├── app/                         # Shared AI/RAG components (legacy, reused)
│   ├── graphs/                  # LangGraph agent definitions
│   │   ├── simple_agent.py      # Basic tool-using agent
│   │   └── agent_with_helpfulness.py  # Agent with evaluation loop
│   ├── models.py                # Chat model configuration
│   ├── rag.py                   # RAG pipeline (retrieve + generate)
│   ├── tools.py                 # Tool belt (Tavily, Arxiv, RAG)
│   ├── state.py                 # AgentState schema
│   └── README.md                # App package documentation
│
├── data/                        # PDF documents for RAG indexing
├── images/                      # Screenshots and assets
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Environment template
├── docker-compose.yml           # Multi-container orchestration
├── pyproject.toml               # Python dependencies (uv)
└── README_NEW.md                # Project README
```

## Key Files Reference

### Backend Entry Points
- **backend/main.py:1-45** - FastAPI app initialization, CORS, router registration
- **backend/core/config.py:1-60** - Pydantic settings with env var loading

### Frontend Entry Points
- **frontend/src/main.tsx:1-11** - React app mount point
- **frontend/src/App.tsx:1-18** - Router setup with HomePage and ChatPage

### API Endpoints
- **backend/api/routes/health.py:7-18** - Health and readiness checks
- **backend/api/routes/chat.py:24-45** - Chat endpoint with RAG option
- **backend/api/routes/ai.py:24-67** - RAG query and agent execution

### AI Components (Reused from app/)
- **app/rag.py:49-150** - RAG graph with Together AI embeddings + generation
- **app/graphs/simple_agent.py:42-56** - Tool-using agent graph
- **app/tools.py:15-18** - Tool belt assembly (Tavily, Arxiv, RAG)

## Development Workflow

### 1. Initial Setup

```bash
# Clone and enter project
cd /Users/dwarak/code/pensieve-ai

# Install backend dependencies
uv sync

# Install frontend dependencies
cd frontend
npm install
cd ..

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - TOGETHER_API_KEY
# - TAVILY_API_KEY
```

### 2. Running Development Servers

**Option A: Separate terminals**

```bash
# Terminal 1: Backend
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Option B: Docker Compose**

```bash
docker-compose up --build
```

**Access Points:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)
- API Redoc: http://localhost:8000/redoc

### 3. Adding Dependencies

**Backend (Python):**
```bash
# Add new package
uv add package-name

# Add dev dependency
uv add --dev package-name

# Update dependencies
uv sync
```

**Frontend (NPM):**
```bash
cd frontend
npm install package-name
npm install --save-dev package-name  # dev dependency
```

## Common Development Tasks

### Adding a New API Endpoint

1. **Create route in `backend/api/routes/`:**

```python
# backend/api/routes/my_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    # Implementation
    return {"result": "success"}
```

2. **Register router in `backend/main.py:20-23`:**

```python
from backend.api.routes import my_feature

app.include_router(my_feature.router, prefix="/api/my-feature", tags=["my-feature"])
```

3. **Add service logic in `backend/api/services/`** (optional, for complex logic)

4. **Update frontend API client in `frontend/src/services/api.ts`**

### Adding a New Frontend Page

1. **Create page component in `frontend/src/pages/`:**

```tsx
// frontend/src/pages/MyPage.tsx
import './MyPage.css'

function MyPage() {
  return <div>My Page</div>
}

export default MyPage
```

2. **Add route in `frontend/src/App.tsx:8-12`:**

```tsx
import MyPage from './pages/MyPage'

<Route path="/my-page" element={<MyPage />} />
```

3. **Add navigation link where needed**

### Modifying RAG Behavior

**Change chunk size** (backend/core/config.py:38-39 or app/rag.py:82):
```python
CHUNK_SIZE: int = 300
CHUNK_OVERLAP: int = 0
```

**Change embedding model** (app/rag.py:88):
```python
embedding_model = TogetherEmbeddings(model="BAAI/bge-large-en-v1.5")
```

**Change generation model** (app/rag.py:105-110):
```python
llm = ChatTogether(
    model="openai/gpt-oss-20b",
    temperature=0,
)
```

**Update RAG prompt** (app/rag.py:99-103):
```python
human_template = "Your custom prompt with {context} and {query}"
```

### Adding a New AI Tool

1. **Define tool function** (create new file or add to `app/tools.py`):

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(query: str) -> str:
    """Description of what this tool does."""
    # Implementation
    return result
```

2. **Add to tool belt in `app/tools.py:15-18`:**

```python
def get_tool_belt() -> List:
    tavily_tool = TavilySearchResults(max_results=5)
    return [tavily_tool, ArxivQueryRun(), retrieve_information, my_custom_tool]
```

3. **Tool is now automatically available to all agents**

### Switching Between OpenAI and Together AI

**For chat models** (backend/core/config.py or app/models.py):
- Set `OPENAI_MODEL` or `TOGETHER_MODEL` in .env
- Update `get_chat_model()` logic

**For RAG** (app/rag.py):
- Change `embedding_model` (line 88)
- Change `llm` (line 105-110)

## Configuration

### Environment Variables (.env)

```bash
# AI Provider Keys
OPENAI_API_KEY=sk-...
TOGETHER_API_KEY=...
TAVILY_API_KEY=...

# Model Selection
OPENAI_MODEL=gpt-4.1-mini
TOGETHER_MODEL=openai/gpt-oss-20b
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# RAG Settings
RAG_DATA_DIR=data
CHUNK_SIZE=300
CHUNK_OVERLAP=0

# Backend Server
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Frontend Environment (.env in frontend/)

```bash
VITE_API_URL=http://localhost:8000
```

## API Reference

### Chat Endpoints

**POST /api/chat**
- Request: `{ messages: Message[], use_rag: bool, stream: bool }`
- Response: `{ message: Message, tool_calls?: any[] }`
- Purpose: Send chat messages with optional RAG enhancement

### AI Endpoints

**POST /api/ai/rag**
- Request: `{ query: string, top_k: number }`
- Response: `{ answer: string, sources: any[] }`
- Purpose: Query RAG system directly

**POST /api/ai/agent**
- Request: `{ task: string, agent_type: "simple" | "helpfulness" }`
- Response: `{ result: string, steps: any[], tool_calls?: any[] }`
- Purpose: Execute AI agent for complex tasks

**GET /api/ai/tools**
- Response: `{ tools: ToolInfo[] }`
- Purpose: List available AI tools

### Health Endpoints

**GET /api/health** - Basic health check

**GET /api/ready** - Readiness probe

## Testing

### Backend Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=backend

# Run specific test file
uv run pytest backend/tests/test_chat.py
```

### Frontend Tests

```bash
cd frontend

# Run tests (when implemented)
npm test

# Run linter
npm run lint
```

## Deployment

### Using Docker Compose

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment

**Backend:**
```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend:**
```bash
cd frontend
npm run build
# Serve dist/ folder with your preferred static server
```

## Troubleshooting

### Backend won't start

1. Check environment variables are set in .env
2. Verify API keys are valid
3. Check port 8000 is not in use: `lsof -i :8000`
4. Review logs for specific error messages

### Frontend can't connect to backend

1. Verify backend is running on port 8000
2. Check CORS settings in backend/main.py:16-22
3. Verify `VITE_API_URL` in frontend/.env
4. Check browser console for CORS errors

### RAG not finding documents

1. Verify PDFs exist in `data/` folder
2. Check `RAG_DATA_DIR` environment variable
3. Review console output for loading errors (app/rag.py:60-70)
4. Ensure Together AI API key is valid

### Tool not working

1. Check API key for that tool (Tavily, etc.)
2. Verify tool is in tool belt (app/tools.py:15-18)
3. Check agent is binding tools (app/graphs/simple_agent.py:20-23)

## Architecture Decisions

### Why separate backend/ and app/?

- **app/**: Reusable AI/RAG components (LangGraph, tools, RAG pipeline)
- **backend/**: FastAPI web layer (routes, services, HTTP concerns)
- This separation allows app/ to be reused in notebooks, CLI, or other contexts

### Why Vite over Create React App?

- Faster development server
- Better TypeScript support
- Smaller bundle sizes
- More modern tooling

### Why FastAPI over Flask/Django?

- Native async/await support
- Automatic API documentation (Swagger/OpenAPI)
- Type safety with Pydantic
- Better performance for I/O-bound operations (AI calls)

### Why in-memory Qdrant?

- Fast for development and small datasets
- No external dependencies
- Easy to swap for persistent Qdrant later

## Best Practices

### Backend

1. **Always use Pydantic models** for request/response validation
2. **Use service layer** for business logic (don't put it in routes)
3. **Handle exceptions** and return proper HTTP status codes
4. **Use dependency injection** for reusable dependencies
5. **Add type hints** for all functions

### Frontend

1. **Use TypeScript** for type safety
2. **Extract reusable logic** into custom hooks
3. **Keep components small** and focused
4. **Use proper error handling** in API calls
5. **Add loading states** for async operations

### AI/RAG

1. **Test prompts thoroughly** before deploying
2. **Monitor token usage** to control costs
3. **Use caching** for expensive operations (already done with @lru_cache)
4. **Implement proper error handling** for API failures
5. **Log agent execution** for debugging

## Future Enhancements

### Planned Features
- [ ] Streaming responses (WebSocket or SSE)
- [ ] User authentication (JWT)
- [ ] Conversation history persistence
- [ ] Document upload UI
- [ ] Multi-agent collaboration
- [ ] Advanced analytics dashboard
- [ ] Export conversations
- [ ] Custom tool creation UI

### Potential Improvements
- [ ] Persistent Qdrant instance
- [ ] Caching layer (Redis)
- [ ] Rate limiting
- [ ] Monitoring and observability
- [ ] Automated testing
- [ ] CI/CD pipeline

## Git Workflow

Current branches:
- **v1**: Main production branch
- **v3**: Current development branch (this new structure)

**Creating a feature:**
```bash
git checkout -b feature/my-feature v3
# Make changes
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

**Important:** Many files from v1/v2 are marked as deleted. Don't commit deletions unless intentional.

## Additional Resources

### Documentation Links
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Router](https://reactrouter.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain](https://python.langchain.com/)
- [Together AI](https://docs.together.ai/)
- [Vite](https://vitejs.dev/)

### Internal Docs
- **app/README.md** - Detailed explanation of app/ package structure
- **README_NEW.md** - Project overview and quick start
- **backend/core/config.py** - All configuration options

## Quick Reference Commands

```bash
# Start development
uv run uvicorn backend.main:app --reload  # Backend
cd frontend && npm run dev                 # Frontend

# Add dependencies
uv add package-name                        # Backend
cd frontend && npm install package-name    # Frontend

# Run tests
uv run pytest                              # Backend
cd frontend && npm test                    # Frontend

# Build for production
cd frontend && npm run build               # Frontend

# Docker
docker-compose up --build                  # Start all services
docker-compose down                        # Stop all services
docker-compose logs -f                     # View logs

# Check API
curl http://localhost:8000/api/health      # Health check
open http://localhost:8000/docs            # API docs
```

## Contact & Support

For questions about this codebase:
1. Check this CLAUDE.md file
2. Review app/README.md for AI components
3. Check API docs at /docs endpoint
4. Review code comments in key files
