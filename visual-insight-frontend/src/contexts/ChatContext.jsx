import { createContext, useContext, useState, useEffect } from 'react'
import { useAuth } from './AuthContext'

const ChatContext = createContext()

export function useChat() {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}

export function ChatProvider({ children }) {
  const { token, API_BASE_URL } = useAuth()
  const [conversations, setConversations] = useState([])
  const [currentConversation, setCurrentConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [typing, setTyping] = useState(false)

  const fetchConversations = async () => {
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/chat/conversations/`, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setConversations(data.results || data)
      }
    } catch (error) {
      console.error('Error fetching conversations:', error)
    }
  }

  const fetchMessages = async (conversationId) => {
    if (!token) return

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/chat/conversations/${conversationId}/messages/`, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setMessages(data.results || data)
      }
    } catch (error) {
      console.error('Error fetching messages:', error)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async (content, conversationId = null, videoId = null) => {
    if (!token) return

    setTyping(true)
    try {
      const response = await fetch(`${API_BASE_URL}/chat/send-message/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          conversation_id: conversationId,
          video_id: videoId,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        // Add user message immediately
        const userMessage = {
          id: Date.now(),
          content,
          sender: 'user',
          created_at: new Date().toISOString(),
        }
        setMessages(prev => [...prev, userMessage])

        // If this is a new conversation, update current conversation
        if (data.conversation_id && !conversationId) {
          setCurrentConversation({ id: data.conversation_id })
        }

        // Simulate AI response (in real implementation, this would come from the backend)
        setTimeout(() => {
          const aiResponse = generateMockAIResponse(content)
          const aiMessage = {
            id: Date.now() + 1,
            content: aiResponse,
            sender: 'assistant',
            created_at: new Date().toISOString(),
          }
          setMessages(prev => [...prev, aiMessage])
          setTyping(false)
        }, 1500)

        return { success: true, data }
      } else {
        setTyping(false)
        return { success: false, error: data.error || 'Failed to send message' }
      }
    } catch (error) {
      console.error('Send message error:', error)
      setTyping(false)
      return { success: false, error: 'Network error. Please try again.' }
    }
  }

  const generateMockAIResponse = (userMessage) => {
    const responses = [
      "I've analyzed your video and found several interesting events. Would you like me to highlight the most significant ones?",
      "Based on the video content, I detected some potential guideline violations. Let me show you the specific timestamps where these occurred.",
      "The video analysis is complete! I found multiple objects and activities. What specific aspect would you like to explore further?",
      "I can see there are some traffic patterns in your video. Would you like me to explain the movement patterns I detected?",
      "Great question! Let me break down the analysis results for you. I found several key events that might be of interest.",
      "I've processed the video and identified various events. The analysis shows some interesting patterns in the timeline.",
    ]
    
    return responses[Math.floor(Math.random() * responses.length)]
  }

  const createConversation = async (videoId = null) => {
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/chat/conversations/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_id: videoId }),
      })

      const data = await response.json()

      if (response.ok) {
        setConversations(prev => [data, ...prev])
        setCurrentConversation(data)
        setMessages([])
        return { success: true, data }
      } else {
        return { success: false, error: data.error || 'Failed to create conversation' }
      }
    } catch (error) {
      console.error('Create conversation error:', error)
      return { success: false, error: 'Network error. Please try again.' }
    }
  }

  const selectConversation = (conversation) => {
    setCurrentConversation(conversation)
    if (conversation) {
      fetchMessages(conversation.id)
    } else {
      setMessages([])
    }
  }

  useEffect(() => {
    if (token) {
      fetchConversations()
    }
  }, [token])

  const value = {
    conversations,
    currentConversation,
    messages,
    loading,
    typing,
    fetchConversations,
    fetchMessages,
    sendMessage,
    createConversation,
    selectConversation,
    setMessages,
  }

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  )
}

