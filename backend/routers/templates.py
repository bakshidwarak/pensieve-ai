from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
import sqlite3
import os
import json
from datetime import datetime
import uuid
from pydantic import BaseModel

from models.schemas import Template, TemplateCreate, TemplateUpdate

logger = logging.getLogger(__name__)

router = APIRouter()

# Database setup
DB_PATH = "./data/templates.db"

def get_db_connection():
    """Get database connection"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            shortcut TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT NOT NULL,
            template TEXT NOT NULL,
            is_builtin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert built-in templates if they don't exist
    builtin_templates = [
        {
            "id": "meet",
            "name": "Meeting",
            "shortcut": "meet",
            "description": "Create a meeting template",
            "icon": "📅",
            "template": "[MEETING]\nTitle: $0\nTime: ${new Date().toLocaleString()}\nAttendees: $1,$YOURS_TRULY\nNotes:\n[NOTE]\n$2\n[ENDNOTE]\n[ENDMEETING]",
            "is_builtin": 1
        },
        {
            "id": "todo",
            "name": "Todo",
            "shortcut": "todo",
            "description": "Create a todo template",
            "icon": "✅",
            "template": "[TODO]\n$0\n[ENDTODO]",
            "is_builtin": 1
        },
        {
            "id": "note",
            "name": "Note",
            "shortcut": "note",
            "description": "Create a note template",
            "icon": "📝",
            "template": "[NOTE]\n$0\n[ENDNOTE]",
            "is_builtin": 1
        }
    ]
    
    for template in builtin_templates:
        cursor.execute("""
            INSERT OR IGNORE INTO templates (id, name, shortcut, description, icon, template, is_builtin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            template["id"], template["name"], template["shortcut"],
            template["description"], template["icon"], template["template"], template["is_builtin"]
        ))
    
    conn.commit()
    conn.close()

# Initialize database on startup
@router.on_event("startup")
async def startup_event():
    init_db()

