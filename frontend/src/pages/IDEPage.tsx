import { useState, useEffect } from 'react'
import NotesSidebar from '../components/NotesSidebar'
import NoteEditor from '../components/NoteEditor'
import ChatInterface from '../components/ChatInterface'
import TemplateManager from '../components/TemplateManager'
import { useNotes } from '../hooks/useNotes'
import { useChat } from '../hooks/useChat'
import './IDEPage.css'

function IDEPage() {
  const { notes, selectedNote, selectNote, createNote, updateNote, deleteNote, refreshNotes } = useNotes()
  const { messages, sendMessage, isLoading } = useChat(true) // use_notes=true
  const [showChat, setShowChat] = useState(true)
  const [showTemplates, setShowTemplates] = useState(false)

  useEffect(() => {
    refreshNotes()
  }, [])

  return (
    <div className="ide-page">
      {/* Header */}
      <header className="ide-header">
        <div className="header-left">
          <h1 className="logo">Pensieve.ai</h1>
          <span className="subtitle">IDE for Leaders</span>
        </div>
        <div className="header-right">
          <button
            className="templates-btn"
            onClick={() => setShowTemplates(true)}
            title="Manage Templates"
          >
            📝 Templates
          </button>
          <button
            className="toggle-chat-btn"
            onClick={() => setShowChat(!showChat)}
          >
            {showChat ? 'Hide Chat' : 'Show Chat'}
          </button>
        </div>
      </header>

      {/* 3-Panel Layout */}
      <div className="ide-container">
        {/* Left Panel - Notes Sidebar */}
        <aside className="sidebar-panel">
          <NotesSidebar
            notes={notes}
            selectedNoteId={selectedNote?.id}
            onSelectNote={selectNote}
            onCreateNote={createNote}
            onDeleteNote={deleteNote}
            onRefresh={refreshNotes}
          />
        </aside>

        {/* Middle Panel - Note Editor */}
        <main className="editor-panel">
          <NoteEditor
            note={selectedNote}
            onUpdate={updateNote}
            onRefresh={refreshNotes}
          />
        </main>

        {/* Right Panel - Chat */}
        {showChat && (
          <aside className="chat-panel">
            <div className="chat-header">
              <h3>Chat with Notes</h3>
              <p>Ask questions about your notes</p>
            </div>
            <ChatInterface
              messages={messages}
              onSendMessage={sendMessage}
              isLoading={isLoading}
            />
          </aside>
        )}
      </div>

      {/* Template Manager Modal */}
      {showTemplates && (
        <div className="template-modal-overlay" onClick={() => setShowTemplates(false)}>
          <div className="template-modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setShowTemplates(false)}>×</button>
            <TemplateManager />
          </div>
        </div>
      )}
    </div>
  )
}

export default IDEPage
