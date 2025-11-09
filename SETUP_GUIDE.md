# Pensieve.ai Setup Guide - Note Ingestion System

## Overview

You now have a complete note ingestion and management system with:

- ✅ **Backend API** (FastAPI with SQLite + Qdrant)
- ✅ **Frontend IDE** (React with 3-panel layout)
- ✅ **Voice Transcription** (OpenAI Whisper)
- ✅ **File Processing** (Images, PDFs, DOCX, PPTX, Text)
- ✅ **Vector Search** (Persistent Qdrant)
- ✅ **AI Chat** (Chat with your notes using RAG)

## Prerequisites

### System Requirements
- Python 3.13+
- Node.js 20+
- Tesseract OCR (for image text extraction)

### Install Tesseract

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

## Installation

### 1. Install Backend Dependencies

```bash
# From project root
uv sync
```

This will install all Python dependencies including:
- FastAPI, Uvicorn
- SQLAlchemy, Pydantic
- OpenAI, LangChain, Together AI
- Qdrant, PIL, PyPDF2, python-docx, python-pptx, pytesseract

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Set Up Environment Variables

```bash
# Copy the example
cp .env.example .env

# Edit .env and add your API keys
```

Required variables in `.env`:
```bash
# CRITICAL: Add these API keys
OPENAI_API_KEY=sk-...          # For Whisper transcription
TOGETHER_API_KEY=...           # For embeddings and LLM
TAVILY_API_KEY=...             # Optional (for web search)

# Model configuration
TOGETHER_MODEL=openai/gpt-oss-20b
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# Database
DATABASE_URL=sqlite:///./pensieve.db
```

## Running the Application

### Option 1: Development Mode (Recommended)

**Terminal 1 - Backend:**
```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: Docker

```bash
docker-compose up --build
```

## Access Points

- **Frontend IDE:** http://localhost:5173/ide
- **Simple Chat:** http://localhost:5173/chat
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **API Redoc:** http://localhost:8000/redoc

## Using the IDE

### 1. Create Your First Note

1. Open http://localhost:5173/ide
2. Click the **+** button in the sidebar
3. A new note will be created
4. Edit the title and content
5. Add tags by typing in the tag input and pressing Enter
6. Click **Save** to persist changes

### 2. Add Voice Input

1. Select a note
2. Click **🎤 Voice** in the toolbar
3. Click **Start Recording**
4. Speak your note
5. Click **Stop** when done
6. The transcribed text will be added to your note

### 3. Attach Files

1. Select a note
2. Click **📎 Attach** in the toolbar
3. Drag and drop a file or click to browse
4. Supported files:
   - **Images:** PNG, JPG, JPEG, GIF, BMP (OCR text extraction)
   - **PDFs:** Text extraction
   - **Documents:** DOCX, PPTX (text extraction)
   - **Text:** TXT, MD
5. Click **Upload**
6. The extracted text will be appended to your note

### 4. Chat with Your Notes

1. Type a question in the chat panel (right side)
2. The AI will search your notes and provide an answer
3. Only information from your notes will be used
4. Filter by tags for more specific searches

### 5. Search Notes

- Use the search box in the sidebar to filter notes
- Search works on title, content, and tags

## API Endpoints

### Notes Management

**Create Note:**
```bash
POST /api/notes/
{
  "title": "My Note",
  "content": "Note content...",
  "tag_names": ["meeting", "important"]
}
```

**Get All Notes:**
```bash
GET /api/notes/?skip=0&limit=100&tags=meeting,feedback
```

**Get Single Note:**
```bash
GET /api/notes/{note_id}
```

**Update Note:**
```bash
PUT /api/notes/{note_id}
{
  "title": "Updated Title",
  "content": "Updated content...",
  "tag_names": ["new-tag"]
}
```

**Delete Note:**
```bash
DELETE /api/notes/{note_id}
```

### File Upload

**Add Attachment:**
```bash
POST /api/notes/{note_id}/attachments
Content-Type: multipart/form-data

