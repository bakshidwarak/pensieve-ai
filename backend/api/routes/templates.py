"""API routes for template/snippet management."""

import re
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.models import Template
from backend.api.schemas.templates import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateExpand,
    TemplateExpandResponse,
)

router = APIRouter()


def expand_template_content(content: str, values: dict[str, str]) -> str:
    """Expand template content by replacing {{placeholders}} with values.

    Args:
        content: Template content with {{placeholder}} syntax
        values: Dictionary mapping placeholder names to values

    Returns:
        Expanded content with placeholders replaced
    """
    result = content

    # Find all placeholders in the format {{variable_name}}
    placeholders = re.findall(r'\{\{(\w+)\}\}', content)

    for placeholder in placeholders:
        if placeholder in values:
            # Replace with provided value
            result = result.replace(f"{{{{{placeholder}}}}}", values[placeholder])
        else:
            # Leave placeholder blank or keep it for user to fill
            result = result.replace(f"{{{{{placeholder}}}}}", "")

    return result


@router.get("/", response_model=List[TemplateResponse])
def get_templates(
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get all templates, optionally filtered by category."""
    query = db.query(Template)

    if category:
        query = query.filter(Template.category == category)

    templates = query.order_by(Template.trigger).all()
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific template by ID."""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.get("/trigger/{trigger}", response_model=TemplateResponse)
def get_template_by_trigger(trigger: str, db: Session = Depends(get_db)):
    """Get a template by its trigger word (e.g., 'meet', 'todo')."""
    template = db.query(Template).filter(Template.trigger == trigger).first()

    if not template:
        raise HTTPException(status_code=404, detail=f"Template with trigger '{trigger}' not found")

    return template


@router.post("/", response_model=TemplateResponse, status_code=201)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new template."""
    # Check if trigger already exists
    existing = db.query(Template).filter(Template.trigger == template.trigger).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Template with trigger '{template.trigger}' already exists"
        )

    # Extract variables from content
    if template.variables is None:
        # Auto-detect variables in {{placeholder}} format
        variables = list(set(re.findall(r'\{\{(\w+)\}\}', template.content)))
    else:
        variables = template.variables

    new_template = Template(
        trigger=template.trigger,
        label=template.label,
        description=template.description,
        content=template.content,
        category=template.category,
        variables=variables,
        is_system=False,
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing template (including system templates)."""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update fields
    update_data = template_update.model_dump(exclude_unset=True)

    # If content is being updated, re-extract variables
    if "content" in update_data and template_update.variables is None:
        variables = list(set(re.findall(r'\{\{(\w+)\}\}', template_update.content)))
        update_data["variables"] = variables

    for field, value in update_data.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)

    return template


@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a template."""
    template = db.query(Template).filter(Template.id == template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Don't allow deleting system templates
    if template.is_system:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete system templates"
        )

    db.delete(template)
    db.commit()

    return None


@router.post("/expand", response_model=TemplateExpandResponse)
def expand_template(expand_request: TemplateExpand, db: Session = Depends(get_db)):
    """Expand a template with provided variable values."""
    template = db.query(Template).filter(Template.id == expand_request.template_id).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Expand template content
    expanded_content = expand_template_content(template.content, expand_request.values)

    return TemplateExpandResponse(
        content=expanded_content,
        trigger=template.trigger,
        label=template.label,
    )
