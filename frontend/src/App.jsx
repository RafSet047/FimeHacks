import { clsx } from 'clsx'
import { AlertCircle, Bell, Bot, CheckCircle, Info, LogOut, Mic, MicOff, Send, Settings, Sparkles, User, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

const ChatApp = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: "What can I do for you, today?",
      sender: 'ai',
      timestamp: new Date(),
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)

  // Voice input states
  const [isRecording, setIsRecording] = useState(false)
  const [recognition, setRecognition] = useState(null)
  const [isVoiceSupported, setIsVoiceSupported] = useState(false)
  const [voiceError, setVoiceError] = useState('')

  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: "New Feature Available",
      message: "Check out the new document processing capabilities",
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      read: false,
      type: "feature"
    },
    {
      id: 2,
      title: "Processing Complete",
      message: "Your document 'research_paper.pdf' has been successfully processed",
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000), // 1 hour ago
      read: false,
      type: "success"
    },
    {
      id: 3,
      title: "System Update",
      message: "Cerebryx has been updated with improved response accuracy",
      timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
      read: true,
      type: "system"
    },
    {
      id: 4,
      title: "Upload Error",
      message: "Failed to upload 'large_file.pdf'. File size exceeds limit",
      timestamp: new Date(Date.now() - 10 * 60 * 1000), // 10 minutes ago
      read: false,
      type: "error"
    }
  ])
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  const dropdownRef = useRef(null)

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

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false)
        setShowNotifications(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognitionInstance = new SpeechRecognition()

      recognitionInstance.continuous = false
      recognitionInstance.interimResults = false
      recognitionInstance.lang = 'en-US'

      recognitionInstance.onstart = () => {
        setIsRecording(true)
        setVoiceError('')
      }

      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        setInputValue(prev => prev + transcript)
        setIsRecording(false)
      }

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setVoiceError(event.error)
        setIsRecording(false)
      }

      recognitionInstance.onend = () => {
        setIsRecording(false)
      }

      setRecognition(recognitionInstance)
      setIsVoiceSupported(true)
    } else {
      setIsVoiceSupported(false)
    }
  }, [])

  // Voice input functions
  const startVoiceRecording = () => {
    if (!recognition) return

    try {
      setVoiceError('')
      recognition.start()
    } catch (error) {
      console.error('Error starting voice recognition:', error)
      setVoiceError('Failed to start voice recognition')
    }
  }

  const stopVoiceRecording = () => {
    if (!recognition) return

    try {
      recognition.stop()
      setIsRecording(false)
    } catch (error) {
      console.error('Error stopping voice recognition:', error)
    }
  }

  // Clear voice error when user starts typing
  const handleInputChange = (e) => {
    setInputValue(e.target.value)
    if (voiceError) {
      setVoiceError('')
    }
  }

  // Clear voice error after a timeout
  useEffect(() => {
    if (voiceError) {
      const timeout = setTimeout(() => {
        setVoiceError('')
      }, 5000)
      return () => clearTimeout(timeout)
    }
  }, [voiceError])

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

  // Notification management functions
  const unreadNotifications = notifications.filter(n => !n.read)
  const unreadCount = unreadNotifications.length

  const markNotificationAsRead = (id) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    )
  }

  const markAllNotificationsAsRead = () => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    )
  }

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success': return CheckCircle
      case 'error': return AlertCircle
      case 'feature': return Sparkles
      case 'system': return Info
      default: return Bell
    }
  }

  const getNotificationColor = (type) => {
    switch (type) {
      case 'success': return 'text-green-600'
      case 'error': return 'text-red-600'
      case 'feature': return 'text-purple-600'
      case 'system': return 'text-blue-600'
      default: return 'text-gray-600'
    }
  }

  const formatTimeAgo = (timestamp) => {
    const now = new Date()
    const diff = now - timestamp
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return 'Just now'
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
        {/* Dropdown Menu - Outside chat container */}
      {isDropdownOpen && (
        <div className={clsx(
          "fixed bg-white rounded-xl shadow-lg border border-gray-200 animate-in slide-in-from-top-2 duration-200 z-[9999]",
          showNotifications ? "w-80" : "w-48"
        )}
        style={{
          top: '70px',
          right: '20px'
        }}>
          {!showNotifications ? (
            // Main menu
            <div className="p-2 space-y-1">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsDropdownOpen(false);
                  // Add your settings logic here
                }}
                className="w-full flex items-center space-x-3 px-3 py-2 text-sm text-gray-700 hover:bg-white/30 rounded-lg transition-all duration-200 group"
              >
                <Settings className="w-4 h-4 text-gray-600 group-hover:text-gray-800 transition-colors" />
                <span className="font-medium">Account Settings</span>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowNotifications(true);
                }}
                className="w-full flex items-center space-x-3 px-3 py-2 text-sm text-gray-700 hover:bg-white/30 rounded-lg transition-all duration-200 group"
              >
                <div className="relative">
                  <Bell className="w-4 h-4 text-gray-600 group-hover:text-gray-800 transition-colors" />
                  {unreadCount > 0 && (
                    <div className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </div>
                  )}
                </div>
                <span className="font-medium">Notifications</span>
              </button>
              <div className="border-t border-white/20 my-1"></div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsDropdownOpen(false);
                  // Add your logout logic here
                }}
                className="w-full flex items-center space-x-3 px-3 py-2 text-sm text-red-600 hover:bg-red-50/30 rounded-lg transition-all duration-200 group"
              >
                <LogOut className="w-4 h-4 text-red-500 group-hover:text-red-700 transition-colors" />
                <span className="font-medium">Logout</span>
              </button>
            </div>
          ) : (
            // Notifications panel
            <div className="p-3">
              {/* Notifications header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowNotifications(false);
                    }}
                    className="p-1 hover:bg-white/20 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4 text-gray-600" />
                  </button>
                  <h3 className="font-semibold text-gray-800">Notifications</h3>
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      markAllNotificationsAsRead();
                    }}
                    className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Mark all read
                  </button>
                )}
              </div>

              {/* Notifications list */}
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="text-center py-4 text-gray-500">
                    <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No notifications</p>
                  </div>
                ) : (
                  notifications.map((notification) => {
                    const IconComponent = getNotificationIcon(notification.type);
                    return (
                      <div
                        key={notification.id}
                        onClick={(e) => {
                          e.stopPropagation();
                          markNotificationAsRead(notification.id);
                        }}
                        className={clsx(
                          "p-3 rounded-lg cursor-pointer transition-all duration-200 hover:bg-white/20 border-l-4",
                          notification.read
                            ? "bg-white/5 border-l-gray-300"
                            : "bg-white/10 border-l-primary-500"
                        )}
                      >
                        <div className="flex items-start space-x-3">
                          <IconComponent className={clsx(
                            "w-5 h-5 mt-0.5 flex-shrink-0",
                            getNotificationColor(notification.type)
                          )} />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <h4 className={clsx(
                                "text-sm font-medium truncate",
                                notification.read ? "text-gray-600" : "text-gray-800"
                              )}>
                                {notification.title}
                              </h4>
                              {!notification.read && (
                                <div className="w-2 h-2 bg-primary-500 rounded-full flex-shrink-0 ml-2"></div>
                              )}
                            </div>
                            <p className={clsx(
                              "text-xs mt-1 line-clamp-2",
                              notification.read ? "text-gray-400" : "text-gray-600"
                            )}>
                              {notification.message}
                            </p>
                            <p className="text-xs text-gray-400 mt-1">
                              {formatTimeAgo(notification.timestamp)}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {/* View all notifications link */}
              {notifications.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/20">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsDropdownOpen(false);
                      setShowNotifications(false);
                      // Add logic to open full notifications page
                    }}
                    className="w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
                  >
                    View all notifications
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
          {/* Header */}
          <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 glass-header border-b border-white/10">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 via-sage-500 to-forest-600 flex items-center justify-center shadow-glow-primary overflow-hidden">
                  <img
                    src="/cerebryx-white-logo.png"
                    alt="Cerebryx"
                    className="w-8 h-8 object-contain drop-shadow-sm"
                  />
                </div>
              </div>
              <div>
                <h1 className="text-lg font-bold gradient-text-primary">
                  Cerebryx
                </h1>
                <p className="text-xs text-primary-600 font-semibold flex items-center">
                  <div className="w-2 h-2 bg-primary-400 rounded-full mr-2 shadow-sm"></div>
                  Ready to chat!
                </p>
              </div>
            </div>

            <div className="relative">
              <button
                ref={dropdownRef}
                onClick={(e) => {
                  e.stopPropagation();
                  setIsDropdownOpen(!isDropdownOpen);
                }}
                className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 via-sage-500 to-forest-600 flex items-center justify-center shadow-glow-primary hover:shadow-glow-primary-soft transition-all duration-300 group"
              >
                <User className="w-5 h-5 text-white drop-shadow-sm" />

                {/* Modern animated notification badge */}
                <div className="absolute -top-1 -right-1">
                  <div className="relative">
                    {/* Pulsing outer ring */}
                    <div className="absolute inset-0 w-3 h-3 bg-red-400 rounded-full animate-ping opacity-75"></div>
                    {/* Main badge */}
                    <div className="relative w-3 h-3 bg-gradient-to-r from-red-500 to-red-600 rounded-full flex items-center justify-center shadow-lg">
                      <div className="w-1 h-1 bg-white rounded-full animate-pulse"></div>
                    </div>
                    {/* Shine effect */}
                    <div className="absolute inset-0 w-3 h-3 bg-gradient-to-br from-white/40 to-transparent rounded-full opacity-60"></div>
                  </div>
                </div>
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
                        onChange={handleInputChange}
                        onKeyPress={handleKeyPress}
                        placeholder="Type your message..."
                        className="w-full resize-none border-0 bg-transparent text-gray-800 placeholder-gray-400 focus:ring-0 focus:outline-none text-sm leading-6 mr-3 font-medium"
                        rows={1}
                        style={{ maxHeight: '120px' }}
                      />
                    </div>

                    {/* Voice Input Button */}
                    {isVoiceSupported && (
                      <button
                        type="button"
                        onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                        className={clsx(
                          'w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-300 shadow-button relative overflow-hidden mr-2',
                          isRecording
                            ? 'bg-red-500 hover:bg-red-600 shadow-red-200'
                            : 'glass-morphism-container hover:shadow-button-hover group/voice border border-white/20'
                        )}
                        title={isRecording ? 'Stop recording' : 'Start voice input'}
                      >
                        {isRecording ? (
                          <MicOff className="w-4 h-4 text-white drop-shadow-sm animate-pulse" />
                        ) : (
                          <Mic className={clsx(
                            'w-4 h-4 transition-all duration-300 relative z-10',
                            'text-gray-600 group-hover/voice:text-gray-800'
                          )} />
                        )}
                      </button>
                    )}

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

                {/* Voice Recording Indicator */}
                {isRecording && (
                  <div className="absolute left-3 -bottom-8 flex items-center space-x-2 text-red-600">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-xs font-medium">Listening...</span>
                  </div>
                )}

                {/* Voice Error Message */}
                {voiceError && (
                  <div className="absolute left-3 -bottom-8 flex items-center space-x-2 text-red-600">
                    <AlertCircle className="w-3 h-3" />
                    <span className="text-xs font-medium">
                      {voiceError === 'not-allowed' ? 'Microphone access denied' :
                       voiceError === 'no-speech' ? 'No speech detected' :
                       'Voice input error'}
                    </span>
                  </div>
                )}

                {/* Voice Not Supported Message */}
                {!isVoiceSupported && (
                  <div className="absolute left-3 -bottom-8 text-xs text-gray-400 font-medium">
                    Voice input not supported in this browser
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
