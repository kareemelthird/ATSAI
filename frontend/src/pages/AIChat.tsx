import { useState, useEffect, useRef } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { aiApi, api } from '@/lib/api'
import { Send, Bot, Download, User, Trash2, AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface CandidateInfo {
  id: string
  name: string
}

interface Message {
  role: string
  content: string
  candidates?: CandidateInfo[]
  timestamp?: Date
}

interface Conversation {
  id: string
  messages: Message[]
  title: string
  created_at: string
}

const AIChat = () => {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  // Detect if text is Arabic
  const isArabic = (text: string) => {
    const arabicPattern = /[\u0600-\u06FF]/
    return arabicPattern.test(text)
  }

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Save conversation to local storage
  const saveConversation = () => {
    if (messages.length === 0) return
    
    const conversationTitle = messages[0]?.content?.substring(0, 50) + '...' || 'New Conversation'
    const conversation: Conversation = {
      id: currentConversationId || Date.now().toString(),
      messages: messages.map(msg => ({
        ...msg,
        timestamp: msg.timestamp || new Date()
      })),
      title: conversationTitle,
      created_at: new Date().toISOString()
    }
    
    const saved = localStorage.getItem('ai-conversations')
    const existing = saved ? JSON.parse(saved) : []
    const updated = existing.filter((c: Conversation) => c.id !== conversation.id)
    updated.unshift(conversation)
    
    // Keep only last 20 conversations
    const limited = updated.slice(0, 20)
    localStorage.setItem('ai-conversations', JSON.stringify(limited))
    setConversations(limited)
    setCurrentConversationId(conversation.id)
  }

  // Load conversations from local storage
  useEffect(() => {
    const saved = localStorage.getItem('ai-conversations')
    if (saved) {
      setConversations(JSON.parse(saved))
    }
  }, [])

  // Save conversation when messages change
  useEffect(() => {
    if (messages.length > 0) {
      saveConversation()
    }
  }, [messages])

  const clearAllConversations = () => {
    localStorage.removeItem('ai-conversations')
    setConversations([])
    setMessages([])
    setCurrentConversationId(null)
  }

  const loadConversation = (conversation: Conversation) => {
    setMessages(conversation.messages)
    setCurrentConversationId(conversation.id)
  }

  const startNewConversation = () => {
    setMessages([])
    setCurrentConversationId(null)
  }

  // Check if user has personal API key configured
  const { data: aiSettings } = useQuery({
    queryKey: ['profile-ai-settings'],
    queryFn: async () => {
      const response = await api.get('/profile/ai-settings')
      return response.data
    }
  })

  const deleteMutation = useMutation({
    mutationFn: () => aiApi.deleteAllQueries('anonymous'),
    onSuccess: () => {
      // Clear local messages and conversations
      clearAllConversations()
      // Refresh history from server
      queryClient.invalidateQueries({ queryKey: ['ai-history'] })
    },
  })

  const chatMutation = useMutation({
    mutationFn: (queryText: string) => {
      // Prepare conversation history (exclude candidates from history to keep it lightweight)
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))
      
      return aiApi.chat(queryText, history)
    },
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { 
          role: 'assistant', 
          content: data.data.response,
          candidates: data.data.candidates || [],
          timestamp: new Date()
        },
      ])
    },
    onError: (error: any) => {
      // Extract error message from API response
      const errorMessage = error.response?.data?.detail || error.message || 'An error occurred'
      const status = error.response?.status
      
      let userFriendlyMessage = ''
      if (status === 429) {
        userFriendlyMessage = 'You have reached your daily limit for AI messages. Please try again tomorrow or add your personal Groq API key for unlimited access.'
      } else if (status === 403) {
        userFriendlyMessage = 'Access denied. You may need to add your personal Groq API key in Profile settings.'
      } else {
        userFriendlyMessage = 'Please try again or contact support if the problem persists.'
      }
      
      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        { 
          role: 'assistant', 
          content: `❌ Error: ${errorMessage}\n\n${userFriendlyMessage}${
            status === 429 || status === 403 ? '\n\n👉 Go to Profile → AI Settings to add your free Groq API key' : ''
          }`
        },
      ])
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setMessages((prev) => [...prev, { 
      role: 'user', 
      content: query,
      timestamp: new Date()
    }])
    chatMutation.mutate(query)
    setQuery('')
  }

  // Format AI response text - preserve line breaks and format properly
  const formatResponse = (text: string) => {
    // Detect language for RTL support
    const isRtl = isArabic(text)
    
    // Remove asterisks and clean up formatting
    let formatted = text.replace(/\*+/g, '')
    
    // Split by double line breaks for paragraphs, or single for simple breaks
    const paragraphs = formatted.split(/\n\n+/).filter(p => p.trim())
    
    return (
      <div dir={isRtl ? 'rtl' : 'ltr'} className={isRtl ? 'text-right' : 'text-left'}>
        {paragraphs.map((para, idx) => {
          // Check if it's a bullet point
          if (para.trim().startsWith('•') || para.trim().startsWith('-')) {
            const items = para.split('\n').filter(i => i.trim())
            return (
              <ul key={idx} className="mb-4 space-y-2 list-disc list-inside">
                {items.map((item, i) => (
                  <li key={i} className="leading-relaxed">
                    {item.replace(/^[•\-]\s*/, '')}
                  </li>
                ))}
              </ul>
            )
          }
          
          // Regular paragraph with preserved line breaks
          return (
            <p key={idx} className="mb-4 last:mb-0 leading-relaxed whitespace-pre-wrap">
              {para.trim()}
            </p>
          )
        })}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI Chat Assistant</h1>
          {messages.length > 0 && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {messages.filter(m => m.role === 'user').length} messages in conversation
            </p>
          )}
        </div>
        {messages.length > 0 && (
          <button
            onClick={() => {
              if (window.confirm('Delete current conversation? This will clear all messages in this chat.')) {
                startNewConversation()
              }
            }}
            className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            Clear Chat
          </button>
        )}
      </div>

      {/* API Key Warning Banner */}
      {aiSettings && (!aiSettings.has_personal_key || !aiSettings.use_personal_ai_key) && (
        <div className="mb-6 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 p-4 rounded-lg">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-1">
                ⚠️ Limited System API Usage
              </h3>
              <p className="text-sm text-yellow-700 dark:text-yellow-300 mb-2">
                AI Chat is using the system API key with very limited usage. For unlimited queries, 
                add your free personal Groq API key.
              </p>
              <Link
                to="/profile"
                className="inline-flex items-center px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium rounded transition-colors"
              >
                🔑 Add Personal Key (Free)
              </Link>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Area - Full Height */}
        <div className="lg:col-span-2">
          <div className="card" style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
            {/* Messages Area - Scrollable */}
            <div className="flex-1 overflow-y-auto space-y-4 p-4">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-500 dark:text-gray-400">
                    <Bot className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium">Ask me anything about candidates!</p>
                    <p className="text-sm mt-2">
                      English: &quot;Find me a senior document controller&quot;
                    </p>
                    <p className="text-sm mt-1 font-arabic">
                      العربية: &quot;ابحث لي عن مراقب مستندات أول&quot;
                    </p>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[85%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                        {/* Avatar */}
                        <div className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                            msg.role === 'user' 
                              ? 'bg-primary-600' 
                              : 'bg-purple-600'
                          }`}>
                            {msg.role === 'user' ? (
                              <User className="w-5 h-5 text-white" />
                            ) : (
                              <Bot className="w-5 h-5 text-white" />
                            )}
                          </div>
                          
                          <div className={`flex-1 ${msg.role === 'user' ? 'text-right' : ''}`}>
                            <div
                              className={`inline-block p-4 rounded-2xl shadow-sm ${
                                msg.role === 'user'
                                  ? 'bg-primary-600 text-white rounded-tr-none'
                                  : msg.content.startsWith('❌ Error:')
                                  ? 'bg-red-50 dark:bg-red-900/20 border-2 border-red-300 dark:border-red-700 text-red-900 dark:text-red-100 rounded-tl-none'
                                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-tl-none'
                              }`}
                              style={{ 
                                maxWidth: '100%',
                                direction: isArabic(msg.content) ? 'rtl' : 'ltr'
                              }}
                            >
                              {msg.role === 'user' ? (
                                <p className="whitespace-pre-wrap leading-relaxed">
                                  {msg.content}
                                </p>
                              ) : (
                                <div className="prose prose-sm dark:prose-invert max-w-none">
                                  {formatResponse(msg.content)}
                                </div>
                              )}
                            </div>
                            
                            {/* Download CV buttons for related candidates */}
                            {msg.role === 'assistant' && msg.candidates && msg.candidates.length > 0 && (
                              <div className="mt-3 flex flex-wrap gap-2">
                                {msg.candidates.map((candidate) => (
                                  <a
                                    key={candidate.id}
                                    href={`${API_BASE_URL}/api/v1/candidates/${candidate.id}/resume/download`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    download
                                    className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-300 border border-primary-300 dark:border-primary-700 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-800 transition-colors"
                                  >
                                    <Download className="w-3.5 h-3.5" />
                                    <span>Download CV - {candidate.name}</span>
                                  </a>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </>
              )}
              {chatMutation.isPending && (
                <div className="flex justify-start">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg rounded-tl-none">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input Form - Always visible at bottom */}
            <form onSubmit={handleSubmit} className="flex-shrink-0 flex gap-2 p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask in English or Arabic... اسأل بالعربية أو الإنجليزية"
                className="input flex-1 text-base"
                style={{ direction: isArabic(query) ? 'rtl' : 'ltr' }}
                disabled={chatMutation.isPending}
              />
              <button
                type="submit"
                disabled={chatMutation.isPending || !query.trim()}
                className="btn-primary flex items-center gap-2 px-6"
              >
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </form>
          </div>
        </div>

        {/* Conversation History Sidebar */}
        <div className="lg:col-span-1">
          <div className="card" style={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Conversations
              </h2>
              <div className="flex gap-2">
                <button
                  onClick={startNewConversation}
                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  New Chat
                </button>
                {conversations.length > 0 && (
                  <button
                    onClick={() => {
                      if (window.confirm('Delete all conversation history? This cannot be undone.')) {
                        clearAllConversations()
                      }
                    }}
                    className="text-xs text-red-600 hover:text-red-700 dark:hover:text-red-400 transition-colors"
                    title="Delete all conversations"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
              Click to load a previous conversation
            </p>
            <div className="flex-1 overflow-y-auto space-y-3">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    currentConversationId === conversation.id
                      ? 'bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800'
                      : 'bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                  onClick={() => loadConversation(conversation)}
                >
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-1 line-clamp-2">
                    {conversation.title}
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                    {conversation.messages.length} messages
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                    <span>{new Date(conversation.created_at).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>{new Date(conversation.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </p>
                </div>
              ))}
              {conversations.length === 0 && (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  <p className="text-sm">No conversations yet</p>
                  <p className="text-xs mt-1">Start chatting to see history!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AIChat