file: <binary file data>
```

### Voice Transcription

**Transcribe Audio:**
```bash
POST /api/transcribe/
Content-Type: multipart/form-data

file: <audio file>
language: en
```

**Supported formats:** mp3, mp4, mpeg, mpga, m4a, wav, webm

### Search

**Search Notes:**
```bash
POST /api/notes/search
{
  "query": "What did we discuss in the meeting?",
  "tag_filter": ["meeting"],
  "limit": 10
}
```

### Chat

**Chat with Notes:**
```bash
POST /api/chat/
{
  "messages": [
    {"role": "user", "content": "What are my action items?"}
  ],
  "use_notes": true,
  "tag_filter": ["todo"]
}
```

### Tags

**Get All Tags:**
```bash
GET /api/notes/tags/all
```

**Create Tag:**
```bash
POST /api/notes/tags
{
  "name": "urgent",
  "color": "#ff4444",
  "description": "Urgent items"
}
```

## Data Storage

### SQLite Database
- Location: `./pensieve.db`
- Contains: Notes, Tags, Attachments, metadata
- Schema auto-created on startup

### Qdrant Vector Store
- Location: `./qdrant_storage/`
- Contains: Note embeddings for semantic search
- Persistent across restarts
- Collection name: `pensieve_notes`

### File Uploads
- Location: `./backend/uploads/`
- Organized by UUID filenames
- Original filenames stored in database

## Architecture

### Backend Structure

```
backend/
├── api/
│   ├── routes/
│   │   ├── notes.py          # CRUD, search, tags, attachments
│   │   ├── transcribe.py     # Voice transcription
│   │   ├── chat.py           # Chat with notes
│   │   └── ai.py             # RAG endpoints
│   └── services/
│       ├── notes_service.py      # Business logic
│       └── notes_rag_service.py  # RAG queries
├── core/
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── database.py           # DB session management
│   ├── config.py             # Configuration
│   ├── vector_store.py       # Qdrant operations
│   └── file_processor.py     # File text extraction
└── main.py                   # FastAPI app
```

### Frontend Structure

```
frontend/src/
├── pages/
│   ├── IDEPage.tsx           # Main 3-panel IDE
│   └── ChatPage.tsx          # Simple chat view
├── components/
│   ├── NotesSidebar.tsx      # Notes list + search
│   ├── NoteEditor.tsx        # Note editing
│   ├── ChatInterface.tsx     # Chat UI
│   ├── VoiceRecorder.tsx     # Voice input
│   └── FileUploader.tsx      # File upload
├── hooks/
│   ├── useNotes.ts           # Notes state management
│   └── useChat.ts            # Chat state management
├── services/
│   ├── api.ts                # Chat API client
│   └── notesApi.ts           # Notes API client
└── types/
    ├── notes.ts              # Note types
    └── chat.ts               # Chat types
