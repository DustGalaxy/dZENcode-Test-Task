import type { User } from './auth'

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
