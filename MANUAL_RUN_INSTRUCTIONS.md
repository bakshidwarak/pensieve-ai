# Manual Run Instructions - Pensieve.ai

The backend keeps hanging during startup. This is because it's trying to load AI models during import.

## ✅ SOLUTION: Run in YOUR Terminal (Not Via Scripts)

### Step 1: Open Terminal 1 - Backend

```bash
cd /Users/dwarak/code/pensieve-ai

# Kill any existing processes
pkill -9 -f uvicorn

# Start backend manually
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**WAIT** until you see this message:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

This may take 30-60 seconds on first run because it's:
- Loading AI models
- Initializing the database
- Setting up the vector store

### Step 2: Open Terminal 2 - Frontend

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

### Step 3: Test It

Open in browser:
- Frontend: http://localhost:5173/ide
- API Docs: http://localhost:8000/docs

---

## 🎯 Quick Test Once Running

1. Go to http://localhost:5173/ide
2. Click the **+** button (create note)
3. Type "Test Note" as title
4. Type "This is my first note" as content
5. Click **Save**
6. See if it saves successfully

---

## 🐛 Troubleshooting

### Backend stuck at "None of PyTorch, TensorFlow..." message?

This is NORMAL. It's a warning, not an error. Just wait 30-60 seconds more.

### Backend shows error about "TogetherEmbeddings"?

I need to fix one more file. Run this:

```bash
# Fix the import
sed -i '' 's/from langchain_together import TogetherEmbeddings/from langchain_openai import OpenAIEmbeddings/' app/rag.py
sed -i '' 's/TogetherEmbeddings/OpenAIEmbeddings/' app/rag.py
```

### Port 8000 already in use?

```bash
# Find what's using it
lsof -i :8000

# Kill it
lsof -ti:8000 | xargs kill -9
```

### Frontend won't install?

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 What Should Happen

**Backend Terminal:**
```
INFO:     Will watch for changes in these directories: ['/Users/dwarak/code/pensieve-ai']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Frontend Terminal:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 🎉 Success Looks Like

When you go to http://localhost:5173/ide you should see:
- Left sidebar (empty at first)
- Middle editor panel
- Right chat panel

That's it! The app is running!
