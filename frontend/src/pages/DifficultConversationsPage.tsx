import { useState, useRef, useEffect } from 'react'
import { notesApi } from '../services/notesApi'
import './DifficultConversationsPage.css'

type Stage = 'setup' | 'practicing' | 'feedback'

interface Message {
  role: 'user' | 'other_party'
  content: string
  timestamp: string
}

function DifficultConversationsPage() {
  // Stage management
  const [stage, setStage] = useState<Stage>('setup')

  // Setup form
  const [situation, setSituation] = useState('')
  const [message, setMessage] = useState('')
  const [otherPartyGender, setOtherPartyGender] = useState<'male' | 'female'>('male')
  const [difficultyLevel, setDifficultyLevel] = useState(5) // 1-10 scale

  // Practice session
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [conversation, setConversation] = useState<Message[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [otherPartySpeaking, setOtherPartySpeaking] = useState(false)
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [liveTranscript, setLiveTranscript] = useState('') // What user is currently saying
  const [coachMode, setCoachMode] = useState(false) // Toggle between roleplay and coach

  // Feedback
  const [feedback, setFeedback] = useState('')
  const [conversationTitle, setConversationTitle] = useState('')

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioStreamRef = useRef<MediaStream | null>(null)
  const isRecordingRef = useRef<boolean>(false)
  const audioBufferRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const transcriptBufferRef = useRef<string>('') // Accumulated transcript
  const lastSpeechTimeRef = useRef<number>(Date.now())
  const pauseDetectionTimerRef = useRef<number | null>(null)
  const sessionIdRef = useRef<string | null>(null) // Ref to avoid closure issues

  const getDifficultyLabel = (level: number) => {
    if (level <= 2) return 'Very Easy'
    if (level <= 4) return 'Easy'
    if (level <= 6) return 'Moderate'
    if (level <= 8) return 'Difficult'
    return 'Very Difficult'
  }

  const startPractice = async () => {
    if (!situation.trim() || !message.trim()) {
      alert('Please fill in all fields')
      return
    }

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_URL}/api/conversations/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          situation,
          message_to_deliver: message,
          other_party_gender: otherPartyGender,
          difficulty_level: difficultyLevel
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Session started with ID:', data.session_id)
        setSessionId(data.session_id)
        sessionIdRef.current = data.session_id // Keep ref in sync
        setStage('practicing')

        // Play initial response from other party
        if (data.audio_url) {
          await playAudioResponse(data.audio_url, data.response)
        }
      }
    } catch (error) {
      console.error('Failed to start practice:', error)
      alert('Failed to start practice session')
    }
  }

  const playAudioResponse = async (audioUrl: string, text: string) => {
    console.log('playAudioResponse called with:', { audioUrl, text })

    // Stop user recording while AI speaks
    if (isRecordingRef.current) {
      // Pause recording but don't lose the stream
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        console.log('Pausing ongoing recording')
        mediaRecorderRef.current.pause()
      }
    }

    setOtherPartySpeaking(true)

    const timestamp = new Date().toLocaleTimeString()
    setConversation(prev => [...prev, {
      role: 'other_party',
      content: text,
      timestamp
    }])

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const audio = new Audio(`${API_URL}${audioUrl}`)
    audioRef.current = audio

    audio.onended = () => {
      console.log('AI audio finished playing')
      console.log('Current state - isRecording:', isRecordingRef.current, 'sessionId:', sessionIdRef.current)

      setOtherPartySpeaking(false)

      // Resume user recording
      if (isRecordingRef.current && mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
        console.log('Resuming paused recording')
        mediaRecorderRef.current.resume()
      } else {
        // Always start recording after AI finishes - no conditions
        console.log('Starting new recording after AI finished')
        startRecording()
      }
    }

    audio.onerror = (e) => {
      console.error('Audio playback error:', e)
      setOtherPartySpeaking(false)
    }

    console.log('Starting audio playback...')
    await audio.play()
  }

  const startRecording = async () => {
    const currentSessionId = sessionIdRef.current
    console.log('startRecording called, sessionId:', currentSessionId)

    if (!currentSessionId) {
      console.error('Cannot start recording - no session ID')
      return
    }

    // If already recording, don't start again
    if (isRecordingRef.current) {
      console.log('Already recording, skipping')
      return
    }

    try {
      console.log('Requesting microphone access...')
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioStreamRef.current = stream
      isRecordingRef.current = true
      setIsRecording(true)

      console.log('🎤 Started recording successfully')

      const startRecordingChunk = () => {
        if (!isRecordingRef.current || !audioStreamRef.current) {
          console.log('Stopping recording loop - recording stopped or stream ended')
          return
        }

        const mediaRecorder = new MediaRecorder(audioStreamRef.current, {
          mimeType: 'audio/webm'
        })

        let audioChunks: Blob[] = []

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.push(event.data)
          }
        }

        mediaRecorder.onstop = () => {
          if (audioChunks.length > 0) {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
            transcribeChunk(audioBlob)
          }

          // Only continue if still recording
          if (isRecordingRef.current && audioStreamRef.current) {
            setTimeout(() => startRecordingChunk(), 100)
          }
        }

        mediaRecorder.start()
        mediaRecorderRef.current = mediaRecorder

        // Shorter chunks - 2 seconds for more responsive dialogue
        setTimeout(() => {
          if (mediaRecorder.state === 'recording') {
            mediaRecorder.stop()
          }
        }, 2000)
      }

      startRecordingChunk()

    } catch (error) {
      console.error('Failed to start recording:', error)
      alert('Could not access microphone')
    }
  }

  const transcribeChunk = async (audioBlob: Blob) => {
    if (!sessionIdRef.current || otherPartySpeaking) {
      console.log('Skipping transcription - no session or AI is speaking')
      return
    }

    try {
      const formData = new FormData()
      formData.append('audio_data', audioBlob, 'chunk.webm')
      formData.append('language', 'en')

      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

      console.log('Transcribing audio chunk...')
      const response = await fetch(`${API_URL}/api/transcribe/from-recording`, {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        const text = data.text
        console.log('Transcribed text:', text)

        if (text && text.trim()) {
          // Update live transcript
          transcriptBufferRef.current += ' ' + text
          setLiveTranscript(transcriptBufferRef.current)
          console.log('Current transcript buffer:', transcriptBufferRef.current)

          // Reset pause timer - user is still speaking
          lastSpeechTimeRef.current = Date.now()

          // Check if AI should respond based on what's being said
          checkForAITurn()
        }
      } else {
        console.error('Transcription failed:', await response.text())
      }
    } catch (error) {
      console.error('Transcription error:', error)
    }
  }

  const checkForAITurn = () => {
    // Clear existing timer
    if (pauseDetectionTimerRef.current) {
      clearTimeout(pauseDetectionTimerRef.current)
    }

    const currentText = transcriptBufferRef.current.trim()

    // Check if user asked a question or made a statement that needs response
    const endsWithQuestion = currentText.match(/[?][\s]*$/)
    const hasCompleteThought = currentText.split(/[.!?]/).length > 1
    const wordCount = currentText.split(/\s+/).length

    // AI should respond if:
    // 1. User asked a question (immediate response)
    // 2. User made a complete statement (2+ sentences)
    // 3. User has said enough (15+ words) and there's a natural pause

    if (endsWithQuestion && wordCount >= 3) {
      // Question asked - respond quickly (500ms pause)
      pauseDetectionTimerRef.current = setTimeout(() => {
        if (transcriptBufferRef.current.trim()) {
          triggerAIResponse(transcriptBufferRef.current)
        }
      }, 500)
    } else if (hasCompleteThought && wordCount >= 10) {
      // Complete thought - respond after short pause (1 second)
      pauseDetectionTimerRef.current = setTimeout(() => {
        const timeSinceLastSpeech = Date.now() - lastSpeechTimeRef.current
        if (timeSinceLastSpeech >= 1000 && transcriptBufferRef.current.trim()) {
          triggerAIResponse(transcriptBufferRef.current)
        }
      }, 1000)
    } else if (wordCount >= 15) {
      // User talking a lot - check for pause to interject (1.5 seconds)
      pauseDetectionTimerRef.current = setTimeout(() => {
        const timeSinceLastSpeech = Date.now() - lastSpeechTimeRef.current
        if (timeSinceLastSpeech >= 1500 && transcriptBufferRef.current.trim()) {
          triggerAIResponse(transcriptBufferRef.current)
        }
      }, 1500)
    } else {
      // Default - wait for longer pause (2.5 seconds)
      pauseDetectionTimerRef.current = setTimeout(() => {
        const timeSinceLastSpeech = Date.now() - lastSpeechTimeRef.current
        if (timeSinceLastSpeech >= 2500 && transcriptBufferRef.current.trim()) {
          triggerAIResponse(transcriptBufferRef.current)
        }
      }, 2500)
    }
  }

  const triggerAIResponse = async (userText: string) => {
    const currentSessionId = sessionIdRef.current
    if (!currentSessionId || !userText.trim()) {
      console.log('Cannot trigger AI response - no session or empty text')
      return
    }

    console.log('🤖 Triggering AI response for:', userText.trim())

    // Add user's turn to conversation
    const timestamp = new Date().toLocaleTimeString()
    setConversation(prev => [...prev, {
      role: 'user',
      content: userText.trim(),
      timestamp
    }])

    // Clear transcript buffer
    transcriptBufferRef.current = ''
    setLiveTranscript('')

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

      console.log('Calling AI endpoint...')
      const response = await fetch(`${API_URL}/api/conversations/respond/${currentSessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_message: userText.trim() })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('AI response received:', data.response)

        // Play AI response
        if (data.audio_url) {
          console.log('Playing AI audio...')
          await playAudioResponse(data.audio_url, data.response)
        }
      } else {
        console.error('AI response failed:', await response.text())
      }
    } catch (error) {
      console.error('Failed to get AI response:', error)
    }
  }

  const finalizeUserTurn = () => {
    // Clear any pending timers
    if (pauseDetectionTimerRef.current) {
      clearTimeout(pauseDetectionTimerRef.current)
    }
  }

  const stopRecording = () => {
    isRecordingRef.current = false
    setIsRecording(false)

    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
    }

    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach(track => track.stop())
      audioStreamRef.current = null
    }
  }


  const endConversation = async () => {
    if (!sessionId) return

    stopRecording()

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_URL}/api/conversations/feedback/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_transcript: conversation.map(m => `${m.role === 'user' ? 'You' : 'Other Party'}: ${m.content}`).join('\n')
        })
      })

      if (response.ok) {
        const data = await response.json()
        setFeedback(data.feedback)
        setStage('feedback')
      }
    } catch (error) {
      console.error('Failed to get feedback:', error)
    }
  }

  const saveConversation = async () => {
    if (!conversationTitle.trim()) {
      alert('Please enter a title for this conversation')
      return
    }

    try {
      const conversationText = conversation.map(msg =>
        `**${msg.role === 'user' ? 'You' : 'Other Party'} [${msg.timestamp}]:** ${msg.content}`
      ).join('\n\n')

      const content = `# ${conversationTitle}

## Situation
${situation}

## Message to Deliver
${message}

## Difficulty Level
${getDifficultyLabel(difficultyLevel)} (${difficultyLevel}/10)

## Conversation

${conversationText}

## Coach Feedback

${feedback}

---
*Practiced with Difficult Conversations Coach based on Crucial Conversations principles*
`

      await notesApi.createNote({
        title: `Practice: ${conversationTitle}`,
        content: content,
        tag_names: ['difficult-conversation', 'practice', conversationTitle.toLowerCase().replace(/\s+/g, '-')]
      })

      alert('Conversation practice saved as note!')
    } catch (error: any) {
      console.error('Failed to save note:', error)
      alert(`Failed to save: ${error.message || 'Unknown error'}`)
    }
  }

  return (
    <div className="difficult-conversations-page">
      <div className="conversations-container">
        {/* Header */}
        <div className="conversations-header">
          <h1>Practice Difficult Conversations</h1>
          <p className="subtitle">Master crucial conversations with AI roleplay based on proven principles</p>
        </div>

        {/* Setup Stage */}
        {stage === 'setup' && (
          <div className="setup-panel">
            <div className="setup-content">
              <h2>Prepare Your Conversation</h2>
              <p className="section-help">Set up the scenario you want to practice</p>

              <div className="form-group">
                <label>Describe the Situation</label>
                <textarea
                  className="setup-textarea"
                  placeholder="What's the context? Who are you speaking with? What's at stake?

Example: I need to give performance feedback to a team member who has been consistently missing deadlines..."
                  value={situation}
                  onChange={(e) => setSituation(e.target.value)}
                  rows={6}
                />
              </div>

              <div className="form-group">
                <label>What Message Do You Want to Deliver?</label>
                <textarea
                  className="setup-textarea"
                  placeholder="What do you need to communicate?

Example: The missed deadlines are affecting the team's ability to deliver, and we need to address this urgently..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={4}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Other Party's Gender</label>
                  <select
                    className="setup-select"
                    value={otherPartyGender}
                    onChange={(e) => setOtherPartyGender(e.target.value as 'male' | 'female')}
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Difficulty Level: {getDifficultyLabel(difficultyLevel)} ({difficultyLevel}/10)</label>
                <input
                  type="range"
                  className="difficulty-slider"
                  min="1"
                  max="10"
                  value={difficultyLevel}
                  onChange={(e) => setDifficultyLevel(parseInt(e.target.value))}
                />
                <div className="difficulty-labels">
                  <span>Easy</span>
                  <span>Moderate</span>
                  <span>Very Difficult</span>
                </div>
              </div>

              <button
                className="start-practice-btn"
                onClick={startPractice}
                disabled={!situation.trim() || !message.trim()}
              >
                Start Practice
              </button>
            </div>
          </div>
        )}

        {/* Practicing Stage */}
        {stage === 'practicing' && (
          <div className="practice-panel">
            <div className="practice-header">
              <h2>Practice Session</h2>
              <div className="practice-controls">
                <button
                  className={`mode-toggle-btn ${!coachMode ? 'active' : ''}`}
                  onClick={() => setCoachMode(false)}
                >
                  Roleplay Mode
                </button>
                <button
                  className={`mode-toggle-btn ${coachMode ? 'active' : ''}`}
                  onClick={() => setCoachMode(true)}
                >
                  Ask Coach
                </button>
                <button className="end-conversation-btn" onClick={endConversation}>
                  End Conversation
                </button>
              </div>
            </div>

            <div className="conversation-display">
              {conversation.map((msg, idx) => (
                <div key={idx} className={`conversation-message ${msg.role}`}>
                  <div className="message-header">
                    <span className="message-role">
                      {msg.role === 'user' ? 'You' : 'Other Party'}
                    </span>
                    <span className="message-time">{msg.timestamp}</span>
                  </div>
                  <div className="message-text">{msg.content}</div>
                </div>
              ))}

              {otherPartySpeaking && (
                <div className="speaking-indicator">
                  <span className="indicator-dot"></span>
                  Other party is speaking...
                </div>
              )}

              {isRecording && !otherPartySpeaking && (
                <div className="recording-indicator">
                  <span className="indicator-dot recording"></span>
                  <div>
                    <div>
                      {coachMode
                        ? "Speaking to Coach... (ask for advice)"
                        : "You are speaking... (talk to the other party)"}
                    </div>
                    {liveTranscript && (
                      <div className="live-transcript">{liveTranscript}</div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="practice-status">
              <div className="status-info">
                {isRecording && <p>🎤 Recording your response...</p>}
                {isProcessing && <p>⏳ Processing...</p>}
                {otherPartySpeaking && <p>🔊 Other party is responding...</p>}
              </div>
            </div>
          </div>
        )}

        {/* Feedback Stage */}
        {stage === 'feedback' && (
          <div className="feedback-panel">
            <div className="feedback-header">
              <h2>Conversation Feedback</h2>
            </div>

            <div className="feedback-content">
              <div className="feedback-section">
                <h3>Coach's Analysis</h3>
                <div className="feedback-text">{feedback}</div>
              </div>

              <div className="conversation-recap">
                <h3>Conversation Transcript</h3>
                {conversation.map((msg, idx) => (
                  <div key={idx} className={`recap-message ${msg.role}`}>
                    <strong>{msg.role === 'user' ? 'You' : 'Other Party'}:</strong> {msg.content}
                  </div>
                ))}
              </div>

              <div className="save-section">
                <input
                  type="text"
                  className="conversation-title-input"
                  placeholder="Enter a title for this practice session"
                  value={conversationTitle}
                  onChange={(e) => setConversationTitle(e.target.value)}
                />
                <button
                  className="save-conversation-btn"
                  onClick={saveConversation}
                  disabled={!conversationTitle.trim()}
                >
                  Save to Notes
                </button>
                <button
                  className="new-practice-btn"
                  onClick={() => {
                    setStage('setup')
                    setSituation('')
                    setMessage('')
                    setConversation([])
                    setFeedback('')
                    setSessionId(null)
                  }}
                >
                  New Practice Session
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DifficultConversationsPage
