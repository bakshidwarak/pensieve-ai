import { useState, useCallback } from 'react'
import { Message } from '../types/chat'
import { chatApi } from '../services/api'

export function useChat(useNotes = true, tagFilter?: string[]) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: Message = {
      role: 'user',
      content,
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await chatApi.sendMessage(
        [...messages, userMessage],
        false, // use_rag
        useNotes, // use_notes
        tagFilter
      )

      setMessages((prev) => [...prev, response.message])
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages((prev) => [
        ...prev,
        {
          role: 'system',
          content: 'Failed to get response. Please try again.',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }, [messages, useNotes, tagFilter])

  return {
    messages,
    sendMessage,
    isLoading,
  }
}
