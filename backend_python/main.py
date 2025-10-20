from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load API key from config file if available
try:
    import json
    import os
    config_file = "./data/config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            if config.get("openai_api_key"):
                os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
                print("✅ API key loaded from config file")
except Exception as e:
    print(f"⚠️ Could not load API key from config: {e}")

# Import routers
from routers import templates

# Make RAG router optional so the server can start even if heavy deps are missing
rag_router = None
rag_router_loaded = False

def load_rag_router():
    global rag_router, rag_router_loaded
    try:
        from routers import rag
        rag_router = rag.router
        rag_router_loaded = True
        print("✅ RAG router loaded successfully")
        return True
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"RAG router disabled due to import error: {e}")
        rag_router = None
        rag_router_loaded = False
        return False

# Try to load RAG router on startup
load_rag_router()

# Create FastAPI app
app = FastAPI(
    title="Pensieve Backend API",
    description="Backend API for Pensieve - IDE for Leaders",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
if rag_router:
    app.include_router(rag_router, prefix="/api/rag", tags=["rag"])

# Add endpoint to reload RAG router
@app.post("/api/reload-rag")
async def reload_rag():
    """Reload RAG router after API key is set"""
    global rag_router, rag_router_loaded
    
    # Remove existing RAG router if it exists
    if rag_router_loaded and rag_router:
        # Note: FastAPI doesn't have a direct way to remove routers at runtime
        # This is a limitation, but we can at least try to reload the module
        pass
    
    # Try to reload the RAG router
    success = load_rag_router()
    
    if success and rag_router:
        # Include the new RAG router
        app.include_router(rag_router, prefix="/api/rag", tags=["rag"])
        return {"success": True, "message": "RAG router reloaded successfully"}
    else:
        return {"success": False, "message": "Failed to reload RAG router"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "message": "Pensieve Backend API is running",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Pensieve Backend API", "version": "1.0.0"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Pensieve Backend API on {host}:{port}")
    print(f"📊 Health check: http://{host}:{port}/api/health")
    print(f"📝 Templates API: http://{host}:{port}/api/templates")
    print(f"🧠 RAG API: http://{host}:{port}/api/rag")
    
    uvicorn.run("main:app", host=host, port=port, reload=True)
