import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { processTemplate } from '../types/commands';
import { createNavigableTemplate, TabStop, findTabStopsInContent, getNextTabStop, getCurrentTabStop } from '../utils/tabStops';
import TemplateEditor from './TemplateEditor';
import { templateApi, Template } from '../services/templateApi';
import './NotepadEditor.css';

interface NotepadEditorProps {}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const NotepadEditor: React.FC<NotepadEditorProps> = () => {
  const [content, setContent] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [showHelp, setShowHelp] = useState(true);
  // Tab stops are now tracked dynamically in content, no need for separate state
  const [allTemplates, setAllTemplates] = useState<Template[]>([]);
  const [showTemplateEditor, setShowTemplateEditor] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatInputRef = useRef<HTMLInputElement>(null);
  const chatMessagesRef = useRef<HTMLDivElement>(null);


  useEffect(() => {
    // Load saved content from localStorage
    const savedContent = localStorage.getItem('pensieve-content');
    if (savedContent) {
      setContent(savedContent);
    }

    // Load templates from API
    const loadTemplates = async () => {
      try {
        const response = await templateApi.getAllTemplates();
        if (response.success && response.data) {
          console.log('=== LOADING FROM API ===');
          console.log('Loaded templates:', response.data);
          setAllTemplates(response.data);
        } else {
          console.error('Failed to load templates:', response.error);
        }
      } catch (error) {
        console.error('Error loading templates:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTemplates();
  }, []);

  // Delete template function
  const handleDeleteTemplate = async (templateId: string) => {
    try {
      const response = await templateApi.deleteTemplate(templateId);
      if (response.success) {
        // Reload templates after deletion
        const loadResponse = await templateApi.getAllTemplates();
        if (loadResponse.success && loadResponse.data) {
          setAllTemplates(loadResponse.data);
        }
        console.log('Template deleted successfully');
      } else {
        console.error('Failed to delete template:', response.error);
        alert('Failed to delete template: ' + (response.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error deleting template:', error);
      alert('Error deleting template: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  useEffect(() => {
    // Save content to localStorage whenever it changes
    localStorage.setItem('pensieve-content', content);
  }, [content]);

  // Auto-scroll chat to bottom when new messages are added
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatMessages, isChatLoading]);


  const autoIngestTimeout = useRef<NodeJS.Timeout | null>(null);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    
    // Auto-save to localStorage
    localStorage.setItem('pensieve-content', newContent);
    
    // Auto-vectorize content for RAG (debounced)
    if (newContent.trim().length > 100) {
      if (autoIngestTimeout.current) {
        clearTimeout(autoIngestTimeout.current);
      }
      autoIngestTimeout.current = setTimeout(() => {
        ingestDocument(newContent);
      }, 5000); // Wait 5 seconds after user stops typing
    }
  };

  const ingestDocument = async (content: string) => {
    try {
      await fetch('http://localhost:3001/api/rag/ingest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content,
          metadata: {
            type: 'auto_ingest',
            timestamp: new Date().toISOString()
          }
        }),
      });
    } catch (error) {
      console.error('Auto-ingest error:', error);
    }
  };

  // Clear tab stop markers from content
  const clearTabStopMarkers = () => {
    const cleanedContent = content.replace(/\[Tab Stop \d+\]/g, '');
    setContent(cleanedContent);
  };

  const expandTemplate = (command: any, cursorPos: number) => {
    // Find the start of the word to replace - look for word boundaries
    const beforeCursor = content.substring(0, cursorPos);
    const afterCursor = content.substring(cursorPos);
    
    // Find word boundaries more accurately
    const wordMatch = beforeCursor.match(/(\S+)\s*$/);
    const wordStart = wordMatch ? cursorPos - wordMatch[0].length : cursorPos;
    
    // Process template and create navigable template
    const template = processTemplate(command.template);
    const { content: processedTemplate } = createNavigableTemplate(template);
    
    // Replace the word with the processed template
    const newText = content.substring(0, wordStart) + processedTemplate + afterCursor;
    
    setContent(newText);
    
    // Focus on first tab stop (which will be found dynamically)
    setTimeout(() => {
      const tabStops = findTabStopsInContent(newText);
      if (textareaRef.current && tabStops.length > 0) {
        const firstStop = tabStops[0];
        console.log('=== FOCUSING ON FIRST TAB STOP ===');
        console.log('First stop:', firstStop);
        textareaRef.current.setSelectionRange(firstStop.start, firstStop.end);
        textareaRef.current.focus();
      }
    }, 0);
  };

  const insertTemplate = (command: any) => {
    const cursorPos = textareaRef.current?.selectionStart || 0;
    
    // Process template and create navigable template
    const template = processTemplate(command.template);
    const { content: processedTemplate } = createNavigableTemplate(template);
    
    console.log('=== INSERTING TEMPLATE ===');
    console.log('Command:', command);
    console.log('Original template:', template);
    console.log('Processed template:', processedTemplate);
    console.log('Cursor position:', cursorPos);
    
    // Insert template at cursor position
    const newText = content.substring(0, cursorPos) + processedTemplate + content.substring(cursorPos);
    setContent(newText);
    
    // Focus on first tab stop (which will be found dynamically)
    setTimeout(() => {
      const tabStops = findTabStopsInContent(newText);
      if (textareaRef.current && tabStops.length > 0) {
        const firstStop = tabStops[0];
        console.log('Focusing on first stop:', firstStop);
        textareaRef.current.setSelectionRange(firstStop.start, firstStop.end);
        textareaRef.current.focus();
      }
    }, 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Handle Tab key for tab stop navigation or template expansion
    if (e.key === 'Tab') {
      e.preventDefault();
      
      console.log('=== TAB PRESSED ===');
      console.log('Current content:', content);
      console.log('Cursor position:', e.currentTarget.selectionStart);
      
      // Check for tab stops in current content dynamically
      const currentTabStops = findTabStopsInContent(content);
      console.log('Found tab stops in content:', currentTabStops);
      
      if (currentTabStops.length > 0) {
        const currentPosition = e.currentTarget.selectionStart || 0;
        const currentStop = getCurrentTabStop(content, currentPosition);
        const nextStop = getNextTabStop(content, currentPosition);
        
        console.log('Current stop:', currentStop);
        console.log('Next stop:', nextStop);
        
        if (nextStop) {
          // Move to next tab stop
          setTimeout(() => {
            if (textareaRef.current) {
              textareaRef.current.setSelectionRange(nextStop.start, nextStop.end);
              textareaRef.current.focus();
            }
          }, 0);
        } else {
          // No more tab stops, clear them
          console.log('No more tab stops, clearing markers');
          clearTabStopMarkers();
        }
      } else {
        console.log('No active tab stops, trying to expand template');
        // No active tab stops, try to expand template
        const cursorPos = e.currentTarget.selectionStart;
        const beforeCursor = content.substring(0, cursorPos);
        
        // Find the last word more accurately
        const wordMatch = beforeCursor.match(/(\S+)\s*$/);
        const lastWord = wordMatch ? wordMatch[1].toLowerCase() : '';

        if (lastWord) {
          // Prioritize custom templates over built-in ones, and newest custom templates first
          const command = allTemplates
            .filter(cmd => cmd.shortcut.toLowerCase() === lastWord.toLowerCase())
            .sort((a, b) => {
              // First sort by is_builtin (custom templates first)
              const builtinDiff = Number(a.is_builtin) - Number(b.is_builtin);
              if (builtinDiff !== 0) return builtinDiff;
              
              // If both are custom or both are built-in, sort by created_at (newest first)
              if (a.created_at && b.created_at) {
                return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
              }
              return 0;
            })
            [0]; // Get the first one (newest custom template if available)

          if (command) {
            console.log('=== TEMPLATE EXPANSION ===');
            console.log('Using template:', command.id, command.name, 'is_builtin:', command.is_builtin);
            console.log('Template content:', command.template);
            expandTemplate(command, cursorPos);
          }
        }
      }
    }
    
    // Handle Escape to clear tab stops
    if (e.key === 'Escape') {
      clearTabStopMarkers();
    }
    
    // Handle Ctrl+S for save
    if (e.ctrlKey && e.key === 's') {
      e.preventDefault();
      // Content is auto-saved to localStorage
    }
    
    // Handle Ctrl+? for help
    if (e.ctrlKey && e.key === '?') {
      e.preventDefault();
      setShowHelp(!showHelp);
    }
  };

  const clearContent = () => {
    setContent('');
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const clearAndIngest = async () => {
    if (!content.trim()) {
      alert('No content to ingest');
      return;
    }

    try {
      const response = await fetch('http://localhost:3001/api/rag/clear-and-ingest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content,
          metadata: {
            type: 'user_notes',
            timestamp: new Date().toISOString()
          }
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setContent('');
        alert(`Content ingested successfully! ${data.chunkCount} chunks created.`);
        if (textareaRef.current) {
          textareaRef.current.focus();
        }
      } else {
        alert('Failed to ingest content: ' + data.error);
      }
    } catch (error) {
      console.error('Clear and ingest error:', error);
      alert('Error ingesting content: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  // Chat functions
  const sendChatMessage = async () => {
    if (!chatInput.trim() || isChatLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: chatInput.trim(),
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsChatLoading(true);

    try {
      const response = await fetch('http://localhost:3001/api/rag/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          context: content // Send current notes as context
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: data.response || 'Sorry, I could not process your request.',
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsChatLoading(false);
      // Auto-focus input after response
      setTimeout(() => {
        if (chatInputRef.current) {
          chatInputRef.current.focus();
        }
      }, 100);
    }
  };

  const handleChatKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  // Chat is now always visible, no toggle needed

  const getWordCount = () => {
    return content.trim().split(/\s+/).filter(word => word.length > 0).length;
  };

  const getCharacterCount = () => {
    return content.length;
  };

  // Template management functions
  // No need to separate built-in and custom templates - users can edit all templates

  const handleCreateTemplate = () => {
    setEditingTemplate(null);
    setShowTemplateEditor(true);
  };

  const handleEditTemplate = (template: Template) => {
    console.log('=== EDITING TEMPLATE ===');
    console.log('Template being edited:', template);
    setEditingTemplate(template);
    setShowTemplateEditor(true);
  };

  const handleSaveTemplate = async (template: Omit<Template, 'id' | 'is_builtin' | 'created_at' | 'updated_at'>) => {
    console.log('=== SAVING TEMPLATE ===');
    console.log('Template to save:', template);
    console.log('Currently editing template:', editingTemplate);
    
    try {
      if (editingTemplate) {
        // Update existing template (built-in or custom)
        const response = await templateApi.updateTemplate(editingTemplate.id, template);
        if (response.success && response.data) {
          setAllTemplates(prev => prev.map(t => t.id === editingTemplate.id ? response.data! : t));
        } else {
          console.error('Failed to update template:', response.error);
          alert('Failed to update template: ' + response.error);
          return;
        }
      } else {
        // Add new template
        const response = await templateApi.createTemplate(template);
        if (response.success && response.data) {
          setAllTemplates(prev => [...prev, response.data!]);
        } else {
          console.error('Failed to create template:', response.error);
          alert('Failed to create template: ' + response.error);
          return;
        }
      }
      
      setShowTemplateEditor(false);
      setEditingTemplate(null);
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Error saving template: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };


  const handleCloseTemplateEditor = () => {
    setShowTemplateEditor(false);
    setEditingTemplate(null);
  };

  return (
    <div className="notepad-editor">
      <div className="notepad-header">
        <div className="header-left">
          <span className="app-icon">⚡</span>
          <span className="app-title">Pensieve - IDE for Leaders</span>
        </div>
        <div className="header-right">
          <div className="stats">
            <span className="stat">{getWordCount()} words</span>
            <span className="stat">{getCharacterCount()} characters</span>
          </div>
          <button className="clear-btn" onClick={clearContent} title="Clear all content">
            Clear
          </button>
          <button className="clear-btn" onClick={clearAndIngest} title="Ingest content and clear screen">
            Clean Slate
          </button>
          <button 
            className="help-btn" 
            onClick={() => setShowHelp(!showHelp)}
            title="Toggle help (Ctrl+?)"
          >
            Help
          </button>
        </div>
      </div>

      <div className="notepad-content">
        <div className="main-editor-area">
          {showHelp && (
            <div className="help-panel">
              <div className="help-content">
                <div className="help-header">
                  <h3>Quick Templates</h3>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button 
                      className="create-template-btn"
                      onClick={handleCreateTemplate}
                      title="Create new template"
                    >
                      + New Template
                    </button>
                  <button 
                    className="create-template-btn"
                    onClick={async () => {
                      console.log('Testing API connection...');
                      try {
                        // Test direct fetch first
                        const directResponse = await fetch('http://localhost:3001/api/health');
                        const directData = await directResponse.json();
                        console.log('Direct fetch response:', directData);
                        
                        // Test API service
                        const response = await templateApi.healthCheck();
                        console.log('API service response:', response);
                        
                        alert(`Direct: ${directResponse.ok ? 'OK' : 'Failed'}\nAPI Service: ${response.success ? 'OK' : 'Failed'}`);
                      } catch (error) {
                        console.error('Test failed:', error);
                        alert('Test failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
                      }
                    }}
                    title="Test API connection"
                    style={{ backgroundColor: '#7c3aed', fontSize: '0.7rem' }}
                  >
                    Test API
                  </button>
                  <button 
                    className="create-template-btn"
                    onClick={async () => {
                      console.log('Testing template creation...');
                      try {
                        const testTemplate = {
                          name: 'Quick Test',
                          shortcut: 'quicktest',
                          description: 'Quick test template',
                          icon: '⚡',
                          template: '[TEST]\n$1\n[ENDTEST]$0'
                        };
                        
                        const response = await templateApi.createTemplate(testTemplate);
                        console.log('Create template response:', response);
                        
                        if (response.success) {
                          alert('Template created successfully!');
                          // Reload templates
                          const reloadResponse = await templateApi.getAllTemplates();
                          if (reloadResponse.success && reloadResponse.data) {
                            setAllTemplates(reloadResponse.data);
                          }
                        } else {
                          alert('Failed to create template: ' + response.error);
                        }
                      } catch (error) {
                        console.error('Template creation failed:', error);
                        alert('Template creation failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
                      }
                    }}
                    title="Test template creation"
                    style={{ backgroundColor: '#f59e0b', fontSize: '0.7rem' }}
                  >
                    Test Create
                  </button>
                </div>
              </div>
              <p>Click any template to insert it, or type the keyword and press Tab:</p>
              
              {loading ? (
                <div className="loading-message">Loading templates...</div>
              ) : (
                <>
                  {allTemplates.length > 0 && (
                    <div className="template-section">
                      <h4>Templates</h4>
                      <div className="template-list">
                        {allTemplates.map(template => (
                          <div 
                            key={template.id} 
                            className="template-item"
                            onClick={() => insertTemplate(template)}
                            title={`Click to insert ${template.shortcut} template`}
                          >
                            <span className="template-icon">{template.icon}</span>
                            <span className="template-name">{template.shortcut}</span>
                            <span className="template-desc">{template.description}</span>
                            <div className="template-actions">
                              <button 
                                className="edit-template-btn"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleEditTemplate(template);
                                }}
                                title="Edit template"
                              >
                                ✏️
                              </button>
                              {!template.is_builtin && (
                                <button 
                                  className="delete-template-btn"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    if (window.confirm(`Are you sure you want to delete "${template.name}"?`)) {
                                      handleDeleteTemplate(template.id);
                                    }
                                  }}
                                  title="Delete template"
                                >
                                  🗑️
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
              <div className="help-shortcuts">
                <p><kbd>Tab</kbd> - Expand template or navigate tab stops</p>
                <p><kbd>Esc</kbd> - Clear tab stops</p>
                <p><kbd>Ctrl+S</kbd> - Save (auto-saved)</p>
                <p><kbd>Ctrl+?</kbd> - Toggle help</p>
              </div>
            </div>
          </div>
        )}

          <div className="editor-container">
            <textarea
              ref={textareaRef}
              value={content}
              onChange={handleTextChange}
              onKeyDown={handleKeyDown}
              placeholder="Start typing... Use keywords like 'meet', 'todo', 'interview' etc. for quick templates."
              className="editor-textarea"
              spellCheck={false}
              autoFocus
            />
          </div>
        </div>

        {/* Chat Sidebar - Always Visible */}
        <div className="chat-sidebar">
          <div className="chat-header">
            <h3>💬 Chat with your notes</h3>
          </div>
          
          <div className="chat-messages" ref={chatMessagesRef}>
            {chatMessages.length === 0 ? (
              <div className="chat-welcome">
                <p>Ask me anything about your notes!</p>
                <p className="chat-examples">
                  Try: "What's the latest about project X?" or "Summarize my meeting notes"
                </p>
              </div>
            ) : (
              chatMessages.map((message) => (
                <div key={message.id} className={`chat-message ${message.type}`}>
                  <div className="message-content">
                    {message.type === 'assistant' ? (
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    ) : (
                      message.content
                    )}
                  </div>
                  <div className="message-time">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))
            )}
            {isChatLoading && (
              <div className="chat-message assistant">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="chat-input-container">
            <input
              ref={chatInputRef}
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={handleChatKeyPress}
              placeholder="Ask about your notes..."
              className="chat-input"
              disabled={isChatLoading}
            />
            <button 
              onClick={sendChatMessage}
              disabled={!chatInput.trim() || isChatLoading}
              className="chat-send-btn"
            >
              Send
            </button>
          </div>
        </div>
      </div>

      {showTemplateEditor && (
        <>
          {console.log('=== TEMPLATE EDITOR MODAL SHOWING ===')}
          <TemplateEditor
            template={editingTemplate}
            onSave={handleSaveTemplate}
            onCancel={handleCloseTemplateEditor}
            onDelete={editingTemplate ? handleDeleteTemplate : undefined}
            isBuiltIn={editingTemplate?.is_builtin || false}
          />
        </>
      )}

    </div>
  );
};

export default NotepadEditor;
