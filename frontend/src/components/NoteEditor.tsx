import { useState, useEffect, useRef } from 'react'
import { Note, NoteUpdate } from '../types/notes'
import VoiceRecorder from './VoiceRecorder'
import FileUploader from './FileUploader'
import { useTemplateExpansion } from '../hooks/useTemplateExpansion'
import { Template } from '../services/templatesApi'
import './NoteEditor.css'

interface NoteEditorProps {
  note: Note | null
  onUpdate: (id: number, update: NoteUpdate) => Promise<void>
  onRefresh: () => void
}

function NoteEditor({ note, onUpdate, onRefresh }: NoteEditorProps) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [newTag, setNewTag] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [showVoiceRecorder, setShowVoiceRecorder] = useState(false)
  const [showFileUploader, setShowFileUploader] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [suggestions, setSuggestions] = useState<Template[]>([])
  const [tabStops, setTabStops] = useState<number[]>([])
  const [currentTabStopIndex, setCurrentTabStopIndex] = useState(0)

  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { handleTabExpansion, getSuggestions } = useTemplateExpansion()

  useEffect(() => {
    if (note) {
      setTitle(note.title)
      setContent(note.content)
      setTags(note.tags.map(t => t.name))
    } else {
      setTitle('')
      setContent('')
      setTags([])
    }
  }, [note])

  const handleSave = async () => {
    if (!note) return

    setIsSaving(true)
    try {
      await onUpdate(note.id, {
        title,
        content,
        tag_names: tags,
      })
    } catch (error) {
      console.error('Failed to save note:', error)
      alert('Failed to save note')
    } finally {
      setIsSaving(false)
    }
  }

  const handleAddTag = () => {
    if (newTag && !tags.includes(newTag)) {
      setTags([...tags, newTag])
      setNewTag('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove))
  }

  const handleTranscriptionComplete = (text: string) => {
    setContent(content + '\n\n' + text)
    setShowVoiceRecorder(false)
  }

  const handleFileUploaded = () => {
    setShowFileUploader(false)
    onRefresh()
  }

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value
    const oldContent = content
    const cursorPosition = e.target.selectionStart
    const oldCursorPosition = e.target.selectionEnd - (newContent.length - oldContent.length)

    setContent(newContent)

    // If we have active tab stops, adjust their positions based on content changes
    if (tabStops.length > 0) {
      const lengthDiff = newContent.length - oldContent.length

      if (lengthDiff !== 0) {
        // Text was added or removed - adjust tab stops that come at or after the edit point
        // When typing, if we're at a tab stop, we want to move it forward
        const editPosition = cursorPosition - Math.max(0, lengthDiff)

        // Check if we're typing at any tab stop
        const typingAtTabStop = tabStops.some((pos, idx) => idx === currentTabStopIndex && pos === editPosition)

        const adjustedTabStops = tabStops.map((stopPos, index) => {
          const isCurrentTabStop = index === currentTabStopIndex && stopPos === editPosition

          // If we're typing at the current tab stop, ONLY move that specific tab stop
          if (isCurrentTabStop) {
            return stopPos + lengthDiff
          }

          // If we're typing at a tab stop, don't adjust any other tab stops
          if (typingAtTabStop) {
            return stopPos
          }

          // Otherwise, adjust tab stops that come after the edit position
          if (stopPos > editPosition) {
            return stopPos + lengthDiff
          }

          return stopPos
        })

        setTabStops(adjustedTabStops)
      }
    }

    // Check for template suggestions as user types
    const textBeforeCursor = newContent.substring(0, cursorPosition)
    const match = textBeforeCursor.match(/(\w+)$/)

    if (match) {
      const trigger = match[1]
      const matchingSuggestions = getSuggestions(trigger)

      if (matchingSuggestions.length > 0) {
        setSuggestions(matchingSuggestions)
        setShowSuggestions(true)
      } else {
        setShowSuggestions(false)
      }
    } else {
      setShowSuggestions(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const textarea = textareaRef.current
    if (!textarea) return

    // Handle Tab key for template expansion or tab stop navigation
    if (e.key === 'Tab') {
      e.preventDefault()

      // If we have active tab stops, navigate to next one
      if (tabStops.length > 0 && currentTabStopIndex < tabStops.length) {
        const nextStopIndex = currentTabStopIndex + 1
        if (nextStopIndex < tabStops.length) {
          // Move to next tab stop
          const nextPosition = tabStops[nextStopIndex]
          setCurrentTabStopIndex(nextStopIndex)
          setTimeout(() => {
            textarea.selectionStart = nextPosition
            textarea.selectionEnd = nextPosition
            textarea.focus()
          }, 0)
        } else {
          // No more tab stops, clear them
          setTabStops([])
          setCurrentTabStopIndex(0)
        }
        return
      }

      // Otherwise, try to expand a template
      const cursorPosition = textarea.selectionStart
      const result = handleTabExpansion(content, cursorPosition)

      if (result) {
        // Expand template
        setContent(result.content)
        setShowSuggestions(false)
        setTabStops(result.tabStops)
        setCurrentTabStopIndex(0)

        // Set cursor position after expansion (first tab stop)
        setTimeout(() => {
          textarea.selectionStart = result.newCursorPosition
          textarea.selectionEnd = result.newCursorPosition
          textarea.focus()
        }, 0)
      }
    }

    // Handle Escape to close suggestions or clear tab stops
    if (e.key === 'Escape') {
      setShowSuggestions(false)
      setTabStops([])
      setCurrentTabStopIndex(0)
    }
  }

  if (!note) {
    return (
      <div className="note-editor-empty">
        <div className="empty-state">
          <p>Select a note to edit or create a new one</p>
        </div>
      </div>
    )
  }

  return (
    <div className="note-editor">
      {/* Toolbar */}
      <div className="editor-toolbar">
        <div className="toolbar-left">
          <button
            className="toolbar-btn"
            onClick={() => setShowVoiceRecorder(!showVoiceRecorder)}
            title="Voice input"
          >
            🎤 Voice
          </button>
          <button
            className="toolbar-btn"
            onClick={() => setShowFileUploader(!showFileUploader)}
            title="Attach file"
          >
            📎 Attach
          </button>
        </div>
        <div className="toolbar-right">
          <span className="save-status">
            {isSaving ? 'Saving...' : 'All changes saved'}
          </span>
          <button
            className="save-btn"
            onClick={handleSave}
            disabled={isSaving}
          >
            Save
          </button>
        </div>
      </div>

      {/* Voice Recorder */}
      {showVoiceRecorder && (
        <div className="tool-panel">
          <VoiceRecorder onTranscriptionComplete={handleTranscriptionComplete} />
        </div>
      )}

      {/* File Uploader */}
      {showFileUploader && note && (
        <div className="tool-panel">
          <FileUploader noteId={note.id} onUploadComplete={handleFileUploaded} />
        </div>
      )}

      {/* Title Input */}
      <input
        type="text"
        className="title-input"
        placeholder="Note title..."
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onBlur={handleSave}
      />

      {/* Tags */}
      <div className="tags-section">
        <div className="tags-list">
          {tags.map((tag) => (
            <span key={tag} className="tag">
              {tag}
              <button
                className="tag-remove"
                onClick={() => handleRemoveTag(tag)}
              >
                ×
              </button>
            </span>
          ))}
          <input
            type="text"
            className="tag-input"
            placeholder="Add tag..."
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                handleAddTag()
              }
            }}
          />
        </div>
      </div>

      {/* Content Textarea */}
      <div className="content-container">
        <textarea
          ref={textareaRef}
          className="content-textarea"
          placeholder="Start typing your note... (Try typing 'meet' and pressing Tab)"
          value={content}
          onChange={handleContentChange}
          onKeyDown={handleKeyDown}
          onBlur={handleSave}
        />

        {/* Template Suggestions */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="template-suggestions">
            <div className="suggestions-header">
              Templates (Press Tab to expand)
            </div>
            {suggestions.map((template) => (
              <div key={template.id} className="suggestion-item">
                <span className="suggestion-trigger">{template.trigger}</span>
                <span className="suggestion-label">{template.label}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Attachments */}
      {note.attachments && note.attachments.length > 0 && (
        <div className="attachments-section">
          <h4>Attachments</h4>
          <div className="attachments-list">
            {note.attachments.map((attachment) => (
              <div key={attachment.id} className="attachment-item">
                <span className="attachment-icon">📄</span>
                <span className="attachment-name">{attachment.filename}</span>
                <span className="attachment-size">
                  {(attachment.file_size / 1024).toFixed(1)} KB
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="editor-footer">
        <span className="metadata">
          Created: {new Date(note.created_at).toLocaleDateString()}
        </span>
        <span className="metadata">
          Updated: {new Date(note.updated_at).toLocaleString()}
        </span>
      </div>
    </div>
  )
}

export default NoteEditor
