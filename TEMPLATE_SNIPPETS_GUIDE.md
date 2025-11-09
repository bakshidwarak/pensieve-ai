# Template/Snippet System - User Guide

## What is it?

A **TextMate-style snippet system** that lets you quickly insert templates into your notes by typing a trigger word and pressing Tab.

## Quick Start

### 1. Using Templates in Notes

1. Open a note
2. Type a trigger word (e.g., `meet`, `todo`, `feed`)
3. Press **Tab** to expand the template
4. The template content will be inserted automatically

### 2. Default Templates

The system comes with 8 pre-built templates:

| Trigger | Label | Description |
|---------|-------|-------------|
| `meet` | Meeting Notes | Full meeting notes with agenda, discussion, action items |
| `todo` | Todo Item | Task template with priority and checklist |
| `feed` | Feedback | Feedback template (giving or receiving) |
| `doc` | Document | General document template |
| `oneonone` | 1:1 Meeting | One-on-one meeting template |
| `standup` | Daily Standup | Daily standup/scrum notes |
| `retro` | Retrospective | Sprint/project retrospective |
| `decision` | Decision Record | Decision documentation template |

### 3. How It Works

**Example:**

```
Type: meet
Press: Tab
Result: ↓
```

```markdown
## Meeting:
**Date:** 2025-11-09
**Attendees:**

### Agenda
-

### Discussion
-

### Action Items
- [ ]

### Next Steps
-

### Notes

```

## Features

### ✓ Auto-complete Suggestions

As you type, you'll see matching templates appear in a popup:

```
Typing: "me"
Shows: [meet] Meeting Notes
       [standup] Daily Standup (if "me" partially matches)
```

### ✓ Smart Variable Replacement

Templates use `{{variable}}` syntax for placeholders:

- `{{date}}` → Automatically filled with today's date
- `{{time}}` → Automatically filled with current time
- `{{title}}`, `{{name}}`, etc. → Left blank for you to fill

### ✓ Nested Snippets

You can use snippets **inside** other notes:

```markdown
## Meeting: Product Review

<!-- During the meeting, insert a todo -->
Type: todo + Tab

<!-- During the meeting, add feedback -->
Type: feed + Tab
```

This allows you to:
- Add todos within meeting notes
- Insert feedback within documents
- Mix and match templates as needed

## Creating Custom Templates

### Via UI (Coming Soon)

1. Go to Templates page (will be added to navigation)
2. Click **+ New Template**
3. Fill in:
   - **Trigger**: Short word to type (e.g., `standup`, `review`)
   - **Label**: Display name
   - **Category**: Optional grouping (meeting, task, document)
   - **Content**: Template text with `{{placeholders}}`

### Via API

```bash
curl -X POST http://localhost:8000/api/templates/ \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "review",
    "label": "Code Review",
    "category": "document",
    "content": "## Code Review: {{title}}\n**Reviewer:** {{reviewer}}\n\n### Changes\n-\n\n### Feedback\n-"
  }'
```

## API Endpoints

### Get All Templates
```
GET /api/templates/
```

### Get Template by Trigger
```
GET /api/templates/trigger/meet
```

### Create Template
```
POST /api/templates/
Body: { trigger, label, content, ... }
```

### Update Template
```
PUT /api/templates/{id}
Body: { content, ... }
```

### Delete Template
```
DELETE /api/templates/{id}
```

**Note:** System templates cannot be deleted or modified.

## Tips & Tricks

### 1. Use Descriptive Triggers

Good: `meet`, `oneonone`, `retro`
Bad: `m`, `o`, `r` (too short, hard to remember)

### 2. Leverage Variables

```markdown
## {{title}}
**Author:** {{author}}
**Date:** {{date}}
```

Variables make templates more flexible and reusable.

### 3. Create Templates for Recurring Tasks

If you write the same structure repeatedly:
- Create a template for it
- Save time and maintain consistency

### 4. Combine Templates

```markdown
## Meeting: Sprint Planning

Type: retro + Tab
<!-- Adds retrospective section -->

Type: todo + Tab
<!-- Adds action items -->
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Expand template at cursor |
| `Esc` | Close suggestion popup |

## Technical Details

### Template Syntax

- **Placeholders:** `{{variable_name}}`
- **Auto-filled:** `{{date}}`, `{{time}}`, `{{datetime}}`
- **Manual fill:** Any other `{{custom}}` placeholder

### Storage

- **System templates:** Pre-defined, cannot be deleted
- **User templates:** Stored in database, fully manageable
- **Database:** SQLite (`templates` table)

### Frontend Integration

- **Hook:** `useTemplateExpansion`
- **Component:** Integrated into `NoteEditor`
- **Suggestions:** Real-time as you type

## Examples

### Example 1: Quick Meeting Notes

```
1. Create new note
2. Type: meet [Tab]
3. Fill in:
   - Title: "Product Sync"
   - Attendees: "Alice, Bob, Charlie"
4. Add agenda items
5. Save
```

### Example 2: Add Todo Within Note

```
You're in a note about "Project X"

Type: todo [Tab]

Result:
## TODO:
**Due:**
**Priority:**

### Description

### Checklist
- [ ]
```

### Example 3: Create Custom Template

```
Trigger: "weekly"
Label: "Weekly Update"
Content:
# Week of {{date}}

## Accomplishments
-

## Challenges
-

## Next Week
-
```

## Troubleshooting

### Template not expanding?

1. Make sure you're pressing `Tab` (not Enter)
2. Check that the trigger word matches exactly
3. Verify templates are loaded (check API: `/api/templates/`)

### Suggestions not showing?

1. Templates load on component mount
2. Check browser console for errors
3. Verify backend is running

### Can't delete template?

- System templates are protected
- Only user-created templates can be deleted

## Future Enhancements

- [ ] Template variables with default values
- [ ] Multi-cursor editing after expansion
- [ ] Template import/export
- [ ] Template categories/folders
- [ ] Template sharing
- [ ] Snippet marketplace

---

**Questions?** Check `/api/docs` for full API documentation.
