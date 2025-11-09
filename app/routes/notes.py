from fastapi import APIRouter, Header, HTTPException
from app.schemas import NoteCreate, ChatRequest
from app.services.notes_service import create_note, list_notes, get_note
from app.services.chat_service import answer_query

router = APIRouter()

def check_api_key(x_api_key: str | None):
    if not x_api_key or x_api_key not in ("dev-key",):
        raise HTTPException(status_code=401, detail="missing or invalid x-api-key")

@router.post("/notes")
async def post_note(payload: NoteCreate, x_api_key: str | None = Header(None)):
    check_api_key(x_api_key)
    nid = await create_note(payload.text, payload.tags, payload.metadata)
    return {"id": nid}

@router.get("/notes")
async def get_notes(tag: str | None = None, x_api_key: str | None = Header(None)):
    check_api_key(x_api_key)
    rows = await list_notes(tag)
    out = [{"id": r.id, "text": r.text, "tags": r.tags, "metadata": r.metadata, "created_at": r.created_at} for r in rows]
    return out

@router.get("/notes/{note_id}")
async def get_single_note(note_id: str, x_api_key: str | None = Header(None)):
    check_api_key(x_api_key)
    n = await get_note(note_id)
    if not n:
        raise HTTPException(404, "not found")
    return {"id": n.id, "text": n.text, "tags": n.tags, "metadata": n.metadata, "created_at": n.created_at}

@router.post("/chat")
async def chat(req: ChatRequest, x_api_key: str | None = Header(None)):
    check_api_key(x_api_key)
    res = await answer_query(req.query, req.top_k, req.tag_filters)
    return res
