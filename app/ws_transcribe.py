import asyncio
import json
import uuid
from fastapi import WebSocket, WebSocketDisconnect
from app.transcribe import transcribe_audio_bytes_blocking
from app.services.notes_service import create_note
from app.config import settings

SESSIONS: dict = {}

async def handle_ws(websocket: WebSocket):
    await websocket.accept()
    qs = websocket.scope.get("query_string", b"").decode()
    params = {}
    for p in qs.split("&"):
        if "=" in p:
            k,v = p.split("=",1)
            params[k]=v
    note_temp_id = params.get("noteTempId") or f"temp-{uuid.uuid4().hex[:8]}"
    api_key = params.get("x-api-key")
    if not api_key or api_key not in settings.API_KEYS.split(","):
        await websocket.send_text(json.dumps({"type":"error","message":"Unauthorized"}))
        await websocket.close()
        return

    SESSIONS[note_temp_id] = {"transcripts": [], "meta": {}, "created_at": asyncio.get_event_loop().time()}

    try:
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.disconnect":
                break

            if "text" in msg and msg["text"] is not None:
                try:
                    data = json.loads(msg["text"])
                except Exception:
                    await websocket.send_text(json.dumps({"type":"error","message":"invalid json"}))
                    continue

                if data.get("type") == "stop":
                    tags = data.get("tags", [])
                    final_text = " ".join([t["text"] for t in SESSIONS[note_temp_id]["transcripts"]])
                    note_id = await create_note(final_text, tags=tags, metadata={"source":"live_mic"})
                    await websocket.send_text(json.dumps({"type":"note_saved","note_id":note_id}))
                    try:
                        del SESSIONS[note_temp_id]
                    except KeyError:
                        pass
                    await websocket.close()
                    return
                else:
                    await websocket.send_text(json.dumps({"type":"info","message":"control received"}))
                    continue

            if "bytes" in msg and msg["bytes"] is not None:
                audio_bytes = msg["bytes"]
                loop = asyncio.get_event_loop()
                transcript_text = await loop.run_in_executor(None, lambda: transcribe_audio_bytes_blocking(audio_bytes, "chunk.webm"))

                chunk_record = {"chunk_id": str(uuid.uuid4()), "text": transcript_text, "timestamp": asyncio.get_event_loop().time()}
                SESSIONS[note_temp_id]["transcripts"].append(chunk_record)

                await websocket.send_text(json.dumps({
                    "type": "transcript_chunk",
                    "chunk_id": chunk_record["chunk_id"],
                    "text": transcript_text,
                    "timestamp": chunk_record["timestamp"]
                }))

    except WebSocketDisconnect:
        try:
            del SESSIONS[note_temp_id]
        except KeyError:
            pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type":"error","message": str(e)}))
            await websocket.close()
        except:
            pass
        try:
            del SESSIONS[note_temp_id]
        except:
            pass
