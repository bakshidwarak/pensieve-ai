# Quick Start Guide - Get Pensieve Running NOW

The system is hanging because **TOGETHER_API_KEY** is not set. Here are your options:

## Option 1: Get a Together AI Key (Recommended - enables all features)

1. Go to https://api.together.xyz/
2. Sign up (free tier available)
3. Get your API key from Settings → API Keys
4. Add it to `.env`:
   ```bash
   TOGETHER_API_KEY=your_actual_key_here
   ```

## Option 2: Use OpenAI Embeddings Instead (Quick workaround)

If you want to test NOW without Together AI:

### Step 1: Comment out Together AI in vector_store.py

Run these commands:

```bash
# Use OpenAI embeddings instead
nano backend/core/vector_store.py
```

Change line 7-8 from:
```python
from langchain_together import TogetherEmbeddings
```
To:
```python
from langchain_openai import OpenAIEmbeddings
```

And line 29 from:
```python
self.embedding_model = TogetherEmbeddings(
    model=settings.EMBEDDING_MODEL
)
```
To:
```python
self.embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
```

### Step 2: Update .env

Make sure OPENAI_API_KEY is set (you already have this!)

### Step 3: Start the backend

```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Option 3: Run with Mock Vector Store (Testing only)

Create a simple mock that doesn't require API keys - I can help you set this up if you want.

## What's Happening?

The issue is that when `backend.main` imports, it:
1. Loads `backend/core/vector_store.py`
2. Tries to initialize `TogetherEmbeddings`
3. Hangs waiting for Together API response with invalid key

## After You Fix This

Once backend is running, start frontend:
```bash
cd frontend
npm install  # if not done yet
npm run dev
```

Then open: http://localhost:5173/ide

Let me know which option you want and I'll help you implement it!
