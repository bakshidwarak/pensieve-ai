"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# Tag Schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#667eea", pattern=r"^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class Tag(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Attachment Schemas
class AttachmentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int
    mime_type: Optional[str] = None


class Attachment(AttachmentBase):
    id: int
    note_id: int
    file_path: str
    extracted_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Note Schemas
class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str
    content_type: str = Field(default="text")


class NoteCreate(NoteBase):
    tag_names: List[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    tag_names: Optional[List[str]] = None


class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    audio_duration: Optional[int] = None
    vector_id: Optional[str] = None
    tags: List[Tag] = []
    attachments: List[Attachment] = []

    class Config:
        from_attributes = True


class NoteList(BaseModel):
    """Simplified note for list views."""
    id: int
    title: str
    content: str = Field(..., description="First 200 chars of content")
    content_type: str
    created_at: datetime
    updated_at: datetime
    tags: List[Tag] = []

    class Config:
        from_attributes = True


# Voice Transcription
class TranscribeRequest(BaseModel):
    language: str = Field(default="en")


class TranscribeResponse(BaseModel):
    text: str
    duration: Optional[float] = None
    language: Optional[str] = None


# Search
class SearchRequest(BaseModel):
    query: str
    tag_filter: Optional[List[str]] = None
    limit: int = Field(default=10, le=100)


class SearchResult(BaseModel):
    note: Note
    score: float
    highlights: List[str] = []
