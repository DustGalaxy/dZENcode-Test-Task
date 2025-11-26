import { api } from '../utils/api'
import type { Comment, CommentsResponse, CommentParams } from '../types/api'

export const commentsApi = {
  getAll: (params: CommentParams = {}) => {
    const queryParams = new URLSearchParams()
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.ordering) queryParams.append('ordering', params.ordering)
    if (params.search) queryParams.append('search', params.search)

    return api.get<CommentsResponse>(`/comments/?${queryParams.toString()}`)
  },

  getById: (id: number) => {
    return api.get<Comment>(`/comments/${id}/`)
  },

  create: (formData: FormData) => {
    return api.post<Comment>('/comments/', formData)
  },

  preview: (text: string, recaptchaToken: string) => {
    return api.post<{ text: string, recaptcha_token: string }>('/comments/preview-text/', { text, recaptcha_token: recaptchaToken })
  }
}
