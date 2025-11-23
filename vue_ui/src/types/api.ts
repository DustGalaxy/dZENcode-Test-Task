import type { Comment } from './comments'

export type { Comment }

export interface CommentsResponse {
  count: number
  next: string | null
  previous: string | null
  results: Comment[]
}

export interface CommentParams {
  page?: number
  ordering?: string
  search?: string
}