@router.get("/")
async def get_all_templates():
    """Get all templates"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM templates ORDER BY is_builtin ASC, created_at DESC")
        rows = cursor.fetchall()
        
        templates = []
        for row in rows:
            templates.append(Template(
                id=row["id"],
                name=row["name"],
                shortcut=row["shortcut"],
                description=row["description"],
                icon=row["icon"],
                template=row["template"],
                is_builtin=bool(row["is_builtin"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"])
            ))
        
        conn.close()
        return {"success": True, "data": templates}
        
    except Exception as e:
        logger.error(f"❌ Error getting templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")

@router.get("/{template_id}")
async def get_template_by_id(template_id: str):
    """Get a single template by id"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()

        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Template not found")

        return {"success": True, "data": Template(
            id=row["id"],
            name=row["name"],
            shortcut=row["shortcut"],
            description=row["description"],
            icon=row["icon"],
            template=row["template"],
            is_builtin=bool(row["is_builtin"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting template by id: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template")

@router.post("/")
async def create_template(template: TemplateCreate):
    """Create a new template"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        template_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO templates (id, name, shortcut, description, icon, template, is_builtin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
        """, (
            template_id, template.name, template.shortcut,
            template.description, template.icon, template.template, now, now
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "data": Template(
            id=template_id,
            name=template.name,
            shortcut=template.shortcut,
            description=template.description,
            icon=template.icon,
            template=template.template,
            is_builtin=False,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now)
        )}
        
    except Exception as e:
        logger.error(f"❌ Error creating template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")

@router.put("/{template_id}")
async def update_template(template_id: str, template: TemplateUpdate):
    """Update a template"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        if template.name is not None:
            update_fields.append("name = ?")
            values.append(template.name)
        if template.shortcut is not None:
            update_fields.append("shortcut = ?")
            values.append(template.shortcut)
        if template.description is not None:
            update_fields.append("description = ?")
            values.append(template.description)
        if template.icon is not None:
            update_fields.append("icon = ?")
            values.append(template.icon)
        if template.template is not None:
            update_fields.append("template = ?")
            values.append(template.template)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(template_id)
        
        cursor.execute(f"""
            UPDATE templates 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        
        conn.commit()
        
        # Get updated template
        cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Template not found")
        
        conn.close()
        
        return {"success": True, "data": Template(
            id=row["id"],
            name=row["name"],
            shortcut=row["shortcut"],
            description=row["description"],
            icon=row["icon"],
            template=row["template"],
            is_builtin=bool(row["is_builtin"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating template: {e}")
        raise HTTPException(status_code=500, detail="Failed to update template")

@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        
        conn.commit()
        conn.close()
        
        return {"success": True, "data": {"deleted": True}}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting template: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete template")

@router.post("/{template_id}/copy")
async def create_custom_copy(template_id: str, template: TemplateUpdate):
    """Create a custom copy of a template (built-in or user)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the source template
        cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
        source = cursor.fetchone()
        if not source:
            raise HTTPException(status_code=404, detail="Template not found")

        new_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Use provided overrides or source values
        name = template.name if template.name is not None else source["name"]
        shortcut = template.shortcut if template.shortcut is not None else source["shortcut"]
        description = template.description if template.description is not None else source["description"]
        icon = template.icon if template.icon is not None else source["icon"]
        body = template.template if template.template is not None else source["template"]

        cursor.execute(
            """
            INSERT INTO templates (id, name, shortcut, description, icon, template, is_builtin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (new_id, name, shortcut, description, icon, body, now, now)
        )

        conn.commit()
        conn.close()

        return {"success": True, "data": Template(
            id=new_id,
            name=name,
            shortcut=shortcut,
            description=description,
            icon=icon,
            template=body,
            is_builtin=False,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now)
        )}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating custom copy: {e}")
        raise HTTPException(status_code=500, detail="Failed to create custom copy")

# API Key management models
class ApiKeyRequest(BaseModel):
    api_key: str

class ApiKeyResponse(BaseModel):
    success: bool
    message: str
    has_key: bool = False

# API Key management endpoints
@router.post("/settings/api-key", response_model=ApiKeyResponse)
async def set_api_key(request: ApiKeyRequest):
    """Set OpenAI API key"""
    try:
        # Store API key in environment variable for this session
        os.environ["OPENAI_API_KEY"] = request.api_key
        
        # Also store in a simple config file for persistence
        config_dir = "./data"
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, "config.json")
        
        config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        
        config["openai_api_key"] = request.api_key
        config["updated_at"] = datetime.now().isoformat()
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ API key updated successfully")
        return ApiKeyResponse(
            success=True,
            message="API key saved successfully",
            has_key=True
        )
    except Exception as e:
        logger.error(f"❌ Error setting API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to save API key")

@router.get("/settings/api-key", response_model=ApiKeyResponse)
async def get_api_key_status():
    """Check if API key is set"""
    try:
        # Check environment variable first
        env_key = os.environ.get("OPENAI_API_KEY")
        if env_key and env_key != "test_key":
            return ApiKeyResponse(
                success=True,
                message="API key is set",
                has_key=True
            )
        
        # Check config file
        config_file = "./data/config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                if config.get("openai_api_key"):
                    # Set environment variable from config
                    os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
                    return ApiKeyResponse(
                        success=True,
                        message="API key loaded from config",
                        has_key=True
                    )
        
        return ApiKeyResponse(
            success=True,
            message="No API key set",
            has_key=False
        )
    except Exception as e:
        logger.error(f"❌ Error checking API key: {e}")
        return ApiKeyResponse(
            success=False,
            message="Error checking API key status",
            has_key=False
        )

@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Delete a template by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if template exists and is not built-in
        cursor.execute("SELECT id, is_builtin FROM templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Template not found")
        
        if row["is_builtin"]:
            conn.close()
            raise HTTPException(status_code=400, detail="Cannot delete built-in templates")
        
        # Delete the template
        cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Template not found")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Template {template_id} deleted successfully")
        return {"success": True, "message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting template: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete template")

@router.get("/health")
async def templates_health():
    """Health check for templates router"""
    try:
        # Quick DB check
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(1) as c FROM templates")
        _ = cursor.fetchone()
        conn.close()
        return {"success": True, "message": "Templates API healthy"}
    except Exception as e:
        logger.error(f"❌ Templates health error: {e}")
        raise HTTPException(status_code=500, detail="Templates API not healthy")

