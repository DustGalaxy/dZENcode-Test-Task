/**
 * Pinia Store для управления аутентификацией
 * 
 * Флоу аутентификации:
 * 1. Инициализация: проверка localStorage на наличие сохраненных токенов
 * 2. Логин: отправка credentials -> получение токенов -> получение данных пользователя -> сохранение
 * 3. Автоматическое обновление токена при истечении
 * 4. Logout: очистка store и localStorage
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, RegistrationCredentials, AuthState } from '../types/auth'
import { storage } from '../utils/storage'
import { isTokenExpired, getUserIdFromToken } from '../utils/jwt'
import { login as apiLogin, register as apiRegister, refreshAccessToken, getCurrentUser } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value)

  // Actions

  /**
   * Инициализация store - проверка перманентного хранилища
   * Вызывается при старте приложения
   */
  async function initialize(): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      // Шаг 1: Поиск в перманентном хранилище
      const savedAccessToken = storage.getAccessToken()
      const savedRefreshToken = storage.getRefreshToken()
      const savedUser = storage.getUser<User>()

      if (!savedAccessToken || !savedRefreshToken) {
        // Нет сохраненных токенов
        return
      }

      // Проверяем, не истек ли access token
      if (isTokenExpired(savedAccessToken)) {
        // Пытаемся обновить токен
        await refreshTokens(savedRefreshToken)
      } else {
        // Токен валидный, восстанавливаем состояние
        accessToken.value = savedAccessToken
        refreshToken.value = savedRefreshToken
        user.value = savedUser

        // Опционально: обновляем данные пользователя с сервера
        if (savedUser) {
          try {
            user.value = await getCurrentUser(savedAccessToken)
            storage.setUser(user.value)
          } catch (err) {
            // Если не удалось получить данные, используем сохраненные
            console.warn('Failed to refresh user data:', err)
          }
        }
      }
    } catch (err) {
      console.error('Failed to initialize auth:', err)
      // Очищаем невалидные данные
      await logout()
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Логин пользователя
   */
  async function login(credentials: LoginCredentials): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      // Шаг 2: Логин через username и password
      // Шаг 3: Получение ответа сервера в виде токенов
      const tokens = await apiLogin(credentials)

      accessToken.value = tokens.access
      refreshToken.value = tokens.refresh

      // Шаг 4: Получение данных о пользователе
      try {
        user.value = await getCurrentUser(tokens.access)
      } catch (err) {
        // Если endpoint /api/user/me/ не существует, создаем базовый объект пользователя
        // из данных токена
        const userId = getUserIdFromToken(tokens.access)
        if (userId) {
          user.value = {
            id: userId,
            username: credentials.username,
            email: '', // Будет заполнено при создании endpoint
          }
        } else {
          throw new Error('Failed to get user data from token')
        }
      }

      // Шаг 5: Запись в useAuthStore (уже сделано выше) и в перманентное хранилище
      storage.setAccessToken(tokens.access)
      storage.setRefreshToken(tokens.refresh)
      storage.setUser(user.value)

      console.log('Login successful:', user.value)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function registration(credentials: RegistrationCredentials): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const new_user = await apiRegister(credentials)

      const tokens = await apiLogin({
        username: credentials.username,
        password: credentials.password,
      })

      accessToken.value = tokens.access
      refreshToken.value = tokens.refresh
      user.value = new_user
      storage.setAccessToken(tokens.access)
      storage.setRefreshToken(tokens.refresh)
      storage.setUser(user.value)

      console.log('Registration successful:', user.value)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Обновление access токена с помощью refresh токена
   */
  async function refreshTokens(currentRefreshToken?: string): Promise<void> {
    const tokenToUse = currentRefreshToken || refreshToken.value

    if (!tokenToUse) {
      throw new Error('No refresh token available')
    }

    try {
      const tokens = await refreshAccessToken(tokenToUse)

      accessToken.value = tokens.access
      // Некоторые backend'ы возвращают новый refresh token
      if (tokens.refresh) {
        refreshToken.value = tokens.refresh
        storage.setRefreshToken(tokens.refresh)
      }

      storage.setAccessToken(tokens.access)

      console.log('Token refreshed successfully')
    } catch (err) {
      console.error('Failed to refresh token:', err)
      // Если не удалось обновить токен, разлогиниваем пользователя
      await logout()
      throw err
    }
  }

  /**
   * Logout пользователя
   */
  async function logout(): Promise<void> {
    // Очистка store
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    error.value = null

    // Очистка перманентного хранилища
    storage.clearAuth()

    console.log('Logout successful')
  }

  /**
   * Получение валидного access токена (с автоматическим обновлением)
   * Используйте этот метод перед каждым API запросом
   */
  async function getValidAccessToken(): Promise<string> {
    if (!accessToken.value) {
      throw new Error('No access token available')
    }

    // Проверяем, не истек ли токен (с буфером 60 секунд)
    if (isTokenExpired(accessToken.value, 60)) {
      await refreshTokens()
    }

    return accessToken.value!
  }

  /**
   * Обновление данных пользователя
   */
  async function updateUser(userData: Partial<User>): Promise<void> {
    if (!user.value) {
      throw new Error('No user logged in')
    }

    user.value = { ...user.value, ...userData }
    storage.setUser(user.value)
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,

    // Computed
    isAuthenticated,

    // Actions
    initialize,
    login,
    registration,
    logout,
    refreshTokens,
    getValidAccessToken,
    updateUser,
  }
})
