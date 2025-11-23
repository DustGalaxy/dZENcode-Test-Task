import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './authStore'

export interface User {
  id: number
  username: string
  email: string
}

export interface Attachment {
  id: number
  file: string
  media_type: string
}

export interface Comment {
  id: number
  user: User
  text: string
  created_at: string
  updated_at: string
  reply: number | null
  replies?: Comment[]
  attachments?: Attachment[]
}

export const useCommentsStore = defineStore('comments', () => {
  const comments = ref<Comment[]>([])
  const totalComments = ref(0)
  const currentPage = ref(1)
  const currentSort = ref('-created_at')
  const currentSearch = ref('')
  const currentComment = ref<Comment | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const socket = ref<WebSocket | null>(null)

  const authStore = useAuthStore()

  // Helper to get headers with token
  const getHeaders = () => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }
    if (authStore.accessToken) {
      headers['Authorization'] = `Bearer ${authStore.accessToken}`
    }
    return headers
  }

  // Fetch top-level comments
  const fetchComments = async (page = 1, ordering?: string, search?: string) => {
    loading.value = true
    error.value = null
    
    if (ordering !== undefined) currentSort.value = ordering
    if (search !== undefined) currentSearch.value = search
    currentPage.value = page

    try {
      const queryParams = new URLSearchParams({
        page: page.toString(),
        ordering: currentSort.value,
      })
      
      if (currentSearch.value) {
        queryParams.append('search', currentSearch.value)
      }

      const response = await fetch(`http://127.0.0.1:8000/api/comments/?${queryParams.toString()}`, {
        headers: getHeaders(),
      })
      if (!response.ok) throw new Error('Failed to fetch comments')
      const data = await response.json()
      comments.value = data.results
      totalComments.value = data.count
      
    } catch (err: any) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // Fetch single comment with replies
  const fetchCommentDetail = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/comments/${id}/`, {
        headers: getHeaders(),
      })
      if (!response.ok) throw new Error('Failed to fetch comment detail')
      const data = await response.json()
      currentComment.value = data
    } catch (err: any) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // Create a new comment or reply
  const addComment = async (text: string, replyTo: number | null = null, files: File[] = []) => {
    loading.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.append('text', text)
      if (replyTo) {
        formData.append('reply', replyTo.toString())
      }
      files.forEach((file) => {
        formData.append('attachments', file)
      })

      const headers: HeadersInit = {}
      if (authStore.accessToken) {
        headers['Authorization'] = `Bearer ${authStore.accessToken}`
      }

      const response = await fetch('http://127.0.0.1:8000/api/comments/', {
        method: 'POST',
        headers: headers,
        body: formData,
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(JSON.stringify(errData))
      }
      
      const newComment = await response.json()
      
      // If it's a top-level comment, add to list
      if (!replyTo) {
        comments.value.unshift(newComment)
      }
      // If it's a reply, it might be handled by WebSocket, but we can optimistically add it if needed
      // For now, we rely on WebSocket or re-fetch for replies in detail view
      
      return newComment
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // WebSocket connection for real-time replies
  const connectWebSocket = (commentId: number) => {
    if (socket.value) {
      socket.value.close()
    }

    let wsUrl = `ws://127.0.0.1:8000/ws/comments/${commentId}/`
    if (authStore.accessToken) {
        wsUrl += `?token=${authStore.accessToken}`
    }
    socket.value = new WebSocket(wsUrl)

    socket.value.onopen = () => {
      console.log('WebSocket connected')
    }

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'new_reply' && currentComment.value && currentComment.value.id === commentId) {
        const newReply = data.data
        
        // Helper to recursively find parent and add reply
        const addReplyToTree = (comments: Comment[], reply: Comment): boolean => {
            // Check if reply belongs to any of these comments
            for (const comment of comments) {
                if (comment.id === reply.reply) {
                    if (!comment.replies) comment.replies = []
                    
                    // Check for duplicates
                    if (!comment.replies.find(r => r.id === reply.id)) {
                        comment.replies.push(reply)
                        // Sort by created_at
                        comment.replies.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
                    }
                    return true
                }
                
                // Recurse into children
                if (comment.replies && comment.replies.length > 0) {
                    if (addReplyToTree(comment.replies, reply)) return true
                }
            }
            return false
        }

        // If reply is direct child of current comment
        if (newReply.reply === currentComment.value.id) {
             if (!currentComment.value.replies) currentComment.value.replies = []
             if (!currentComment.value.replies.find(r => r.id === newReply.id)) {
                 currentComment.value.replies.push(newReply)
                 currentComment.value.replies.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
             }
        } else {
            // Try to find parent in the tree
            if (currentComment.value.replies) {
                addReplyToTree(currentComment.value.replies, newReply)
            }
        }
      }
    }

    socket.value.onerror = (err) => {
      console.error('WebSocket error:', err)
    }

    socket.value.onclose = () => {
      console.log('WebSocket disconnected')
    }
  }

  const disconnectWebSocket = () => {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
  }

  return {
    comments,
    totalComments,
    currentPage,
    currentSort,
    currentSearch,
    currentComment,
    loading,
    error,
    fetchComments,
    fetchCommentDetail,
    addComment,
    connectWebSocket,
    disconnectWebSocket
  }
})
