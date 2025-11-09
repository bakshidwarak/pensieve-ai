#!/bin/bash

echo "========================================="
echo "  Starting Pensieve.ai Servers"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this from the pensieve-ai directory"
    exit 1
fi

# Kill any existing processes on ports 8000 and 5173
echo "🧹 Cleaning up old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend
echo ""
echo "🚀 Starting Backend on port 8000..."
echo "   (This may take 10-15 seconds...)"
echo ""

uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "   Waiting for backend to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "   ✅ Backend is ready!"
        break
    fi
    echo -n "."
    sleep 1
done

# Check if backend is actually running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo ""
    echo "❌ Backend failed to start. Check backend.log for errors:"
    echo "   tail -50 backend.log"
    exit 1
fi

echo ""
echo "========================================="
echo "  Backend Running ✅"
echo "  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================="
echo ""

# Start frontend
echo "🚀 Starting Frontend on port 5173..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "   📦 Installing frontend dependencies (first time)..."
    npm install
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for frontend
echo "   Waiting for frontend to start..."
for i in {1..20}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "   ✅ Frontend is ready!"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "========================================="
echo "  ✅ BOTH SERVERS RUNNING!"
echo "========================================="
echo ""
echo "📝 Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🎨 Frontend: http://localhost:5173"
echo "   IDE Page: http://localhost:5173/ide"
echo ""
echo "========================================="
echo ""
echo "📋 Process IDs:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "🛑 To stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   OR run: ./STOP_SERVERS.sh"
echo ""
echo "📊 View logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "========================================="
echo ""
echo "🎉 Ready! Open http://localhost:5173/ide"
echo ""
