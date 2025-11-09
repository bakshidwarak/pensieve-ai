import { useState, useRef } from 'react'
import { transcribeApi } from '../services/notesApi'
import './VoiceRecorder.css'

interface VoiceRecorderProps {
  onTranscriptionComplete: (text: string) => void
}

function VoiceRecorder({ onTranscriptionComplete }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<number | null>(null)

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)

      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        await transcribeAudio(audioBlob)

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)

      // Start timer
      timerRef.current = window.setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)

    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Failed to access microphone. Please grant permission.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)

      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }

  const transcribeAudio = async (audioBlob: Blob) => {
    setIsTranscribing(true)
    try {
      const result = await transcribeApi.transcribeRecording(audioBlob)
      onTranscriptionComplete(result.text)
    } catch (error) {
      console.error('Transcription failed:', error)
      alert('Failed to transcribe audio')
    } finally {
      setIsTranscribing(false)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="voice-recorder">
      <div className="recorder-content">
        {isTranscribing ? (
          <div className="transcribing">
            <div className="spinner"></div>
            <p>Transcribing audio...</p>
          </div>
        ) : (
          <>
            <div className="recorder-status">
              {isRecording ? (
                <>
                  <div className="recording-indicator">
                    <span className="recording-dot"></span>
                    <span>Recording</span>
                  </div>
                  <span className="recording-time">{formatTime(recordingTime)}</span>
                </>
              ) : (
                <p>Click the microphone to start recording</p>
              )}
            </div>

            <button
              className={`record-btn ${isRecording ? 'recording' : ''}`}
              onClick={isRecording ? stopRecording : startRecording}
            >
              {isRecording ? '⏸️ Stop' : '🎤 Start Recording'}
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default VoiceRecorder
