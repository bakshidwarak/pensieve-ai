import { useState } from 'react'
import ChatInterface from '../components/ChatInterface'
import { useChat } from '../hooks/useChat'
import './ChatPage.css'

function ChatPage() {
  const { messages, sendMessage, isLoading } = useChat()

  return (
    <div className="chat-page">
      <header className="chat-header">
        <h2>Pensieve.ai Chat</h2>
        <p>Ask questions, get insights</p>
      </header>

      <div className="chat-container">
        <ChatInterface
          messages={messages}
          onSendMessage={sendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}

export default ChatPage
