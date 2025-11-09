# Pensieve.ai - IDE for Leaders

An intelligent development environment designed to help leaders navigate complexity, make informed decisions, and drive strategic outcomes using AI-powered insights.

## Project Structure

```
pensieve-ai/
├── backend/              # FastAPI backend
│   ├── api/             # API routes and services
│   │   ├── routes/      # Endpoint definitions
│   │   └── services/    # Business logic
│   ├── core/            # Core configuration
│   └── main.py          # Application entry point
├── frontend/            # React + TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript types
│   └── public/          # Static assets
├── app/                 # Shared AI/RAG components (LangGraph)
│   ├── graphs/          # Agent definitions
│   ├── models.py        # Model configuration
│   ├── rag.py           # RAG pipeline
│   ├── tools.py         # AI tools
│   └── state.py         # State management
├── data/                # PDF documents for RAG
└── images/              # Assets and screenshots
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.13)
- **AI/LLM**: LangChain, LangGraph
- **Models**: Together AI (open-source endpoints), OpenAI (fallback)
- **Vector DB**: Qdrant (in-memory)
- **Tools**: Tavily (web search), Arxiv (academic papers)

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Routing**: React Router
- **Styling**: CSS Modules
- **HTTP Client**: Axios

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 20+
- uv (Python package manager)

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY, TOGETHER_API_KEY, TAVILY_API_KEY
```

### 2. Backend Setup

```bash
# Install Python dependencies
uv sync

# Run backend
uv run uvicorn backend.main:app --reload

# Backend runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy frontend environment
cp .env.example .env

# Run development server
npm run dev

# Frontend runs on http://localhost:5173
```

### 4. Docker Setup (Alternative)

```bash
# Build and run both frontend and backend
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

## API Endpoints

### Health
- `GET /api/health` - Health check
- `GET /api/ready` - Readiness check

### Chat
- `POST /api/chat` - Send chat messages
- `POST /api/chat/stream` - Streaming chat (coming soon)

### AI
- `POST /api/ai/rag` - Query RAG system
- `POST /api/ai/agent` - Execute AI agent
- `GET /api/ai/tools` - List available tools

## Features

### Current
- AI-powered chat interface
- RAG (Retrieval-Augmented Generation) for document Q&A
- Agentic workflows with LangGraph
- Tool integration (web search, academic papers)
- Modern responsive UI

### Planned
- Streaming responses
- Multi-agent collaboration
- Document upload and management
- User authentication
- Conversation history
- Advanced analytics dashboard

## Development

### Backend Development

```bash
# Run tests
uv run pytest

# Add new dependency
uv add package-name

# Update dependencies
uv sync
```

### Frontend Development

```bash
cd frontend

# Run linter
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

### Backend (`backend/core/config.py`)
- Model selection (OpenAI vs Together AI)
- RAG chunk size and overlap
- CORS origins
- Database settings

### Frontend (`frontend/.env`)
- API URL configuration
- Feature flags (future)

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

MIT

## Support

For issues and questions, please open a GitHub issue.
