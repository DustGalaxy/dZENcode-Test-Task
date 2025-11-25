interface JWTPayload {
  user_id: number
  exp: number
  iat: number
  jti: string
  token_type?: string
}

/**
 * Декодирует JWT токен без верификации (только для чтения payload)
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    const base64Url = token.split('.')[1]
    if (!base64Url) return null

    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )

    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Failed to decode JWT:', error)
    return null
  }
}

/**
 * Проверяет, истек ли токен
 * @param token JWT токен
 * @param bufferSeconds Буфер в секундах (обновлять токен за N секунд до истечения)
 */
export function isTokenExpired(token: string, bufferSeconds = 60): boolean {
  const payload = decodeJWT(token)
  if (!payload || !payload.exp) return true

  const expirationTime = payload.exp * 1000
  const currentTime = Date.now()
  const bufferTime = bufferSeconds * 1000

  return currentTime >= expirationTime - bufferTime
}

/**
 * Получает user_id из токена
 */
export function getUserIdFromToken(token: string): number | null {
  const payload = decodeJWT(token)
  return payload?.user_id ?? null
}

/**
 * Получает время до истечения токена в секундах
 */
export function getTokenTimeToExpire(token: string): number {
  const payload = decodeJWT(token)
  if (!payload || !payload.exp) return 0

  const expirationTime = payload.exp * 1000
  const currentTime = Date.now()
  const timeLeft = expirationTime - currentTime

  return Math.max(0, Math.floor(timeLeft / 1000))
}
