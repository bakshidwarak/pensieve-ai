import { useState, useEffect, useRef } from 'react'
import { interviewApi, InterviewResponse } from '../services/interviewApi'
import { notesApi } from '../services/notesApi'
import './InterviewWizardPage.css'

type InterviewStage = 'setup' | 'conducting' | 'brainstorm' | 'complete'

function InterviewWizardPage() {
  // Stage management
  const [stage, setStage] = useState<InterviewStage>('setup')

  // Setup data
  const [candidateName, setCandidateName] = useState('')
  const [position, setPosition] = useState('')
  const [rubric, setRubric] = useState('')
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [resumeUrl, setResumeUrl] = useState<string | null>(null)

  // Interview session
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [interviewNotes, setInterviewNotes] = useState('')
  const [transcript, setTranscript] = useState<string[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([])
  const [coachingTips, setCoachingTips] = useState<string[]>([])
  const [suggestionHistory, setSuggestionHistory] = useState<Array<{timestamp: string, questions: string[]}>>([])
  const [coachingHistory, setCoachingHistory] = useState<Array<{timestamp: string, tips: string[]}>>([])


  // Brainstorm stage
  const [analysis, setAnalysis] = useState('')
  const [strengths, setStrengths] = useState<string[]>([])
  const [concerns, setConcerns] = useState<string[]>([])
  const [brainstormMessages, setBrainstormMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([])
  const [userInput, setUserInput] = useState('')
  const [hireDecision, setHireDecision] = useState<'hire' | 'no-hire' | null>(null)
  const [decisionReason, setDecisionReason] = useState('')
  const [isShepherdTyping, setIsShepherdTyping] = useState(false)

  // Final feedback
  const [finalFeedback, setFinalFeedback] = useState('')

  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const transcriptTimerRef = useRef<NodeJS.Timeout | null>(null)
  const suggestionTimerRef = useRef<NodeJS.Timeout | null>(null)
  const audioBufferRef = useRef<Blob[]>([])
  const isRecordingRef = useRef<boolean>(false)
  const audioStreamRef = useRef<MediaStream | null>(null)

  // Handle resume upload
  const handleResumeUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type === 'application/pdf') {
      setResumeFile(file)
      const url = URL.createObjectURL(file)
      setResumeUrl(url)
    }
  }

  // Start interview
  const handleStartInterview = async () => {
    if (!candidateName || !position || !rubric) {
      alert('Please fill in all required fields')
      return
    }

    try {
      const response = await interviewApi.startInterview({
        candidate_name: candidateName,
        position: position,
        interview_rubric: rubric,
        resume: resumeFile || undefined
      })

      setSessionId(response.session_id)
      setSuggestedQuestions(response.suggested_questions || [])
      setStage('conducting')
    } catch (error) {
      console.error('Failed to start interview:', error)
      alert('Failed to start interview session')
    }
  }

  // Start/stop recording
  const toggleRecording = async () => {
    if (isRecording) {
      // Stop recording
      console.log('Stopping recording...')
      isRecordingRef.current = false
      setIsRecording(false)

      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop()
      }

      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach(track => track.stop())
        audioStreamRef.current = null
      }
    } else {
      // Start recording with continuous restart for real-time transcription
      try {
        console.log('Starting recording...')
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        audioStreamRef.current = stream
        isRecordingRef.current = true
        setIsRecording(true)

        const startRecordingChunk = () => {
          // Check if we should still be recording
          if (!isRecordingRef.current) {
            console.log('Recording stopped by user, not starting new chunk')
            return
          }

          console.log('Starting new 3-second recording chunk')
          const mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm'
          })

          let audioChunks: Blob[] = []

          mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
              console.log('Audio chunk received, size:', event.data.size)
              audioChunks.push(event.data)
            }
          }

          mediaRecorder.onstop = () => {
            console.log('Recorder stopped, chunks collected:', audioChunks.length)

            // Create complete audio file from this recording session
            if (audioChunks.length > 0) {
              const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
              console.log('Transcribing blob of size:', audioBlob.size)

              // Transcribe this chunk
              transcribeAudio(audioBlob).catch(err => {
                console.error('Transcription error:', err)
              })
            }

            // Restart recording if still in recording mode (check ref, not state)
            if (isRecordingRef.current) {
              console.log('Still recording, starting next chunk in 100ms')
              setTimeout(() => startRecordingChunk(), 100)
            } else {
              console.log('Recording finished, cleaning up')
            }
          }

          // Record for 3 seconds then stop to create a complete file
          mediaRecorder.start()
          mediaRecorderRef.current = mediaRecorder

          // Stop after 3 seconds to generate a complete audio file
          setTimeout(() => {
            if (mediaRecorder.state === 'recording') {
              console.log('3 seconds elapsed, stopping recorder')
              mediaRecorder.stop()
            }
          }, 3000)
        }

        startRecordingChunk()
      } catch (error) {
        console.error('Failed to start recording:', error)
        alert('Could not access microphone')
        isRecordingRef.current = false
        setIsRecording(false)
      }
    }
  }

  // Transcribe audio using backend API
  const transcribeAudio = async (audioBlob: Blob) => {
    console.log('Starting transcription, blob size:', audioBlob.size)
    try {
      setIsTranscribing(true)

      const formData = new FormData()
      formData.append('audio_data', audioBlob, 'recording.webm')
      formData.append('language', 'en')

      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      console.log('Sending to:', `${API_URL}/api/transcribe/from-recording`)

      const response = await fetch(`${API_URL}/api/transcribe/from-recording`, {
        method: 'POST',
        body: formData,
      })

      console.log('Response status:', response.status)

      if (response.ok) {
        const data = await response.json()
        console.log('Transcription result:', data)

        if (data.text && data.text.trim()) {
          const newText = data.text
          console.log('Adding text:', newText)

          // Append to current transcript with a space
          setCurrentTranscript(prev => {
            const updated = prev ? `${prev} ${newText}` : newText
            console.log('Updated transcript to:', updated)
            return updated
          })

          // Also update the interview notes field in real-time
          setInterviewNotes(prev => {
            if (prev) {
              return prev + ' ' + newText
            }
            return newText
          })

          // Trigger AI suggestions
          setTimeout(() => sendTranscriptToAI(), 500)
        } else {
          console.log('No text in response or empty text')
        }
      } else {
        console.error('Response not ok:', response.status, await response.text())
      }
    } catch (error) {
      console.error('Failed to transcribe audio:', error)
    } finally {
      setIsTranscribing(false)
    }
  }

  // Send transcript to AI for suggestions
  const sendTranscriptToAI = async () => {
    if (!sessionId) return

    try {
      // Use the current live transcript for context
      const transcriptText = currentTranscript || interviewNotes

      // Call dedicated suggestions endpoint for real-time, contextual AI feedback
      const response = await interviewApi.getSuggestions(sessionId, transcriptText)

      const timestamp = new Date().toLocaleTimeString()

      // Update current suggestions
      const newQuestions = response.suggested_questions || []
      const newTips = response.coaching_feedback || []

      setSuggestedQuestions(newQuestions)
      setCoachingTips(newTips)

      // Add to history (latest first)
      if (newQuestions.length > 0) {
        setSuggestionHistory(prev => [{timestamp, questions: newQuestions}, ...prev])
      }
      if (newTips.length > 0) {
        setCoachingHistory(prev => [{timestamp, tips: newTips}, ...prev])
      }
    } catch (error) {
      console.error('Failed to get AI suggestions:', error)
    }
  }

  // Add transcript entry manually
  const handleAddTranscriptEntry = (entry: string) => {
    setTranscript(prev => {
      const newTranscript = [...prev, entry]
      // Trigger AI suggestions automatically after manual entry
      setTimeout(() => sendTranscriptToAI(), 500)
      return newTranscript
    })
  }

  // Move to brainstorm stage
  const handleMoveToBrainstorm = async () => {
    if (!sessionId) return

    try {
      // Start brainstorm stage with shepherd's initial message
      setStage('brainstorm')
      setIsShepherdTyping(true)

      const response = await interviewApi.brainstormChat({
        session_id: sessionId,
        message: "Let's brainstorm about this candidate. What are your initial thoughts on how the interview went?"
      })

      // Add initial messages to chat
      setBrainstormMessages([
        {
          role: 'assistant',
          content: response.response
        }
      ])
      setIsShepherdTyping(false)
    } catch (error: any) {
      console.error('Failed to start brainstorm:', error)
      setIsShepherdTyping(false)

      // Check if it's a 404 (session not found)
      if (error.response?.status === 404) {
        alert('Session expired. Please start a new interview. (This happens when the server restarts during development)')
        window.location.reload()
      } else {
        alert('Failed to start brainstorm. Please try again.')
      }
    }
  }

  // Submit brainstorm chat message
  const handleBrainstormInput = async () => {
    if (!sessionId || !userInput.trim()) return

    try {
      // Add user message to chat immediately
      const userMessage = { role: 'user' as const, content: userInput }
      setBrainstormMessages(prev => [...prev, userMessage])
      setUserInput('')
      setIsShepherdTyping(true)

      // Send to AI
      const response = await interviewApi.brainstormChat({
        session_id: sessionId,
        message: userMessage.content
      })

      // Add AI response to chat
      const assistantMessage = { role: 'assistant' as const, content: response.response }
      setBrainstormMessages(prev => [...prev, assistantMessage])
      setIsShepherdTyping(false)
    } catch (error) {
      console.error('Failed to send brainstorm message:', error)
      setIsShepherdTyping(false)
      alert('Failed to send message. Please try again.')
    }
  }

  // Generate final feedback scorecard
  const handleGenerateFeedback = async () => {
    if (!sessionId || !hireDecision || !decisionReason) {
      alert('Please make a hire/no-hire decision and provide your reasoning')
      return
    }

    try {
      const response = await interviewApi.generateFeedback(sessionId, hireDecision, decisionReason)

      setFinalFeedback(response.response)
      setStage('complete')
    } catch (error) {
      console.error('Failed to generate feedback:', error)
      alert('Failed to generate final feedback scorecard')
    }
  }

  // Save as note
  const handleSaveAsNote = async () => {
    if (!candidateName || !position) {
      alert('Missing candidate information')
      return
    }

    try {
      const content = `# Interview with ${candidateName}

**Position:** ${position}

## Interview Notes
${interviewNotes || 'No notes recorded'}

## Transcript
${transcript.length > 0 ? transcript.join('\n\n') : 'No transcript available'}

${hireDecision ? `## Decision\n**Hiring Decision:** ${hireDecision.toUpperCase()}\n**Reason:** ${decisionReason || 'Not provided'}\n` : ''}

${finalFeedback ? `## Interview Scorecard\n${finalFeedback}` : '## Feedback\nInterview completed but no detailed feedback generated.'}
`

      await notesApi.createNote({
        title: `Interview: ${candidateName} - ${position}`,
        content: content,
        tag_names: ['interview', candidateName.toLowerCase().replace(/\s+/g, '-'), position.toLowerCase().replace(/\s+/g, '-')]
      })

      alert('Interview saved as note successfully!')

      // Clean up
      if (sessionId) {
        await interviewApi.endInterview(sessionId)
      }

      // Reset
      window.location.reload()
    } catch (error: any) {
      console.error('Failed to save note:', error)
      alert(`Failed to save interview as note: ${error.message || 'Unknown error'}`)
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (resumeUrl) {
        URL.revokeObjectURL(resumeUrl)
      }
      if (transcriptTimerRef.current) {
        clearInterval(transcriptTimerRef.current)
      }
      if (suggestionTimerRef.current) {
        clearInterval(suggestionTimerRef.current)
      }
    }
  }, [resumeUrl])

  // Continuous polling for suggestions every 30 seconds during interview
  useEffect(() => {
    if (stage === 'conducting' && sessionId) {
      // Start polling for suggestions every 30 seconds
      suggestionTimerRef.current = setInterval(() => {
        sendTranscriptToAI()
      }, 30000) // 30 seconds

      // Cleanup when leaving conducting stage
      return () => {
        if (suggestionTimerRef.current) {
          clearInterval(suggestionTimerRef.current)
        }
      }
    }
  }, [stage, sessionId])

  // Render based on stage
  return (
    <div className="interview-wizard-page">
      {stage === 'setup' && (
        <div className="setup-stage">
          <div className="setup-content">
            <h1>New Interview</h1>
            <div className="setup-form">
              <div className="form-group">
                <label>Candidate Name *</label>
                <input
                  type="text"
                  value={candidateName}
                  onChange={(e) => setCandidateName(e.target.value)}
                  placeholder="John Doe"
                />
              </div>

              <div className="form-group">
                <label>Position *</label>
                <input
                  type="text"
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                  placeholder="Senior Software Engineer"
                />
              </div>

              <div className="form-group">
                <label>Interview Rubric *</label>
                <textarea
                  value={rubric}
                  onChange={(e) => setRubric(e.target.value)}
                  placeholder="Enter the interview criteria and evaluation rubric..."
                  rows={8}
                />
              </div>

              <div className="form-group">
                <label>Resume (PDF)</label>
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={handleResumeUpload}
                />
              </div>

              <button className="start-btn" onClick={handleStartInterview}>
                Start Interview
              </button>
            </div>
          </div>
        </div>
      )}

      {stage === 'conducting' && (
        <div className="conducting-stage">
          {/* Left Panel - Resume */}
          <div className="resume-panel">
            <div className="panel-header">
              <h3>Resume</h3>
            </div>
            <div className="panel-content">
              {resumeUrl ? (
                <iframe
                  src={resumeUrl}
                  title="Resume"
                  className="pdf-viewer"
                />
              ) : (
                <div className="empty-state">
                  <p>No resume uploaded</p>
                </div>
              )}
            </div>
          </div>

          {/* Middle Panel - Notes & Transcript */}
          <div className="notes-panel">
            <div className="panel-header">
              <h3>Interview Notes</h3>
              <button
                className={`mic-btn ${isRecording ? 'recording' : ''}`}
                onClick={toggleRecording}
              >
                🎤 {isRecording ? 'Stop' : 'Record'}
              </button>
            </div>
            <div className="panel-content">
              <textarea
                className="notes-textarea"
                value={interviewNotes}
                onChange={(e) => setInterviewNotes(e.target.value)}
                placeholder="Take notes during the interview..."
              />

              {/* Live Transcript Display */}
              <div className="transcript-section">
                <h4>Live Transcript {isTranscribing && <span className="transcribing-indicator">● Transcribing...</span>}</h4>
                <div className="live-transcript">
                  {currentTranscript || <span className="transcript-placeholder">Start recording to see live transcript...</span>}
                </div>
              </div>
            </div>
            <div className="panel-footer">
              <button className="next-btn" onClick={handleMoveToBrainstorm}>
                Next: Brainstorm →
              </button>
            </div>
          </div>

          {/* Right Panel - AI Suggestions */}
          <div className="suggestions-panel">
            <div className="panel-header">
              <h3>Interview Buddy</h3>
            </div>
            <div className="panel-content">
              {/* Real-time AI Feedback */}
              {currentTranscript && (
                <div className="ai-feedback-section">
                  <h4>💬 Real-time Feedback</h4>
                  <div className="ai-feedback-content">
                    {transcript.length < 3
                      ? "Keep recording... I'll provide feedback as the conversation progresses."
                      : "Based on the conversation flow, I'm analyzing the interview dynamics and rubric coverage..."}
                  </div>
                </div>
              )}

              {suggestionHistory.length > 0 && (
                <div className="suggestions-section">
                  <h4>💡 Suggested Questions (Latest First)</h4>
                  <div className="suggestions-scroll">
                    {suggestionHistory.map((entry, entryIdx) => (
                      <div key={entryIdx} className="suggestion-entry">
                        <div className="suggestion-timestamp">{entry.timestamp}</div>
                        <ul className="suggestions-list">
                          {entry.questions.map((q, idx) => (
                            <li key={idx}>{q}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {coachingTips.length > 0 && (
                <div className="coaching-section">
                  <h4>🎯 Coaching Tips</h4>
                  <ul className="coaching-list">
                    {coachingTips.map((tip, idx) => (
                      <li key={idx}>{tip}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {stage === 'brainstorm' && (
        <div className="brainstorm-stage">
          <div className="brainstorm-content">
            <h1>Interview Brainstorm - Chat with your Shepherd</h1>
            <p className="shepherd-intro">
              Discuss your thoughts about the candidate with the Interview Shepherd.
              Work through your decision together.
            </p>

            {/* Chat Messages */}
            <div className="chat-container">
              <div className="chat-messages">
                {brainstormMessages.map((msg, idx) => (
                  <div key={idx} className={`chat-message ${msg.role}`}>
                    <div className="message-header">
                      {msg.role === 'assistant' ? '🧙 Interview Shepherd' : '👤 You'}
                    </div>
                    <div className="message-content">{msg.content}</div>
                  </div>
                ))}
                {isShepherdTyping && (
                  <div className="chat-message assistant">
                    <div className="message-header">🧙 Interview Shepherd</div>
                    <div className="message-content typing">Thinking...</div>
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div className="chat-input-container">
                <textarea
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleBrainstormInput()
                    }
                  }}
                  placeholder="Share your thoughts, ask questions, or discuss the candidate..."
                  rows={3}
                  disabled={isShepherdTyping}
                />
                <button
                  onClick={handleBrainstormInput}
                  disabled={!userInput.trim() || isShepherdTyping}
                  className="send-btn"
                >
                  Send
                </button>
              </div>
            </div>

            {/* Decision Section */}
            <div className="decision-section">
              <h3>When you're ready, make your decision:</h3>
              <div className="decision-buttons">
                <button
                  className={`decision-btn hire ${hireDecision === 'hire' ? 'selected' : ''}`}
                  onClick={() => setHireDecision('hire')}
                >
                  ✓ Hire
                </button>
                <button
                  className={`decision-btn no-hire ${hireDecision === 'no-hire' ? 'selected' : ''}`}
                  onClick={() => setHireDecision('no-hire')}
                >
                  ✗ No Hire
                </button>
              </div>

              {hireDecision && (
                <div className="decision-reason">
                  <label>Final Remarks & Reason for Decision *</label>
                  <textarea
                    value={decisionReason}
                    onChange={(e) => setDecisionReason(e.target.value)}
                    placeholder="Summarize your reasoning for this decision..."
                    rows={4}
                  />
                </div>
              )}

              <button
                className="generate-feedback-btn"
                onClick={handleGenerateFeedback}
                disabled={!hireDecision || !decisionReason}
              >
                Generate Final Scorecard →
              </button>
            </div>
          </div>
        </div>
      )}

      {stage === 'complete' && (
        <div className="complete-stage">
          <div className="complete-content">
            <h1>Interview Scorecard Complete</h1>

            <div className="feedback-section">
              <h3>📊 Interview Scorecard</h3>
              <p className="scorecard-info">
                Comprehensive evaluation based on the rubric, transcript, and your brainstorm discussion.
              </p>
              <pre className="feedback-markdown">{finalFeedback}</pre>
              <div className="action-buttons">
                <button
                  className="copy-btn"
                  onClick={() => {
                    navigator.clipboard.writeText(finalFeedback)
                    alert('Scorecard copied to clipboard!')
                  }}
                >
                  📋 Copy to Clipboard
                </button>
                <button className="save-note-btn" onClick={handleSaveAsNote}>
                  💾 Save as Note
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InterviewWizardPage
