from app.db import AsyncSessionLocal
from app.models import Note
from app.utils import make_id
from app.embeddings_store import vector_store
from sqlalchemy import select

async def create_note(text: str, tags: list = None, metadata: dict = None):
    note_id = make_id("n")
    tags = tags or []
    metadata = metadata or {}
    async with AsyncSessionLocal() as session:
        note = Note(id=note_id, text=text, tags=tags, metadata=metadata)
        session.add(note)
        await session.commit()
    await vector_store.add_note(note_id, text, {"tags": tags, **(metadata or {})})
    return note_id

async def list_notes(tag: str | None = None, limit: int = 50):
    async with AsyncSessionLocal() as session:
        if tag:
            q = select(Note).where(Note.tags.contains([tag])).limit(limit)
        else:
            q = select(Note).limit(limit)
        r = await session.execute(q)
        rows = r.scalars().all()
        return rows

async def get_note(note_id: str):
    async with AsyncSessionLocal() as session:
        r = await session.get(Note, note_id)
        return r
