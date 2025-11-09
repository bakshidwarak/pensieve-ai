# 🚀 START HERE - Run Pensieve.ai

## Option 1: Automated Script (Recommended)

Just run this command:

```bash
./RUN_SERVERS.sh
```

This will:
- Start the backend on port 8000
- Start the frontend on port 5173
- Show you the URLs when ready

To stop:
```bash
./STOP_SERVERS.sh
```

---

## Option 2: Manual (If script doesn't work)

### Terminal 1 - Backend

```bash
cd /Users/dwarak/code/pensieve-ai

# Start backend
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Wait until you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Terminal 2 - Frontend

```bash
cd /Users/dwarak/code/pensieve-ai/frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

Wait until you see:
```
  ➜  Local:   http://localhost:5173/
```

---

## ✅ Verify It's Working

Open these URLs in your browser:

1. **Frontend IDE:** http://localhost:5173/ide
2. **API Docs:** http://localhost:8000/docs
3. **Health Check:** http://localhost:8000/api/health

---

## 🐛 Troubleshooting

### Backend won't start?

```bash
# Check what's on port 8000
lsof -i :8000

# Kill it if needed
lsof -ti:8000 | xargs kill -9

# Check the logs
tail -f backend.log
```

### Frontend won't start?

```bash
# Check what's on port 5173
lsof -i :5173

# Kill it if needed
lsof -ti:5173 | xargs kill -9

# Reinstall dependencies
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Still having issues?

Check the logs:
```bash
# Backend logs
tail -50 backend.log

# Frontend logs
tail -50 frontend.log
```

---

## 📝 What I Changed

I've already configured the app to use **OpenAI only** (no Together AI needed):

- ✅ Embeddings: OpenAI `text-embedding-3-small`
- ✅ LLM for chat: OpenAI `gpt-4o-mini`
- ✅ Disabled Tavily (web search) for now

All you need is your OPENAI_API_KEY (already in .env).

---

## 🎯 Quick Test

Once both servers are running:

1. Go to http://localhost:5173/ide
2. Click the **+** button to create a note
3. Type some content and click **Save**
4. Ask a question in the chat panel on the right

That's it!
