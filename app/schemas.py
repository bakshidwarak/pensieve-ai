from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NoteCreate(BaseModel):
    text: str
    tags: Optional[List[str]] = []
    metadata: Optional[dict] = {}

class NoteOut(BaseModel):
    id: str
    text: str
    tags: List[str]
    metadata: Optional[dict]
    created_at: datetime

class ChatRequest(BaseModel):
    query: str
    top_k: int = 4
    tag_filters: Optional[List[str]] = None
