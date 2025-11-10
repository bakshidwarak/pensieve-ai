"""Service layer for notes operations."""

import os
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile
from backend.core.models import Note, Tag, Attachment
from backend.core.schemas import NoteCreate, NoteUpdate
from backend.core.vector_store import get_vector_store
from backend.core.file_processor import FileProcessor
from backend.core.config import settings


class NotesService:
    """Business logic for notes management."""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.file_processor = FileProcessor()
        self.upload_dir = os.path.join(os.getcwd(), "backend", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    def create_note(
        self,
        db: Session,
        note_data: NoteCreate
    ) -> Note:
        """Create a new note with tags and vector embedding."""
        # Create note
        note = Note(
            title=note_data.title,
            content=note_data.content,
            content_type=note_data.content_type,
        )

        # Handle tags
        if note_data.tag_names:
            for tag_name in note_data.tag_names:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                note.tags.append(tag)

        db.add(note)
        db.commit()
        db.refresh(note)

        # Add to vector store
        metadata = {
            "title": note.title,
            "tags": [tag.name for tag in note.tags],
            "created_at": note.created_at.isoformat(),
        }

        vector_id = self.vector_store.add_note(
            note_id=note.id,
            content=f"{note.title}\n\n{note.content}",
            metadata=metadata
        )

        # Update note with vector_id
        note.vector_id = vector_id
        db.commit()
        db.refresh(note)

        return note

    def get_note(self, db: Session, note_id: int) -> Optional[Note]:
        """Get a note by ID."""
        return db.query(Note).filter(
            Note.id == note_id,
            Note.is_deleted == False
        ).first()

    def get_notes(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        tag_filter: Optional[List[str]] = None
    ) -> List[Note]:
        """Get all notes with optional tag filtering."""
        query = db.query(Note).filter(Note.is_deleted == False)

        if tag_filter:
            query = query.join(Note.tags).filter(Tag.name.in_(tag_filter))

        return query.order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()

    def update_note(
        self,
        db: Session,
        note_id: int,
        note_update: NoteUpdate
    ) -> Optional[Note]:
        """Update an existing note."""
        note = self.get_note(db, note_id)
        if not note:
            return None

        # Update fields
        if note_update.title is not None:
            note.title = note_update.title
        if note_update.content is not None:
            note.content = note_update.content
        if note_update.content_type is not None:
            note.content_type = note_update.content_type

        # Update tags
        if note_update.tag_names is not None:
            note.tags.clear()
            for tag_name in note_update.tag_names:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                note.tags.append(tag)

        db.commit()
        db.refresh(note)

        # Update vector store
        if note.vector_id:
            metadata = {
                "title": note.title,
                "tags": [tag.name for tag in note.tags],
                "updated_at": note.updated_at.isoformat(),
            }

            try:
                self.vector_store.update_note(
                    vector_id=note.vector_id,
                    content=f"{note.title}\n\n{note.content}",
                    metadata=metadata
                )
            except ValueError as e:
                # Vector not found - create a new one instead
                print(f"Vector ID {note.vector_id} not found, creating new vector: {e}")
                vector_id = self.vector_store.add_note(
                    note_id=note.id,
                    content=f"{note.title}\n\n{note.content}",
                    metadata=metadata
                )
                note.vector_id = vector_id
                db.commit()
            except Exception as e:
                print(f"Error updating vector store: {e}")
                # Continue anyway - don't fail the note update

        return note

    def delete_note(self, db: Session, note_id: int) -> bool:
        """Soft delete a note."""
        note = self.get_note(db, note_id)
        if not note:
            return False

        note.is_deleted = True
        db.commit()

        # Remove from vector store
        if note.vector_id:
            try:
                self.vector_store.delete_note(note.vector_id)
            except Exception as e:
                print(f"Error deleting from vector store: {e}")

        return True

    async def add_attachment(
        self,
        db: Session,
        note_id: int,
        file: UploadFile
    ) -> Optional[Attachment]:
        """Add a file attachment to a note."""
        note = self.get_note(db, note_id)
        if not note:
            return None

        # Determine file type
        file_type = self.file_processor.get_file_type(file.filename)
        if not file_type:
            raise ValueError(f"Unsupported file type: {file.filename}")

        # Save file
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        saved_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(self.upload_dir, saved_filename)

        # Write file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        file_size = len(content)

        # Extract text
        extracted_text, _ = self.file_processor.process_file(file_path, file_type)

        # Create attachment
        attachment = Attachment(
            note_id=note.id,
            filename=file.filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            mime_type=file.content_type,
            extracted_text=extracted_text
        )

        db.add(attachment)

        # Update note content with extracted text
        if extracted_text and not extracted_text.startswith("Error"):
            note.content += f"\n\n--- Extracted from {file.filename} ---\n{extracted_text}"

        db.commit()
        db.refresh(attachment)

        # Update vector store with new content
        if note.vector_id:
            metadata = {
                "title": note.title,
                "tags": [tag.name for tag in note.tags],
                "updated_at": note.updated_at.isoformat(),
            }

            self.vector_store.update_note(
                vector_id=note.vector_id,
                content=f"{note.title}\n\n{note.content}",
                metadata=metadata
            )

        return attachment

    def search_notes(
        self,
        query: str,
        tag_filter: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[dict]:
        """Search notes using vector similarity."""
        return self.vector_store.search_notes(
            query=query,
            tag_filter=tag_filter,
            limit=limit
        )


# Singleton
_notes_service = None


def get_notes_service() -> NotesService:
    """Get or create notes service instance."""
    global _notes_service
    if _notes_service is None:
        _notes_service = NotesService()
    return _notes_service
