import { api } from '../utils/api'
import type { Comment, CommentsResponse, CommentParams } from '../types/api'

export const commentsApi = {
  getAll: (params: CommentParams = {}) => {
    const queryParams = new URLSearchParams()
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.ordering) queryParams.append('ordering', params.ordering)
    if (params.search) queryParams.append('search', params.search)

    return api.get<CommentsResponse>(`/api/comments/?${queryParams.toString()}`)
  },

  getById: (id: number) => {
    return api.get<Comment>(`/api/comments/${id}/`)
  },

  create: (formData: FormData) => {
    return api.post<Comment>('/api/comments/', formData)
  },

  preview: (text: string) => {
    return api.post<{ text: string }>('/api/comments/preview-text/', { text })
  }
}
