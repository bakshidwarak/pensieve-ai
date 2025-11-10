"""FastAPI application entry point for Pensieve.ai backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api.routes import health, notes, transcribe, templates, interview, strategy
# Temporarily disabled - heavy AI imports causing startup delays
# from backend.api.routes import ai, chat
from backend.core.config import settings
from backend.core.database import init_db
import os

# Initialize database on startup
init_db()

app = FastAPI(
    title="Pensieve.ai API",
    description="Backend API for Pensieve - IDE for Leaders",
    version="0.1.0",
)

# Startup event to seed templates
@app.on_event("startup")
async def startup_event():
    """Seed templates on startup."""
    try:
        from backend.seed_templates import seed_templates
        seed_templates()
        print("✅ Templates seeded successfully")
    except Exception as e:
        print(f"⚠️  Template seeding skipped: {e}")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving files
uploads_dir = os.path.join(os.getcwd(), "backend", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(transcribe.router, prefix="/api/transcribe", tags=["transcribe"])
app.include_router(interview.router, prefix="/api/interview", tags=["interview"])
app.include_router(strategy.router, prefix="/api/strategy", tags=["strategy"])
# Temporarily disabled - heavy AI imports
# app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
# app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Pensieve.ai API",
        "docs": "/docs",
        "version": "0.1.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
