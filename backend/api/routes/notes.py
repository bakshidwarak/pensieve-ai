"""API routes for notes management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.schemas import (
    Note,
    NoteCreate,
    NoteUpdate,
    NoteList,
    Tag,
    TagCreate,
    SearchRequest,
)
from backend.core.models import Tag as TagModel
from backend.api.services.notes_service import get_notes_service, NotesService

router = APIRouter()


# ==================== NOTES CRUD ====================

@router.post("/", response_model=Note, status_code=201)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    service: NotesService = Depends(get_notes_service)
):
    """Create a new note."""
    try:
        return service.create_note(db, note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[NoteList])
def get_notes(
    skip: int = 0,
    limit: int = 100,
    tags: Optional[str] = None,
    db: Session = Depends(get_db),
    service: NotesService = Depends(get_notes_service)
):
    """
    Get all notes.

    - **skip**: Number of notes to skip (pagination)
    - **limit**: Maximum number of notes to return
    - **tags**: Comma-separated list of tags to filter by
    """
    tag_filter = tags.split(",") if tags else None
    notes = service.get_notes(db, skip=skip, limit=limit, tag_filter=tag_filter)

    # Convert to list format (truncate content)
    return [
        NoteList(
            id=note.id,
            title=note.title,
            content=note.content[:200] + "..." if len(note.content) > 200 else note.content,
            content_type=note.content_type,
            created_at=note.created_at,
            updated_at=note.updated_at,
            tags=note.tags
        )
        for note in notes
    ]


@router.get("/{note_id}", response_model=Note)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    service: NotesService = Depends(get_notes_service)
):
    """Get a specific note by ID."""
    note = service.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    service: NotesService = Depends(get_notes_service)
):
    """Update a note."""
    note = service.update_note(db, note_id, note_update)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    service: NotesService = Depends(get_notes_service)
):
    """Delete a note (soft delete)."""
    success = service.delete_note(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return None


# ==================== FILE ATTACHMENTS ====================

@router.post("/{note_id}/attachments", status_code=201)
async def add_attachment(
    note_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    service: NotesService = Depends(get_notes_service)
):
    """
    Add a file attachment to a note.

    Supported file types:
    - Images: PNG, JPG, JPEG, GIF, BMP (OCR text extraction)
    - PDFs: Text extraction
    - Documents: DOCX, PPTX (text extraction)
    - Text: TXT, MD
    """
    try:
        attachment = await service.add_attachment(db, note_id, file)
        if not attachment:
            raise HTTPException(status_code=404, detail="Note not found")
        return {
            "id": attachment.id,
            "filename": attachment.filename,
            "file_type": attachment.file_type,
            "file_size": attachment.file_size,
            "extracted_text_preview": attachment.extracted_text[:200] if attachment.extracted_text else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SEARCH ====================

@router.post("/search", response_model=List[dict])
def search_notes(
    search: SearchRequest,
    service: NotesService = Depends(get_notes_service)
):
    """
    Search notes using semantic similarity.

    - **query**: Search query
    - **tag_filter**: Optional list of tags to filter by
    - **limit**: Maximum number of results
    """
    try:
        results = service.search_notes(
            query=search.query,
            tag_filter=search.tag_filter,
            limit=search.limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TAGS ====================

@router.get("/tags/all", response_model=List[Tag])
def get_all_tags(db: Session = Depends(get_db)):
    """Get all available tags."""
    tags = db.query(TagModel).order_by(TagModel.name).all()
    return tags


@router.post("/tags", response_model=Tag, status_code=201)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db)
):
    """Create a new tag."""
    # Check if tag exists
    existing = db.query(TagModel).filter(TagModel.name == tag.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")

    new_tag = TagModel(**tag.model_dump())
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag
