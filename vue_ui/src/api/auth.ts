/**
 * API методы для аутентификации
 */

import type { LoginCredentials, TokenResponse, RegistrationCredentials, User } from '../types/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

/**
 * Логин пользователя
 */
export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/token/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }))
    throw new Error(error.detail || 'Invalid credentials')
  }

  return response.json()
}

/**
 * Обновление access токена с помощью refresh токена
 */
export async function refreshAccessToken(refreshToken: string): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/token/refresh/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh: refreshToken }),
  })

  if (!response.ok) {
    throw new Error('Failed to refresh token')
  }

  return response.json()
}

export async function getCurrentUser(accessToken: string): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/user/me/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error('Failed to fetch user data')
  }

  return response.json()
}

export async function register(userData: RegistrationCredentials): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/user/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Registration failed' }))
    throw new Error(error.detail || 'Registration failed')
  }

  return response.json()
}
