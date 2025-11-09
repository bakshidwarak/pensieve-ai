# Pensieve - IDE for Leaders

Pensieve is a notepad-style text editor designed specifically for leaders and managers. It provides automatic template expansion when you type specific keywords, making it easy to quickly create structured notes and documents.

## Features

### Notepad-style Interface
- **Continuous Typing**: Write freely like in a notepad
- **Auto-expansion**: Keywords automatically expand into structured templates
- **TextMate-style Snippets**: Instant template expansion with placeholder variables
- **Auto-save**: Content is automatically saved to browser storage
- **Real-time Stats**: Word and character count in the header

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

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

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
