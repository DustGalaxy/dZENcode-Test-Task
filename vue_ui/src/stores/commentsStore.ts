import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './authStore'
import { commentsApi } from '../api/comments'
import type { Comment } from '../types/comments'

const API_HOST = import.meta.env.VITE_API_HOST

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



  // Fetch top-level comments
  const fetchComments = async (page = 1, ordering?: string, search?: string) => {
    loading.value = true
    error.value = null
    
    if (ordering !== undefined) currentSort.value = ordering
    if (search !== undefined) currentSearch.value = search
    currentPage.value = page

    try {
      const response = await commentsApi.getAll({
        page,
        ordering: currentSort.value,
        search: currentSearch.value
      })
      comments.value = response.results
      totalComments.value = response.count
      
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
      const data = await commentsApi.getById(id)
      currentComment.value = data
    } catch (err: any) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // Create a new comment or reply
  const addComment = async (text: string, replyTo: number | null = null, files: File[] = [], recaptchaToken: string) => {
    loading.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.append('text', text)
      formData.append('recaptcha_token', recaptchaToken)
      if (replyTo) {
        formData.append('reply', replyTo.toString())
      }
      files.forEach((file) => {
        formData.append('attachments', file)
      })
      
      const newComment = await commentsApi.create(formData)
      
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

    let wsUrl = `ws://${API_HOST}/ws/comments/${commentId}/`
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
