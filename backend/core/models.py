"""SQLAlchemy database models for Pensieve.ai."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Table, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base


# Association table for note tags (many-to-many)
note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Note(Base):
    """Note model for storing user notes."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, audio, image, pdf, etc.

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # File information (if note has attached files)
    file_path = Column(String(1000), nullable=True)
    file_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)

    # Audio transcription metadata
    audio_duration = Column(Integer, nullable=True)
    transcription_confidence = Column(Integer, nullable=True)

    # Vector DB reference
    vector_id = Column(String(100), nullable=True, unique=True)

    # Soft delete
    is_deleted = Column(Boolean, default=False)

    # Additional metadata (JSON field for extensibility)
    # Note: Using 'extra_metadata' instead of 'metadata' (reserved by SQLAlchemy)
    extra_metadata = Column(JSON, nullable=True)

    # Relationships
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")
    attachments = relationship("Attachment", back_populates="note", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title[:30]}...')>"


class Tag(Base):
    """Tag model for categorizing notes."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    color = Column(String(20), default="#667eea")  # Hex color for UI
    description = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    notes = relationship("Note", secondary=note_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(name='{self.name}')>"


class Attachment(Base):
    """Attachment model for files associated with notes."""

    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)

    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=False)  # image, pdf, docx, etc.
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=True)

    # Extracted content (for text extraction from images, PDFs, etc.)
    extracted_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    note = relationship("Note", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment(filename='{self.filename}')>"


class Template(Base):
    """Template/Snippet model for note templates (TextMate-style)."""

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    trigger = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "meet", "todo"
    label = Column(String(200), nullable=False)  # e.g., "Meeting Notes"
    description = Column(String(1000), nullable=True)
    content = Column(Text, nullable=False)  # Template content with {{placeholders}}

    # Template metadata
    is_system = Column(Boolean, default=False)  # System templates vs user-created
    category = Column(String(100), nullable=True)  # meeting, task, document, etc.

    # Variables/placeholders used in template (JSON array)
    # e.g., ["title", "date", "attendees"]
    variables = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Template(trigger='{self.trigger}', label='{self.label}')>"
