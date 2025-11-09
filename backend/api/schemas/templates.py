"""Pydantic schemas for template/snippet operations."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TemplateBase(BaseModel):
    """Base template schema."""
    trigger: str = Field(..., min_length=1, max_length=50, description="Trigger word (e.g., 'meet', 'todo')")
    label: str = Field(..., min_length=1, max_length=200, description="Display label")
    description: Optional[str] = Field(None, max_length=1000)
    content: str = Field(..., min_length=1, description="Template content with {{placeholders}}")
    category: Optional[str] = Field(None, max_length=100)
    variables: Optional[List[str]] = Field(None, description="List of variable placeholders")


class TemplateCreate(TemplateBase):
    """Schema for creating a new template."""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template."""
    trigger: Optional[str] = Field(None, min_length=1, max_length=50)
    label: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    variables: Optional[List[str]] = None


class TemplateResponse(TemplateBase):
    """Schema for template responses."""
    id: int
    is_system: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateExpand(BaseModel):
    """Schema for expanding a template with variable values."""
    template_id: int
    values: dict[str, str] = Field(..., description="Variable name -> value mapping")


class TemplateExpandResponse(BaseModel):
    """Response after expanding a template."""
    content: str
    trigger: str
    label: str
