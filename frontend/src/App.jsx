import { clsx } from 'clsx'
import { Bot, MoreHorizontal, Send, Settings, Sparkles, User } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

const ChatApp = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: "Hello! I'm your AI assistant. How can I help you today?",
      sender: 'ai',
      timestamp: new Date(),
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      const scrollHeight = textareaRef.current.scrollHeight
      const maxHeight = 120
      textareaRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`
    }
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [inputValue])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputValue }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const aiMessage = {
        id: Date.now() + 1,
        content: data.response,
        sender: 'ai',
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: Date.now() + 1,
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'ai',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage()
  }

  return (
    <div className="h-screen w-full relative overflow-hidden">
      {/* Animated Background */}
      <div className="w-full h-full bg-gradient-to-br from-primary-50 via-sage-50 to-mint-50">
        {/* Floating Orbs */}
        <div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-gradient-to-r from-mint-400/20 to-primary-400/20 rounded-full blur-3xl"></div>

        {/* Glassmorphic Triangles */}
        <svg className="absolute top-0 left-0 w-full h-full" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
          <defs>
            <linearGradient id="triangleGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#5f9c4a" stopOpacity="0.05" />
              <stop offset="100%" stopColor="#73a169" stopOpacity="0.03" />
            </linearGradient>
            <linearGradient id="triangleGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#39c491" stopOpacity="0.04" />
              <stop offset="100%" stopColor="#5f9c4a" stopOpacity="0.02" />
            </linearGradient>
          </defs>
          {/* Large background triangles */}
          <path d="M 0 0 L 600 0 L 300 520 Z" fill="url(#triangleGradient1)" />
          <path d="M 1920 1080 L 1920 580 L 1420 1080 Z" fill="url(#triangleGradient2)" />
          <path d="M 960 0 L 1260 0 L 1110 300 Z" fill="url(#triangleGradient1)" />
          <path d="M 0 1080 L 0 780 L 300 1080 Z" fill="url(#triangleGradient2)" />
          <path d="M 1600 200 L 1920 0 L 1920 400 Z" fill="url(#triangleGradient1)" opacity="0.5" />
          <path d="M 400 600 L 600 800 L 200 800 Z" fill="url(#triangleGradient2)" opacity="0.5" />
        </svg>

        {/* Grid Pattern */}
        <div className="absolute top-0 left-0 w-full h-full bg-grid-pattern opacity-[0.02]"></div>
      </div>

      {/* Main Content */}
      <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center p-4">
        {/* Chat Container */}
        <div className="relative z-10 w-full max-w-4xl h-full max-h-screen glass-morphism-container rounded-2xl shadow-glass border border-white/20 flex flex-col overflow-hidden backdrop-blur-2xl mx-auto">
          {/* Header */}
          <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 glass-header border-b border-white/10">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 via-sage-500 to-forest-600 flex items-center justify-center shadow-glow-primary">
                  <Sparkles className="w-6 h-6 text-white drop-shadow-sm" />
                </div>
                <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-gradient-to-r from-sage-400 to-primary-500 rounded-full border-2 border-white shadow-sm">
                  <div className="w-full h-full rounded-full bg-white/20"></div>
                </div>
              </div>
              <div>
                <h1 className="text-lg font-bold gradient-text-primary">
                  AI Assistant
                </h1>
                <p className="text-xs text-primary-600 font-semibold flex items-center">
                  <div className="w-2 h-2 bg-primary-400 rounded-full mr-2 shadow-sm"></div>
                  Online & Ready
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button className="w-9 h-9 rounded-lg glass-button-secondary hover:glass-button-secondary-hover flex items-center justify-center transition-all duration-300 group">
                <Settings className="w-4 h-4 text-gray-600 group-hover:text-gray-800 transition-colors" />
              </button>
              <button className="w-9 h-9 rounded-lg glass-button-secondary hover:glass-button-secondary-hover flex items-center justify-center transition-all duration-300 group">
                <MoreHorizontal className="w-4 h-4 text-gray-600 group-hover:text-gray-800 transition-colors" />
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4 messages-container min-h-0">
            {messages.map((message) => (
              <div
                key={message.id}
                className={clsx(
                  'flex items-start space-x-3 group',
                  message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                )}
              >
                {/* Avatar */}
                <div
                  className={clsx(
                    'w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-glow',
                    message.sender === 'ai'
                      ? 'bg-gradient-to-br from-primary-500 via-sage-500 to-forest-600 shadow-glow-primary'
                      : 'bg-gradient-to-br from-primary-500 via-sage-500 to-forest-600 shadow-glow-primary'
                  )}
                >
                  {message.sender === 'ai' ? (
                    <Bot className="w-5 h-5 text-white drop-shadow-sm" />
                  ) : (
                    <User className="w-5 h-5 text-white drop-shadow-sm" />
                  )}
                </div>

                {/* Message Content */}
                <div className={clsx(
                  'flex flex-col max-w-[75%]',
                  message.sender === 'user' ? 'items-end' : 'items-start'
                )}>
                  {/* Message Bubble */}
                  <div
                    className={clsx(
                      'px-3 py-2 rounded-xl text-sm leading-relaxed shadow-message backdrop-blur-md transition-all duration-300 group-hover:shadow-message-hover relative overflow-hidden',
                      message.sender === 'user'
                        ? 'bg-gradient-to-br from-primary-500 via-sage-500 to-forest-600 text-white rounded-br-md shadow-glow-primary-soft'
                        : 'glass-message text-gray-800 rounded-bl-md border border-white/20'
                    )}
                  >

                    <p className="whitespace-pre-wrap relative z-10">{message.content}</p>
                  </div>

                  {/* Timestamp */}
                  <span className="text-xs text-gray-400 mt-1 px-1 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-1 group-hover:translate-y-0">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex items-start space-x-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 via-sage-500 to-forest-600 flex items-center justify-center shadow-glow-primary">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="glass-message px-3 py-2 rounded-xl rounded-bl-md shadow-message border border-white/20">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                    <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                    <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="flex-shrink-0 p-5 glass-footer border-t border-white/10">
            <form onSubmit={handleSubmit}>
              <div className="relative">
                <div className="glass-input-container rounded-xl shadow-input">
                  <div className="flex items-end px-3 py-2">
                    <div className="flex-1 relative">
                      <textarea
                        ref={textareaRef}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your message..."
                        className="w-full resize-none border-0 bg-transparent text-gray-800 placeholder-gray-400 focus:ring-0 focus:outline-none text-sm leading-6 mr-3 font-medium"
                        rows={1}
                        style={{ maxHeight: '120px' }}
                      />


                    </div>

                    {/* Send Button */}
                    <button
                      type="submit"
                      disabled={!inputValue.trim() || isLoading}
                      className={clsx(
                        'w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-300 shadow-button relative overflow-hidden',
                        !inputValue.trim() || isLoading
                          ? 'glass-button-disabled cursor-not-allowed'
                          : 'glass-button-primary hover:shadow-button-hover group/btn'
                      )}
                    >


                      <Send className={clsx(
                        'w-4 h-4 transition-all duration-300 relative z-10',
                        !inputValue.trim() || isLoading
                          ? 'text-gray-400'
                          : 'text-white drop-shadow-sm group-hover/btn:translate-x-0.5'
                      )} />
                    </button>
                  </div>
                </div>

                {/* Character count */}
                {inputValue.length > 0 && (
                  <div className="absolute right-2 -bottom-4 text-xs text-gray-400 font-medium">
                    {inputValue.length} characters
                  </div>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatApp
