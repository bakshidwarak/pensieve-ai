## Five Minute Video Walkthrough
https://www.loom.com/share/f45f275a13b24ec697607012fd0c5dc3?sid=20ba1187-aa3c-411c-9072-84089d56c5d4

## Document answering all the questions and more details on implementation
https://docs.google.com/document/d/15-LHyjBfPID2ZweqVV3LsumrSmDaro4XNGr1siUDYG0/edit?usp=sharing

<img width="1400" height="700" alt="image" src="https://github.com/user-attachments/assets/fe8bb093-31d2-4b19-a221-4c7c4af4f7e8" />




# Pensieve AI - IDE for Leaders

Pensieve AI is an intelligent notepad-style text editor designed specifically for leaders and managers. It combines automatic template expansion with AI-powered chat capabilities, making it easy to create structured notes, manage documents, and get intelligent insights from your content.

## Features

### Notepad-style Interface
- **Continuous Typing**: Write freely like in a notepad
- **Auto-expansion**: Keywords automatically expand into structured templates
- **TextMate-style Snippets**: Instant template expansion with placeholder variables
- **Auto-save**: Content is automatically saved to browser storage
- **Real-time Stats**: Word and character count in the header

### AI-Powered Features
- **Intelligent Chat**: Ask questions about your documents and get AI-powered responses
- **Document Processing**: Automatically ingest and vectorize your content
- **Semantic Search**: Find relevant information using natural language queries
- **Template Management**: Create, edit, and manage custom templates
- **API Key Management**: Secure settings for OpenAI API integration

### Built-in Templates
- **`meet`** - Meeting notes with attendees, agenda, and follow-ups
- **`interview`** - Interview notes with candidate evaluation
- **`feedback`** - Structured feedback sessions
- **`todo`** - Task management with priorities and due dates
- **`project`** - Project tracking with objectives and risks
- **`decision`** - Decision-making process with options and criteria
- **`people`** - People management and development tracking
- **`stakeholder`** - Stakeholder analysis and engagement strategies
- **`doc`** - Document creation template
- **`note`** - Quick note template
- **`idea`** - Idea capture template

### Template System
- **Text-based Templates**: Clean, readable template format similar to TextMate
- **Placeholder Variables**: Use `$1`, `$2`, etc. for template variables
- **Auto-timestamps**: Automatic date/time insertion
- **Structured Format**: Organized sections with clear boundaries

### IDE-like Experience
- **Dark Theme**: Professional dark interface with monospace fonts
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Responsive Design**: Works on all device sizes
- **Help Panel**: Toggle help panel to see available templates

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- Python 3.11
- Qdrant (vector database)
- OpenAI API key

### Frontend Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start Qdrant (vector database):
   ```bash
   docker run --name qdrant -p 6333:6333 -p 6334:6334 -d qdrant/qdrant
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 3001 --reload
   ```

6. Configure your OpenAI API key in the settings UI (⚙️ button in the app)

## Tech Stack

### Frontend
- **React** with TypeScript
- **CSS** for styling
- **Local Storage** for persistence

### Backend
- **Python 3.11** with FastAPI
- **Pydantic** for data validation
- **SQLite** for template storage
- **Qdrant** for vector database
- **OpenAI API** for embeddings and chat
- **LangChain** for AI integration

### AI Features
- **RAG (Retrieval Augmented Generation)** for intelligent responses
- **Semantic Search** using vector embeddings
- **Document Processing** with automatic chunking
- **Template Management** with CRUD operations

## Usage

### How It Works
1. **Start typing**: Begin writing in the text editor like a normal notepad
2. **Use templates**: Either click on template buttons in the help panel OR type keywords like `meet`, `todo`, `interview`, etc. and press **Tab** to expand them
3. **Navigate with Tab**: After template expansion, press **Tab** to navigate between placeholder fields (just like TextMate snippets!)
4. **Fill in details**: The cursor automatically focuses on the first field, then use **Tab** to move to the next field
5. **Continue writing**: Keep typing and use more templates as needed

### Available Templates
- `meet` - Meeting notes template
- `note` - Quick note template
- `by` - By template
- `feed` - Feedback template
- `ai` - Todo template
- `w` - With template
- `ref` - Reference template
- `interview` - Interview notes template  
- `project` - Project management template
- `decision` - Decision-making template
- `people` - People management template
- `stakeholder` - Stakeholder management template
- `doc` - Document template
- `idea` - Idea capture template

### Keyboard Shortcuts
- **Tab** - Expand template (when cursor is after a keyword) or navigate between tab stops
- **Esc** - Clear tab stops and exit navigation mode
- **Ctrl+S** - Save (content is auto-saved)
- **Ctrl+?** - Toggle help panel

### TextMate-style Tab Stops
Just like [TextMate snippets](https://macromates.com/manual/en/snippets), Pensieve uses `$1`, `$2`, etc. as tab stops:
- After template expansion, cursor automatically focuses on `$1`
- Press **Tab** to move to `$2`, then `$3`, etc.
- Press **Esc** to exit tab stop navigation
- Placeholders with default values are automatically selected for easy replacement

### Example Usage
Type `meet` and press **Tab** (or click the meet button), and it expands to:
```
[MEETING]
Title : $1
Time: 12/7/2023, 2:30:00 PM
Attendees: $2,$YOURS_TRULY
Notes:
[NOTE]
$3
[ENDNOTE]
[ENDMEETING]$4
```

The cursor will be positioned at the first `$1` placeholder, ready for you to type the meeting title! Press **Tab** to move to the next field.

Try other templates like:
- `note` → `[NOTE] $1 [ENDNOTE]$2`
- `by` → `BY [$1] $2`
- `feed` → `[FEEDBACK] FOR [$1] FROM [$2] $3`
- `ai` → `12/7/2023 [TODO] $1`

## Technology Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **CSS3** - Custom styling with modern features
- **Local Storage** - Data persistence in browser

## Browser Support

Pensieve works in all modern browsers including:
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing

This is a personal project for leadership productivity. Feel free to fork and customize for your own needs.

## License

MIT License - feel free to use and modify as needed.
