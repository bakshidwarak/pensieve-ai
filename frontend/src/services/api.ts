import axios from 'axios'
import { Message, ChatRequest, ChatResponse } from '../types/chat'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const chatApi = {
  sendMessage: async (
    messages: Message[],
    useRag = false,
    useNotes = true,
    tagFilter?: string[]
  ): Promise<ChatResponse> => {
    const request: ChatRequest = {
      messages,
      use_rag: useRag,
      stream: false,
      use_notes: useNotes,
      tag_filter: tagFilter,
    }
    const response = await api.post<ChatResponse>('/api/chat', request)
    return response.data
  },
}

export const aiApi = {
  queryRag: async (query: string, topK = 5) => {
    const response = await api.post('/api/ai/rag', { query, top_k: topK })
    return response.data
  },

  runAgent: async (task: string, agentType = 'simple') => {
    const response = await api.post('/api/ai/agent', { task, agent_type: agentType })
    return response.data
  },

  getTools: async () => {
    const response = await api.get('/api/ai/tools')
    return response.data
  },
}

export const healthApi = {
  check: async () => {
    const response = await api.get('/api/health')
    return response.data
  },
}

export default api
