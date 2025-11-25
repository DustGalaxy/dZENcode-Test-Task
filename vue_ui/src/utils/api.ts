/**
 * API клиент с автоматической обработкой токенов
 * Используйте этот клиент для всех API запросов
 */

import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean
}

/**
 * Обертка над fetch с автоматической обработкой аутентификации
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { requiresAuth = true, headers = {}, ...fetchOptions } = options

  const url = `${API_BASE_URL}${endpoint}`

  const requestHeaders = {
    ...(headers as Record<string, string>),
  }

  // Only set Content-Type to application/json if body is NOT FormData
  // and Content-Type is not already set
  if (!(fetchOptions.body instanceof FormData) && !requestHeaders['Content-Type']) {
    requestHeaders['Content-Type'] = 'application/json'
  }

  // Добавляем токен аутентификации, если требуется
  if (requiresAuth) {
    const authStore = useAuthStore()
    try {
      const token = await authStore.getValidAccessToken()
      requestHeaders['Authorization'] = `Bearer ${token}`
    } catch (error) {
      console.error('Failed to get access token:', error)
      throw new Error('Authentication required')
    }
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers: requestHeaders,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP ${response.status}: ${response.statusText}`,
    }))
    throw new Error(error.detail || error.message || 'Request failed')
  }

  // Обрабатываем пустые ответы (например, 204 No Content)
  const contentType = response.headers.get('content-type')
  if (!contentType || !contentType.includes('application/json')) {
    return {} as T
  }

  return response.json()
}

/**
 * Вспомогательные методы для разных HTTP методов
 */
export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    apiRequest<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data instanceof FormData ? data : (data ? JSON.stringify(data) : undefined),
    }),

  put: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  patch: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    apiRequest<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    apiRequest<T>(endpoint, { ...options, method: 'DELETE' }),
}
