from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db
from app.routes import notes
from app.ws_transcribe import handle_ws

app = FastAPI(title="Pensieve Notes API (PoC)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(notes.router, prefix="/v1")

@app.websocket("/v1/stream-transcribe")
async def ws_stream_transcribe(websocket: WebSocket):
    await handle_ws(websocket)
