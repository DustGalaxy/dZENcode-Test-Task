export interface User {
  id: number
  username: string
  email: string
  home_page?: string
  created_at?: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegistrationCredentials {
  username: string
  email: string
  password: string
  password2: string
}

export interface TokenResponse {
  access: string
  refresh: string
}

export interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}
