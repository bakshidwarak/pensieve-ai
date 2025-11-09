import { useState } from 'react'
import { NoteList, NoteCreate } from '../types/notes'
import './NotesSidebar.css'

interface NotesSidebarProps {
  notes: NoteList[]
  selectedNoteId?: number
  onSelectNote: (id: number) => void
  onCreateNote: (note: NoteCreate) => Promise<void>
  onDeleteNote: (id: number) => Promise<void>
  onRefresh: () => void
}

function NotesSidebar({
  notes,
  selectedNoteId,
  onSelectNote,
  onCreateNote,
  onDeleteNote,
  onRefresh,
}: NotesSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  const handleCreateNote = async () => {
    setIsCreating(true)
    try {
      await onCreateNote({
        title: 'New Note',
        content: '',
        tag_names: [],
      })
      onRefresh()
    } catch (error) {
      console.error('Failed to create note:', error)
    } finally {
      setIsCreating(false)
    }
  }

  const filteredNotes = notes.filter(
    (note) =>
      note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      note.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      note.tags.some((tag) => tag.name.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <div className="notes-sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <h2>Notes</h2>
        <button className="new-note-btn" onClick={handleCreateNote} disabled={isCreating}>
          +
        </button>
      </div>

      {/* Search */}
      <div className="search-box">
        <input
          type="text"
          placeholder="Search notes..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      {/* Notes List */}
      <div className="notes-list">
        {filteredNotes.length === 0 ? (
          <div className="empty-notes">
            <p>No notes found</p>
            <button className="create-first-btn" onClick={handleCreateNote}>
              Create your first note
            </button>
          </div>
        ) : (
          filteredNotes.map((note) => (
            <div
              key={note.id}
              className={`note-item ${selectedNoteId === note.id ? 'selected' : ''}`}
              onClick={() => onSelectNote(note.id)}
            >
              <div className="note-item-header">
                <h3 className="note-title">{note.title || 'Untitled'}</h3>
                <span className="note-date">
                  {new Date(note.updated_at).toLocaleDateString()}
                </span>
              </div>
              <p className="note-preview">{note.content || 'No content'}</p>
              {note.tags.length > 0 && (
                <div className="note-tags">
                  {note.tags.slice(0, 3).map((tag) => (
                    <span key={tag.id} className="note-tag" style={{ background: tag.color }}>
                      {tag.name}
                    </span>
                  ))}
                  {note.tags.length > 3 && (
                    <span className="note-tag-more">+{note.tags.length - 3}</span>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default NotesSidebar
