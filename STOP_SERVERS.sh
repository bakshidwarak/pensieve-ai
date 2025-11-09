#!/bin/bash

echo "🛑 Stopping Pensieve.ai servers..."

# Kill processes on ports 8000 and 5173
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Backend stopped" || echo "   Backend was not running"
lsof -ti:5173 | xargs kill -9 2>/dev/null && echo "✅ Frontend stopped" || echo "   Frontend was not running"

echo ""
echo "All servers stopped."
