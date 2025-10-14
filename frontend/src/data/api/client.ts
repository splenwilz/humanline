import { redirect } from 'next/navigation'
import {
  ApiError,
  ValidationError,
  AuthError,
  NetworkError,
} from './types'
import type { ApiConfig } from './types'
import {
  isTokenValid,
  isRefreshTokenValid,
  getAccessToken,
  getRefreshToken,
  storeTokens,
  clearTokens,
} from '@/lib/auth'

// Unified API client that works in both client and server environments
class ApiClient {
  private config: ApiConfig
  private refreshPromise: Promise<string | null> | null = null
  private requestQueue: Array<() => Promise<void>> = []
  private isRefreshing = false
  private isServer = typeof window === 'undefined'

  constructor() {
    this.config = {
      baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      retries: 2,
    }
  }

  // Get auth token - works differently for client vs server
  private async getAuthToken(): Promise<string | null> {
    if (this.isServer) {
      // Server-side: get from cookies
      const { cookies } = await import('next/headers')
      const cookieStore = await cookies()
      return cookieStore.get('access_token')?.value || null
    } else {
      // Client-side: get from localStorage
      return getAccessToken()
    }
  }

  // Handle auth errors - works differently for client vs server
  private handleAuthError(): void {
    if (this.isServer) {
      // Server-side: redirect
      redirect('/signin')
    } else {
      // Client-side: clear tokens and redirect
      clearTokens()
      window.location.href = '/signin'
    }
  }

  // Token refresh - only works on client-side
  private async refreshAccessToken(): Promise<string | null> {
    if (this.isServer) {
      // Server-side: no token refresh, just return null
      return null
    }

    // Client-side token refresh logic
    if (this.refreshPromise) {
      return this.refreshPromise
    }

    this.isRefreshing = true
    this.refreshPromise = this.performTokenRefresh()

    try {
      const newToken = await this.refreshPromise
      await this.processQueue()
      return newToken
    } finally {
      this.isRefreshing = false
      this.refreshPromise = null
    }
  }

  private async performTokenRefresh(): Promise<string | null> {
    try {
      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        console.warn('No refresh token available')
        return null
      }

      if (!isRefreshTokenValid()) {
        console.warn('Refresh token is invalid or expired')
        clearTokens()
        return null
      }

      const response = await fetch(`${this.config.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!response.ok) {
        console.warn('Token refresh failed:', response.status)
        if (response.status === 401) {
          clearTokens()
        }
        return null
      }

      const data = await response.json()
      storeTokens({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        expires_in: data.expires_in,
        token_type: data.token_type,
      })

      return data.access_token
    } catch (error) {
      console.error('Error refreshing token:', error)
      clearTokens()
      return null
    }
  }

  private async processQueue() {
    const pending = [...this.requestQueue]
    this.requestQueue = []

    for (const callback of pending) {
      await callback()
    }
  }

  // Unified request method
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retryCount = 0,
  ): Promise<T> {
    const url = `${this.config.baseURL}${endpoint}`

    // Create a per-call controller; do not auto-abort prior unrelated requests
    const controller = !this.isServer ? new AbortController() : null

    // Get and validate access token
    let accessToken = await this.getAuthToken()

    // Client-side: check if token is valid, if not try to refresh
    if (!this.isServer && accessToken) {
      try {
        if (!isTokenValid(accessToken)) {
          console.log('Access token expired, attempting refresh...')
          const newToken = await this.refreshAccessToken()
          if (newToken) {
            accessToken = newToken
            console.log('Token refreshed successfully')
          } else {
            console.warn('Token refresh failed, proceeding with expired token')
          }
        }
      } catch (error) {
        console.warn('Error validating token:', error)
      }
    }

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
        ...options.headers,
      },
      ...(controller && { signal: controller.signal }),
      ...options,
    }

    try {
      // Client-side: add timeout
      let timeoutId: NodeJS.Timeout | undefined
      if (!this.isServer) {
        timeoutId = setTimeout(() => {
          controller?.abort()
        }, this.config.timeout)
      }

      const response = await fetch(url, config)
      
      if (timeoutId) {
        clearTimeout(timeoutId)
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))

        switch (response.status) {
          case 400:
            throw new ValidationError(
              errorData.detail || 'Validation failed',
              errorData,
            )
          case 401:
            // Client-side: try to refresh token and retry once
            if (!this.isServer && retryCount === 0 && isRefreshTokenValid()) {
              console.log('401 error, attempting token refresh and retry...')

              if (this.isRefreshing) {
                return new Promise<T>((resolve, reject) => {
                  this.requestQueue.push(async () => {
                    try {
                      const result = await this.request<T>(
                        endpoint,
                        options,
                        retryCount + 1,
                      )
                      resolve(result)
                    } catch (error) {
                      reject(error)
                    }
                  })
                })
              }

              const newToken = await this.refreshAccessToken()
              if (newToken) {
                console.log('Token refreshed, retrying request...')
                return this.request(endpoint, options, retryCount + 1)
              }
            }
            // If refresh failed or server-side, handle auth error
            this.handleAuthError()
            throw new AuthError(
              errorData.detail || 'Authentication failed',
              response.status,
            )
          case 403:
            throw new AuthError(
              errorData.detail || 'Access forbidden',
              response.status,
            )
          case 404:
            throw new ApiError('Resource not found', 404, 'NOT_FOUND')
          case 422:
            throw new ValidationError(
              errorData.detail || 'Validation failed',
              errorData,
            )
          case 500:
            throw new ApiError('Internal server error', 500, 'SERVER_ERROR')
          default:
            throw new ApiError(
              errorData.detail || 'Request failed',
              response.status,
              'UNKNOWN_ERROR',
            )
        }
      }

      // Handle empty responses
      if (response.status === 204 || response.headers.get('content-length') === '0') {
        return undefined as T
      }
      
      const data = await response.json()
      return data
    } catch (error: unknown) {
      // Client-side: handle network errors
      if (!this.isServer) {
        if (error instanceof TypeError && error.message === 'Failed to fetch') {
          throw new NetworkError()
        }

        if (error instanceof Error && error.name === 'AbortError') {
          throw new NetworkError('Request was cancelled')
        }

        // Retry logic for network errors
        if (retryCount < this.config.retries && error instanceof NetworkError) {
          console.warn(
            `Retrying request (${retryCount + 1}/${this.config.retries})`,
          )
          await new Promise((resolve) =>
            setTimeout(resolve, 1000 * (retryCount + 1)),
          )
          return this.request(endpoint, options, retryCount + 1)
        }
      }

      // Re-throw API errors
      if (error instanceof ApiError) {
        throw error
      }

      // Wrap unknown errors
      const errorMessage =
        error instanceof Error ? error.message : 'An unexpected error occurred'
      throw new ApiError(errorMessage, 0, 'UNKNOWN_ERROR')
    }
  }

  // Public methods
  async get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  async post<T>(
    endpoint: string,
    data?: Record<string, unknown>,
    options?: RequestInit,
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(
    endpoint: string,
    data?: Record<string, unknown>,
    options?: RequestInit,
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }

  // Client-side only methods
  cancel() {
    // Note: With per-request controllers, this method is no longer useful
    // Individual requests can be cancelled by their respective controllers
    console.warn('cancel() method is deprecated - use per-request AbortController instead')
  }

  updateConfig(newConfig: Partial<ApiConfig>) {
    this.config = { ...this.config, ...newConfig }
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
