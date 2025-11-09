export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  messages: Message[]
  use_rag: boolean
  stream: boolean
  use_notes?: boolean
  tag_filter?: string[]
}

export interface ChatResponse {
  message: Message
  tool_calls?: any[]
  sources?: any[]
}
