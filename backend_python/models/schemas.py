from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Template schemas
class TemplateBase(BaseModel):
    name: str
    shortcut: str
    description: str
    icon: str
    template: str

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    shortcut: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    template: Optional[str] = None

class Template(TemplateBase):
    id: str
    is_builtin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# RAG schemas
class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    sources: Optional[Dict[str, int]] = None
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class DocumentIngestRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentIngestResponse(BaseModel):
    success: bool
    message: str
    chunk_count: Optional[int] = None
    backup_path: Optional[str] = None
    error: Optional[str] = None

class ClearAndIngestRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class StatsResponse(BaseModel):
    success: bool
    vector_db: Optional[Dict[str, Any]] = None
    backup_files: Optional[int] = None
    pending_documents: Optional[int] = None
    is_processing: Optional[bool] = None
    error: Optional[str] = None

# Agent schemas
class AgentAnalysis(BaseModel):
    needs_meeting_search: bool
    needs_web_search: bool
    search_strategy: str
    priority: str

class SearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    relevance: float
    source: str

class WebSearchResult(BaseModel):
    title: str
    content: str
    url: str
    source: str
    relevance: float

