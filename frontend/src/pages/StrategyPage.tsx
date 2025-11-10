import { useState, useRef, useEffect } from 'react'
import { notesApi } from '../services/notesApi'
import './StrategyPage.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

function StrategyPage() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [strategyText, setStrategyText] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [userInput, setUserInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [strategyTitle, setStrategyTitle] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const startSession = async () => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_URL}/api/strategy/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy_text: strategyText })
      })

      if (response.ok) {
        const data = await response.json()
        setSessionId(data.session_id)
        setMessages([{ role: 'assistant', content: data.response }])
      }
    } catch (error) {
      console.error('Failed to start strategy session:', error)
      alert('Failed to start coaching session')
    }
  }

  const sendMessage = async () => {
    if (!userInput.trim() || !sessionId) return

    const userMessage: Message = { role: 'user', content: userInput }
    setMessages(prev => [...prev, userMessage])
    setUserInput('')
    setIsLoading(true)

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_URL}/api/strategy/message/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userInput,
          current_strategy: strategyText
        })
      })

      if (response.ok) {
        const data = await response.json()
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
      }
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const saveAsNote = async () => {
    if (!strategyTitle.trim()) {
      alert('Please enter a strategy title')
      return
    }

    try {
      const conversationText = messages.map(msg =>
        `**${msg.role === 'user' ? 'You' : 'Strategy Coach'}:** ${msg.content}`
      ).join('\n\n')

      const content = `# ${strategyTitle}

## Strategy Statement

${strategyText || 'No strategy statement provided'}

## Coaching Conversation

${conversationText}

---
*Coached with Strategy AI combining Richard Rumelt and John Doerr principles*
`

      await notesApi.createNote({
        title: `Strategy: ${strategyTitle}`,
        content: content,
        tag_names: ['strategy', strategyTitle.toLowerCase().replace(/\s+/g, '-')]
      })

      alert('Strategy saved as note successfully!')
    } catch (error: any) {
      console.error('Failed to save note:', error)
      alert(`Failed to save strategy: ${error.message || 'Unknown error'}`)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="strategy-page">
      <div className="strategy-container">
        {/* Header */}
        <div className="strategy-header">
          <h1>Strategy Coach</h1>
          <p className="subtitle">Crystallize your strategy with insights from Richard Rumelt and John Doerr</p>
        </div>

        {/* Two-column layout */}
        <div className="strategy-content">
          {/* Left Panel - Strategy Document */}
          <div className="strategy-panel">
            <div className="panel-header">
              <h2>Your Strategy</h2>
              <p className="panel-subtitle">Write and refine your strategy statement here</p>
            </div>
            <div className="panel-content">
              <input
                type="text"
                className="strategy-title-input"
                placeholder="Strategy Title (e.g., 'Q1 2024 Product Strategy')"
                value={strategyTitle}
                onChange={(e) => setStrategyTitle(e.target.value)}
              />
              <textarea
                className="strategy-textarea"
                placeholder="Describe your strategy...

Consider:
- What is the core challenge or opportunity?
- What is your diagnosis of the situation?
- What is your guiding policy?
- What are your coherent actions?
- What are your key objectives and key results (OKRs)?"
                value={strategyText}
                onChange={(e) => setStrategyText(e.target.value)}
              />
            </div>
            <div className="panel-footer">
              {!sessionId ? (
                <button
                  className="start-coaching-btn"
                  onClick={startSession}
                  disabled={!strategyText.trim()}
                >
                  Start Coaching Session
                </button>
              ) : (
                <button
                  className="save-btn"
                  onClick={saveAsNote}
                  disabled={!strategyTitle.trim()}
                >
                  Save Strategy as Note
                </button>
              )}
            </div>
          </div>

          {/* Right Panel - Coaching Chat */}
          <div className="coaching-panel">
            <div className="panel-header">
              <h2>Strategy Coach</h2>
              <p className="panel-subtitle">
                {sessionId ? 'Ask questions and get feedback' : 'Start a session to begin coaching'}
              </p>
            </div>

            {!sessionId ? (
              <div className="coaching-placeholder">
                <div className="placeholder-content">
                  <h3>Welcome to Strategy Coach</h3>
                  <p>I combine the strategic thinking of:</p>
                  <ul>
                    <li><strong>Richard Rumelt</strong> - Good strategy kernel: Diagnosis, Guiding Policy, Coherent Actions</li>
                    <li><strong>John Doerr</strong> - OKRs: Objectives and Key Results framework</li>
                  </ul>
                  <p>Write your strategy in the left panel and click "Start Coaching Session" to begin.</p>
                </div>
              </div>
            ) : (
              <>
                <div className="messages-container">
                  {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                      <div className="message-header">
                        {msg.role === 'user' ? 'You' : 'Strategy Coach'}
                      </div>
                      <div className="message-content">
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="message assistant">
                      <div className="message-header">Strategy Coach</div>
                      <div className="message-content typing-indicator">
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                <div className="message-input-container">
                  <textarea
                    className="message-input"
                    placeholder="Ask a question or share your thoughts..."
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    rows={3}
                  />
                  <button
                    className="send-btn"
                    onClick={sendMessage}
                    disabled={!userInput.trim() || isLoading}
                  >
                    Send
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StrategyPage
