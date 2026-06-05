import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  X, 
  Bot, 
  User, 
  FileText, 
  Activity,
  Heart,
  Brain,
  Pill
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const ChatBot = ({ isOpen, onClose }) => {
  const { user } = useAuth()
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: `Hello ${user?.name || 'there'}! I'm Clare, your AI healthcare assistant. I'm here to help you understand your medical reports, medications, and answer any health-related questions. How can I assist you today?`,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const [sessionId, setSessionId] = useState(null) // State to hold the session ID
  const [showHistory, setShowHistory] = useState(false) // State to show/hide chat history
  const [chatHistory, setChatHistory] = useState([]) // State to hold chat history
  const [selectedSession, setSelectedSession] = useState(null) // State to hold selected session for viewing
  const [showSessionPopup, setShowSessionPopup] = useState(false) // State to show/hide session popup
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false) // State to show/hide delete confirmation
  const [sessionToDelete, setSessionToDelete] = useState(null) // State to hold session ID to delete
  const [availableReports, setAvailableReports] = useState([]) // State to hold available reports
  const [selectedReport, setSelectedReport] = useState(null) // State to hold selected report for context

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  // Fetch available reports when chat opens
  useEffect(() => {
    if (isOpen) {
      fetchReports()
    }
  }, [isOpen])

  const fetchReports = async () => {
    try {
      const response = await fetch('http://localhost:5000/reports', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setAvailableReports(data.reports || [])
      }
    } catch (error) {
      console.error('Failed to fetch reports:', error)
    }
  }

  // Healthcare-focused responses
  const healthcareResponses = {
    greetings: [
      "Hello! I'm here to help with your health questions. What would you like to know?",
      "Hi there! I'm Clare, your AI healthcare assistant. How can I help you today?",
      "Welcome! I'm ready to assist you with any medical questions or concerns."
    ],
    medications: [
      "I can help explain your medications, but always consult your doctor for medical advice. What medication would you like to know more about?",
      "Medication information is important. I can provide general information, but please discuss any concerns with your healthcare provider.",
      "I'm here to help you understand your medications better. What specific medication are you asking about?"
    ],
    symptoms: [
      "I can help you understand symptoms, but I cannot diagnose. Please consult a healthcare professional for proper diagnosis.",
      "While I can provide general information about symptoms, it's important to see a doctor for proper evaluation.",
      "I'm here to help you understand symptoms, but remember to seek professional medical advice for diagnosis."
    ],
    reports: [
      "I can help you understand medical terminology in your reports. Which part would you like me to explain?",
      "Medical reports can be confusing. I'm here to break down the terminology for you. What specific terms do you need help with?",
      "I can help translate medical jargon into simple terms. What report are you looking at?"
    ],
    default: [
      "I'm here to help with your health questions. Could you please provide more details?",
      "I want to make sure I understand your question correctly. Can you rephrase that?",
      "I'm your healthcare assistant. How can I help you better understand your health information?"
    ]
  }

  const getResponse = (message) => {
    const lowerMessage = message.toLowerCase()
    
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
      return healthcareResponses.greetings[Math.floor(Math.random() * healthcareResponses.greetings.length)]
    }
    
    if (lowerMessage.includes('medication') || lowerMessage.includes('medicine') || lowerMessage.includes('pill') || lowerMessage.includes('drug')) {
      return healthcareResponses.medications[Math.floor(Math.random() * healthcareResponses.medications.length)]
    }
    
    if (lowerMessage.includes('symptom') || lowerMessage.includes('pain') || lowerMessage.includes('ache') || lowerMessage.includes('fever')) {
      return healthcareResponses.symptoms[Math.floor(Math.random() * healthcareResponses.symptoms.length)]
    }
    
    if (lowerMessage.includes('report') || lowerMessage.includes('test result') || lowerMessage.includes('lab') || lowerMessage.includes('diagnosis')) {
      return healthcareResponses.reports[Math.floor(Math.random() * healthcareResponses.reports.length)]
    }
    
    return healthcareResponses.default[Math.floor(Math.random() * healthcareResponses.default.length)]
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    try {
      // Send message to our AI backend
      const response = await fetch('http://localhost:5000/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include', // Include JWT cookies
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId, // Use existing session if available
          selected_report_id: selectedReport?._id // Include selected report for context
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        // Update session ID if this is a new session
        if (data.session_id && !sessionId) {
          setSessionId(data.session_id)
        }

        const aiMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: data.reply,
          timestamp: new Date(),
          metadata: {
            used_context: data.used_context,
            model: data.model
          }
        }

        setMessages(prev => [...prev, aiMessage])
      } else {
        // Fallback to mock response if AI fails
        const fallbackResponse = getResponse(userMessage.content)
        const aiMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: fallbackResponse,
          timestamp: new Date(),
          metadata: { fallback: true }
        }
        setMessages(prev => [...prev, aiMessage])
      }
    } catch (error) {
      console.error('AI chat error:', error)
      // Fallback to mock response
      const fallbackResponse = getResponse(userMessage.content)
      const aiMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: fallbackResponse,
        timestamp: new Date(),
        metadata: { fallback: true }
      }
      setMessages(prev => [...prev, aiMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const loadChatHistory = async () => {
    try {
      const response = await fetch('http://localhost:5000/chat/sessions', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setChatHistory(data.sessions || [])
      }
    } catch (error) {
      console.error('Failed to load chat history:', error)
    }
  }

  const loadChatSession = async (sessionId) => {
    try {
      const response = await fetch(`http://localhost:5000/chat/sessions/${sessionId}`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        setSelectedSession(data.session)
        setShowSessionPopup(true)
      }
    } catch (error) {
      console.error('Failed to load chat session:', error)
    }
  }

  const confirmDeleteSession = (sessionId) => {
    setSessionToDelete(sessionId)
    setShowDeleteConfirm(true)
  }

  const deleteChatSession = async () => {
    if (!sessionToDelete) return
    
    try {
      const response = await fetch(`http://localhost:5000/chat/sessions/${sessionToDelete}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      
      if (response.ok) {
        // Remove from local state
        setChatHistory(prev => prev.filter(session => session._id !== sessionToDelete))
        // If current session is deleted, clear it
        if (sessionToDelete === sessionId) {
          setSessionId(null)
          setMessages([{
            id: Date.now(),
            type: 'bot',
            content: `Hello ${user?.name || 'there'}! I'm Clare, your AI healthcare assistant. How can I assist you today?`,
            timestamp: new Date()
          }])
        }
        // Close popup if it was open
        if (selectedSession && selectedSession._id === sessionToDelete) {
          setShowSessionPopup(false)
          setSelectedSession(null)
        }
      }
    } catch (error) {
      console.error('Failed to delete chat session:', error)
    } finally {
      setShowDeleteConfirm(false)
      setSessionToDelete(null)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const quickActions = [
    { icon: Pill, text: "Medication Info", action: "Can you explain my medications?" },
    { icon: FileText, text: "Report Analysis", action: "Help me understand my medical report" },
    { icon: Activity, text: "Symptom Check", action: "I have some symptoms to discuss" },
    { icon: Heart, text: "Health Tips", action: "Give me some health tips" }
  ]

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          key="chatbot-main"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className="fixed top-4 right-4 z-50 w-[450px] h-[calc(100vh-2rem)] sm:w-[500px] sm:h-[calc(100vh-2rem)] lg:w-[40vw] lg:h-[calc(100vh-2rem)] xl:w-[35vw] xl:h-[calc(100vh-2rem)] 2xl:w-[30vw] 2xl:h-[calc(100vh-2rem)] bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-healthcare-500 to-primary-500 rounded-t-2xl">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-healthcare-500" />
              </div>
              <div>
                <h3 className="text-white font-semibold">Clare AI Assistant</h3>
                <p className="text-xs text-white/80">Healthcare Support</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => {
                  setShowHistory(!showHistory)
                  if (!showHistory) {
                    loadChatHistory()
                  }
                }}
                className="p-1 rounded-full hover:bg-white/20 transition-colors text-white"
                title="Chat History"
              >
                <FileText className="w-4 h-4" />
              </button>
              <button
                onClick={onClose}
                className="p-1 rounded-full hover:bg-white/20 transition-colors"
              >
                <X className="w-4 h-4 text-white" />
              </button>
            </div>
          </div>

          {/* Report Selection Panel */}
          {availableReports.length > 0 && (
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
              <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                📄 Ask about a specific report:
              </label>
              <select
                value={selectedReport?._id || ''}
                onChange={(e) => {
                  const report = availableReports.find(r => r._id === e.target.value)
                  setSelectedReport(report)
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              >
                <option value="">General conversation (no report)</option>
                {availableReports.map(report => (
                  <option key={report._id} value={report._id}>
                    {report.reportName || report.fileName} ({new Date(report.createdAt).toLocaleDateString()})
                  </option>
                ))}
              </select>
              
              {selectedReport && (
                <div className="mt-2 flex items-center justify-between p-2 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                    <span className="text-xs text-primary-700 dark:text-primary-300">
                      Chatting about: <strong>{selectedReport.reportName}</strong>
                    </span>
                  </div>
                  <button
                    onClick={() => setSelectedReport(null)}
                    className="text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-200 transition-colors"
                    title="Clear selection"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Chat History Panel */}
          {showHistory && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700"
            >
              <div className="p-4">
                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Chat History</h4>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {chatHistory.length === 0 ? (
                    <p className="text-xs text-gray-500 dark:text-gray-400">No previous chats</p>
                  ) : (
                    chatHistory.map((session) => (
                      <div key={session._id} className="flex items-center justify-between p-2 bg-white dark:bg-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-500 transition-colors">
                        <div 
                          className="flex-1 min-w-0 cursor-pointer"
                          onClick={() => loadChatSession(session._id)}
                        >
                          <p className="text-xs text-gray-900 dark:text-white truncate">
                            {formatDate(session.startedAt)}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {session.messageCount ? `${session.messageCount} messages` : 'No messages'}
                          </p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            confirmDeleteSession(session._id)
                          }}
                          className="ml-2 p-1 text-red-500 hover:bg-red-100 dark:hover:bg-red-900 rounded"
                          title="Delete chat"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-2xl ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </motion.div>
            ))}
            
            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-2xl">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          {messages.length === 1 && (
            <div className="px-4 pb-2">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Quick actions:</p>
              <div className="grid grid-cols-2 gap-2">
                {quickActions.map((action, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setInputValue(action.action)}
                    className="flex items-center space-x-2 p-2 text-xs bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    <action.icon className="w-3 h-3" />
                    <span>{action.text}</span>
                  </motion.button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about your health..."
                className="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isTyping}
                className="p-2 bg-gradient-to-r from-healthcare-500 to-primary-500 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
              </motion.button>
            </div>
          </div>

          {/* Static Disclaimer */}
          <div className="px-4 pb-3">
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3">
              <div className="flex items-start space-x-2">
                <div className="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0">
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="text-xs text-amber-800 dark:text-amber-200">
                  <p className="font-medium mb-1">Medical Disclaimer</p>
                  <p>I am an AI assistant and cannot replace professional medical advice. For urgent or critical issues, please consult a doctor immediately.</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Chat Session Popup */}
      <AnimatePresence>
        {showSessionPopup && selectedSession && (
          <motion.div
            key="session-popup"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={() => setShowSessionPopup(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl h-[80vh] flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Popup Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-healthcare-500 to-primary-500 rounded-t-2xl">
                <div>
                  <h3 className="text-white font-semibold">Chat History</h3>
                  <p className="text-xs text-white/80">
                    {formatDate(selectedSession.startedAt)}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => confirmDeleteSession(selectedSession._id)}
                    className="p-2 text-red-300 hover:text-red-100 hover:bg-red-500/20 rounded-lg transition-colors"
                    title="Delete this chat"
                  >
                    <X className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setShowSessionPopup(false)}
                    className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {selectedSession.messages && selectedSession.messages.length > 0 ? (
                  selectedSession.messages.map((message, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] p-3 rounded-2xl ${
                          message.sender === 'user'
                            ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {new Date(message.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500 dark:text-gray-400">No messages in this chat</p>
                  </div>
                )}
              </div>

              {/* Popup Footer */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>
                    {selectedSession.messageCount} messages
                  </span>
                  <span>
                    Started: {formatDate(selectedSession.startedAt)}
                  </span>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Dialog */}
      <AnimatePresence>
        {showDeleteConfirm && (
          <motion.div
            key="delete-confirm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={() => setShowDeleteConfirm(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md p-6"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Confirmation Header */}
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
                  <X className="w-5 h-5 text-red-600 dark:text-red-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Delete Chat Session
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    This action cannot be undone
                  </p>
                </div>
              </div>

              {/* Confirmation Message */}
              <div className="mb-6">
                <p className="text-gray-700 dark:text-gray-300">
                  Are you sure you want to delete this chat session? All messages in this conversation will be permanently removed.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={deleteChatSession}
                  className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                  Delete
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AnimatePresence>
  )
}

export default ChatBot 