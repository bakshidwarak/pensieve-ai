import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface StartInterviewRequest {
  candidate_name: string
  position: string
  interview_rubric: string
  resume?: File
}

export interface InterviewMessageRequest {
  session_id: string
  message: string
  transcript_entry?: string
}

export interface InterviewResponse {
  session_id: string
  response: string
  suggested_questions?: string[]
  coaching_feedback?: string[]
  structured_notes?: string
  strengths?: string[]
  areas_of_improvement?: string[]
}

export const interviewApi = {
  startInterview: async (data: StartInterviewRequest): Promise<InterviewResponse> => {
    const formData = new FormData()
    formData.append('candidate_name', data.candidate_name)
    formData.append('position', data.position)
    formData.append('interview_rubric', data.interview_rubric)
    if (data.resume) {
      formData.append('resume', data.resume)
    }

    const response = await axios.post(`${API_URL}/api/interview/start`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  sendMessage: async (data: InterviewMessageRequest): Promise<InterviewResponse> => {
    const response = await axios.post(`${API_URL}/api/interview/message`, data)
    return response.data
  },

  getSessionState: async (sessionId: string): Promise<InterviewResponse> => {
    const response = await axios.get(`${API_URL}/api/interview/session/${sessionId}`)
    return response.data
  },

  getSuggestions: async (sessionId: string, transcriptEntry?: string): Promise<InterviewResponse> => {
    const response = await axios.post(`${API_URL}/api/interview/suggestions/${sessionId}`, {
      session_id: sessionId,
      message: '',
      transcript_entry: transcriptEntry
    })
    return response.data
  },

  brainstormChat: async (data: InterviewMessageRequest): Promise<InterviewResponse> => {
    const response = await axios.post(`${API_URL}/api/interview/brainstorm/${data.session_id}`, data)
    return response.data
  },

  generateFeedback: async (sessionId: string, hireDecision: string, decisionReason: string): Promise<InterviewResponse> => {
    const response = await axios.post(`${API_URL}/api/interview/feedback/${sessionId}`, {
      hire_decision: hireDecision,
      decision_reason: decisionReason
    })
    return response.data
  },

  endInterview: async (sessionId: string): Promise<void> => {
    await axios.delete(`${API_URL}/api/interview/session/${sessionId}`)
  }
}
