# ⚠️ TROUBLESHOOTING - Backend Not Running

## Your Current Situation

✅ Frontend IS running (you can see the IDE)
❌ Backend is NOT running (that's why nothing works)

## Why "Create Note" Does Nothing

The frontend is trying to call:
```
POST http://localhost:8000/api/notes/
```

But there's no backend listening on port 8000, so:
- Create note button does nothing
- Chat returns "Failed to get response"
- Everything times out

## ✅ THE FIX - Start Backend Properly

The backend CANNOT be started in background via Claude Code because it hangs during AI model loading.

### YOU MUST DO THIS MANUALLY:

Open **your own Terminal** (not Claude Code) and run:

```bash
cd /Users/dwarak/code/pensieve-ai

# Kill any stuck processes
pkill -9 -f uvicorn

# Start backend (WAIT and WATCH the output)
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### What You'll See:

```
None of PyTorch, TensorFlow >= 2.0, or Flax have been found...
(This is just a warning - NOT an error)

Loading models...
(wait 30-60 seconds)

INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.  <-- WAIT FOR THIS
```

**ONLY AFTER** you see "Application startup complete" will the backend work.

## Verify Backend is Running

In another terminal:
```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{"status":"healthy","service":"pensieve-ai"}
```

## Now Try the Frontend Again

1. Go back to http://localhost:5173/ide
2. Click **+** button (create note)
3. It should work now!

---

## If Backend Still Won't Start

### Check for import errors:

```bash
cd /Users/dwarak/code/pensieve-ai
uv run python -c "from backend.main import app; print('✅ Backend imports OK')"
```

If you see an error, send me the full error message.

### Check if port is in use:

```bash
lsof -i :8000
```

If something is using it:
```bash
lsof -ti:8000 | xargs kill -9
```

### Try a different port:

```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
```

Then update frontend/.env:
```
VITE_API_URL=http://localhost:8001
```

---

## Quick Diagnosis

Run this to see what's happening:

```bash
# Is backend process running?
ps aux | grep uvicorn

# Is it listening on port 8000?
lsof -i :8000

# Can we connect?
curl -v http://localhost:8000/api/health
```

---

## The Root Cause

The backend startup process:
1. Imports all modules
2. Loads AI models (OpenAI embeddings)
3. Initializes database
4. Sets up vector store
5. **This takes 30-60 seconds**

When run in background, it gets stuck at step 2-3.
When YOU run it in your terminal, you can see the progress.

---

## ✅ What Should Work Once Backend Starts

1. Create notes ✓
2. Edit and save notes ✓
3. Add tags ✓
4. Search notes ✓
5. Upload files ✓
6. Voice recording ✓
7. Chat with notes ✓

But NONE of this works until the backend is running!

---

## Still Stuck?

Run this diagnostic script:

```bash
cd /Users/dwarak/code/pensieve-ai

# Create diagnostic
cat > diagnose.sh << 'EOF'
#!/bin/bash
echo "=== Pensieve.ai Diagnostic ==="
echo ""
echo "1. Python version:"
python3 --version
echo ""
echo "2. uv installed:"
which uv
echo ""
echo "3. Dependencies installed:"
ls -la .venv 2>/dev/null || echo "Virtual env not found"
echo ""
echo "4. Port 8000 status:"
lsof -i :8000 || echo "Port 8000 is FREE"
echo ""
echo "5. Port 5173 status:"
lsof -i :5173 || echo "Port 5173 is FREE"
echo ""
echo "6. Can import backend:"
uv run python -c "from backend.main import app" 2>&1
echo ""
echo "=== End Diagnostic ==="
EOF

chmod +x diagnose.sh
./diagnose.sh
```

Send me the output and I'll help debug further.
