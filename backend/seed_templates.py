"""Seed database with default system templates."""

from backend.core.database import SessionLocal
from backend.core.models import Template
from datetime import datetime


DEFAULT_TEMPLATES = [
    {
        "trigger": "meet",
        "label": "Meeting Notes",
        "description": "Template for meeting notes with agenda, discussion, and action items",
        "category": "meeting",
        "content": """## Meeting: {{title}}
**Date:** {{date}}
**Attendees:** {{attendees}}

### Agenda
-

### Discussion
-

### Action Items
- [ ]

### Next Steps
-

### Notes
""",
        "variables": ["title", "date", "attendees"],
    },
    {
        "trigger": "todo",
        "label": "Todo Item",
        "description": "Simple todo/task template",
        "category": "task",
        "content": """## TODO: {{title}}
**Due:** {{due_date}}
**Priority:** {{priority}}

### Description
{{description}}

### Checklist
- [ ]

### Notes
""",
        "variables": ["title", "due_date", "priority", "description"],
    },
    {
        "trigger": "feed",
        "label": "Feedback",
        "description": "Feedback template for giving or receiving feedback",
        "category": "feedback",
        "content": """## Feedback: {{subject}}
**From:** {{from}}
**To:** {{to}}
**Date:** {{date}}

### Context
{{context}}

### What Went Well
-

### Areas for Improvement
-

### Action Items
- [ ]

### Additional Notes
""",
        "variables": ["subject", "from", "to", "date", "context"],
    },
    {
        "trigger": "doc",
        "label": "Document",
        "description": "General document template",
        "category": "document",
        "content": """# {{title}}
**Author:** {{author}}
**Date:** {{date}}
**Status:** {{status}}

## Overview
{{overview}}

## Details


## References


## Notes
""",
        "variables": ["title", "author", "date", "status", "overview"],
    },
    {
        "trigger": "oneonone",
        "label": "1:1 Meeting",
        "description": "One-on-one meeting template",
        "category": "meeting",
        "content": """## 1:1: {{name}}
**Date:** {{date}}

### Their Topics
-

### My Topics
-

### Discussion Notes
-

### Action Items
- [ ]

### Follow-up for Next Time
-
""",
        "variables": ["name", "date"],
    },
    {
        "trigger": "standup",
        "label": "Daily Standup",
        "description": "Daily standup/scrum notes",
        "category": "meeting",
        "content": """## Daily Standup - {{date}}

### Yesterday
-

### Today
-

### Blockers
-

### Notes
""",
        "variables": ["date"],
    },
    {
        "trigger": "retro",
        "label": "Retrospective",
        "description": "Sprint/project retrospective template",
        "category": "meeting",
        "content": """## Retrospective: {{sprint_name}}
**Date:** {{date}}
**Participants:** {{participants}}

### What Went Well
-

### What Didn't Go Well
-

### What We Learned
-

### Action Items
- [ ]

### Appreciations
-
""",
        "variables": ["sprint_name", "date", "participants"],
    },
    {
        "trigger": "decision",
        "label": "Decision Record",
        "description": "Template for documenting decisions",
        "category": "document",
        "content": """## Decision: {{title}}
**Date:** {{date}}
**Status:** {{status}}
**Deciders:** {{deciders}}

### Context
{{context}}

### Options Considered
1.
2.
3.

### Decision
{{decision}}

### Consequences
**Positive:**
-

**Negative:**
-

**Risks:**
-

### Next Steps
- [ ]
""",
        "variables": ["title", "date", "status", "deciders", "context", "decision"],
    },
]


def seed_templates():
    """Seed database with default templates."""
    db = SessionLocal()

    try:
        # Check if templates already exist
        existing_count = db.query(Template).filter(Template.is_system == True).count()

        if existing_count > 0:
            print(f"Found {existing_count} existing system templates. Skipping seed.")
            return

        print("Seeding default templates...")

        for template_data in DEFAULT_TEMPLATES:
            template = Template(
                **template_data,
                is_system=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(template)

        db.commit()
        print(f"Successfully seeded {len(DEFAULT_TEMPLATES)} default templates!")

        # Display created templates
        for t in DEFAULT_TEMPLATES:
            print(f"  ✓ {t['trigger']} - {t['label']}")

    except Exception as e:
        print(f"Error seeding templates: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_templates()
