import React, { createContext, useContext, useState } from 'react'

const ChatContext = createContext()

export const useChat = () => {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}

export const ChatProvider = ({ children }) => {
  const [chatOpen, setChatOpen] = useState(false)

  const openChat = () => setChatOpen(true)
  const closeChat = () => setChatOpen(false)
  const toggleChat = () => setChatOpen(!chatOpen)

  const value = {
    chatOpen,
    openChat,
    closeChat,
    toggleChat
  }

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  )
}
