// Authentication utility functions

export interface AuthTokens {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
}

export interface UserProfile {
  id: string
  email: string
  full_name?: string
  email_confirmed_at?: string
  created_at: string
}

// Token storage keys
const TOKEN_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  TOKEN_EXPIRES_IN: 'token_expires_in',
  USER_PROFILE: 'user_profile',
  PENDING_EMAIL: 'pending_email',
}

// Store authentication tokens
export const storeTokens = (tokens: AuthTokens) => {
  localStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, tokens.access_token)
  localStorage.setItem(TOKEN_KEYS.REFRESH_TOKEN, tokens.refresh_token)
  localStorage.setItem(
    TOKEN_KEYS.TOKEN_EXPIRES_IN,
    tokens.expires_in.toString(),
  )
}

// Get access token
export const getAccessToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEYS.ACCESS_TOKEN)
}

// Get refresh token
export const getRefreshToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEYS.REFRESH_TOKEN)
}

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  const token = getAccessToken()
  if (!token) return false

  // Check if token is expired
  const expiresIn = localStorage.getItem(TOKEN_KEYS.TOKEN_EXPIRES_IN)
  if (expiresIn) {
    const expiryTime = parseInt(expiresIn) * 1000 // Convert to milliseconds
    const currentTime = Date.now()
    if (currentTime > expiryTime) {
      // Token expired, clear storage
      clearTokens()
      return false
    }
  }

  return true
}

// Store user profile
export const storeUserProfile = (profile: UserProfile) => {
  localStorage.setItem(TOKEN_KEYS.USER_PROFILE, JSON.stringify(profile))
}

// Get user profile
export const getUserProfile = (): UserProfile | null => {
  const profile = localStorage.getItem(TOKEN_KEYS.USER_PROFILE)
  return profile ? JSON.parse(profile) : null
}

// Store pending email for signup confirmation
export const storePendingEmail = (email: string) => {
  localStorage.setItem(TOKEN_KEYS.PENDING_EMAIL, email)
}

// Get pending email for signup confirmation
export const getPendingEmail = (): string | null => {
  return localStorage.getItem(TOKEN_KEYS.PENDING_EMAIL)
}

// Clear pending email after successful confirmation
export const clearPendingEmail = () => {
  localStorage.removeItem(TOKEN_KEYS.PENDING_EMAIL)
}

// Clear all authentication data
export const clearTokens = () => {
  localStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN)
  localStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN)
  localStorage.removeItem(TOKEN_KEYS.TOKEN_EXPIRES_IN)
  localStorage.removeItem(TOKEN_KEYS.USER_PROFILE)
  localStorage.removeItem(TOKEN_KEYS.PENDING_EMAIL)
}

// JWT payload interface
interface JWTPayload {
  sub?: string
  user_id?: string
  email?: string
  exp?: number
  iat?: number
  type?: string
  [key: string]: unknown
}

// Parse JWT token to get payload
export const parseJWT = (token: string): JWTPayload | null => {
  try {
    // Check if token has the expected JWT format (3 parts separated by dots)
    const parts = token.split('.')
    if (parts.length !== 3) {
      console.warn('Invalid JWT token format:', token)
      return null
    }
    
    const base64Url = parts[1]
    if (!base64Url) {
      console.warn('JWT token missing payload part')
      return null
    }
    
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        })
        .join(''),
    )
    return JSON.parse(jsonPayload) as JWTPayload
  } catch (error) {
    console.error('Error parsing JWT token:', error)
    return null
  }
}

// Get user email from stored token
export const getUserEmail = (): string | null => {
  const token = getAccessToken()
  if (!token) return null

  const payload = parseJWT(token)
  return payload?.email || null
}

// Check if token is expired (with buffer time)
export const isTokenExpired = (token?: string): boolean => {
  const accessToken = token || getAccessToken()
  if (!accessToken) return true

  const payload = parseJWT(accessToken)
  if (!payload?.exp) return true

  // Add 5 minute buffer before actual expiration
  const bufferTime = 5 * 60 * 1000 // 5 minutes in milliseconds
  const expirationTime = payload.exp * 1000 // Convert to milliseconds
  const currentTime = Date.now()

  return currentTime >= (expirationTime - bufferTime)
}

// Check if token is valid and not expired
export const isTokenValid = (token?: string): boolean => {
  const accessToken = token || getAccessToken()
  if (!accessToken) return false

  const payload = parseJWT(accessToken)
  if (!payload) return false

  // For Supabase tokens, we don't check the 'type' field as it might not be present
  // Just check if not expired
  return !isTokenExpired(accessToken)
}

// Get token expiration time in milliseconds
export const getTokenExpirationTime = (token?: string): number | null => {
  const accessToken = token || getAccessToken()
  if (!accessToken) return null

  const payload = parseJWT(accessToken)
  if (!payload?.exp) return null

  return payload.exp * 1000 // Convert to milliseconds
}

// Check if refresh token is valid
export const isRefreshTokenValid = (): boolean => {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return false

  const payload = parseJWT(refreshToken)
  if (!payload) return false

  // For Supabase tokens, we don't check the 'type' field as it might not be present
  // Just check if not expired
  if (!payload.exp) return false
  const expirationTime = payload.exp * 1000
  const currentTime = Date.now()

  return currentTime < expirationTime
}

// Logout user
export const logout = () => {
  clearTokens()
  // Redirect to home or signin page
  window.location.href = '/signin'
}

// Custom hook for managing pending email (for React components)
export const usePendingEmail = () => {
  const getEmail = () => getPendingEmail()
  const setEmail = (email: string) => storePendingEmail(email)
  const clearEmail = () => clearPendingEmail()

  return { getEmail, setEmail, clearEmail }
}