```

## Features Explained

### 1. Note Vectorization

When you create or update a note:
1. Text is extracted from title + content + attachments
2. Text is embedded using Together AI's BAAI/bge-large-en-v1.5
3. Vector is stored in Qdrant with metadata (tags, title, etc.)
4. Used for semantic search and RAG

### 2. File Processing

Different file types are processed differently:

- **Images:** Tesseract OCR extracts text
- **PDFs:** PyPDF2 extracts text page by page
- **DOCX:** python-docx extracts paragraphs
- **PPTX:** python-pptx extracts slide text
- **Text files:** Direct read

Extracted text is:
- Stored in the `attachments` table
- Appended to note content
- Included in vector embedding

### 3. Voice Transcription

Uses OpenAI Whisper API:
1. Browser records audio (WebM format)
2. Audio sent to backend
3. Whisper transcribes with high accuracy
4. Text returned to editor
5. User can edit before saving

### 4. Chat with Notes

RAG (Retrieval-Augmented Generation) flow:
1. User asks a question
2. Question is embedded
3. Similar notes retrieved from Qdrant (vector search)
4. Notes provided as context to LLM
5. LLM generates answer based ONLY on notes
6. If no relevant notes, AI says "I don't know"

### 5. Tagging System

- Tags are reusable across notes
- Many-to-many relationship
- Color-coded for visual organization
- Filterable in search and chat

## Troubleshooting

### Backend won't start

**Error: "No module named 'backend'"**
```bash
# Make sure you're in project root
pwd  # Should show .../pensieve-ai
uv run uvicorn backend.main:app --reload
```

**Error: "Could not import Together"**
```bash
uv sync  # Reinstall dependencies
```

### Frontend won't start

**Error: "Cannot find module '@/...'"**
```bash
cd frontend
npm install
```

### Tesseract not found

**Error: "TesseractNotFoundError"**
```bash
# Install Tesseract OCR
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Linux
```

### Voice recording not working

- Ensure HTTPS or localhost (required for microphone access)
- Grant microphone permissions in browser
- Check OPENAI_API_KEY is set

### Files not uploading

- Check `backend/uploads/` directory exists
- Verify file type is supported
- Check file size (default limit: 10MB)

### Notes not appearing in chat

- Verify notes have been created and saved
- Check Qdrant storage exists: `ls qdrant_storage/`
- Verify TOGETHER_API_KEY is set (for embeddings)

### Search returns no results

- Notes need to be vectorized (happens on create/update)
- Check vector_id field is populated in database
- Verify Qdrant collection exists

## Testing the System

### 1. Create Test Notes

```bash
curl -X POST http://localhost:8000/api/notes/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting Notes",
    "content": "Discussed Q1 goals. Action items: Review proposal by Friday.",
    "tag_names": ["meeting", "todo"]
  }'
```

### 2. Search Notes

```bash
curl -X POST http://localhost:8000/api/notes/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "action items",
    "limit": 5
  }'
```

### 3. Chat with Notes

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What are my action items?"}
    ],
    "use_notes": true
  }'
```

### 4. Upload File

```bash
curl -X POST http://localhost:8000/api/notes/1/attachments \
  -F "file=@/path/to/document.pdf"
```

### 5. Transcribe Audio

```bash
curl -X POST http://localhost:8000/api/transcribe/ \
  -F "file=@/path/to/audio.mp3" \
  -F "language=en"
```

## Next Steps

### Recommended Enhancements

1. **User Authentication**
   - Add JWT-based auth
   - Multi-user support
   - User-specific notes

2. **Advanced Search**
   - Full-text search (combine with vector search)
   - Date range filters
   - Content type filters

3. **Collaboration**
   - Share notes with team
   - Comments and annotations
   - Real-time collaboration

4. **Export/Import**
   - Export notes to Markdown, PDF
   - Import from Evernote, Notion, etc.
   - Backup/restore functionality

5. **Mobile App**
   - React Native app
   - Voice-first interface
   - Offline sync

6. **Analytics**
   - Note creation trends
   - Tag usage statistics
   - Search analytics

## Updating Dependencies

### Backend

```bash
# Add new package
uv add package-name

# Update all packages
uv sync --upgrade
```

### Frontend

```bash
cd frontend
npm install package-name
npm update
```

## Database Migrations

Currently using SQLAlchemy's `create_all()` which auto-creates tables.

For production, use Alembic:

```bash
# Install Alembic
uv add alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Deployment Checklist

Before deploying to production:

- [ ] Change DEBUG=False in .env
- [ ] Use production database (PostgreSQL recommended)
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure backup strategy
- [ ] Use production-grade Qdrant (Docker or Cloud)
- [ ] Implement proper authentication
- [ ] Add request logging
- [ ] Set up CI/CD pipeline

## Support

For issues with Pensieve.ai:
1. Check this setup guide
2. Review CLAUDE.md for detailed code documentation
3. Check API docs at /docs
4. Review browser console and backend logs

## License

MIT
