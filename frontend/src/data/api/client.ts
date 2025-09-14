import {
  ApiError,
  ValidationError,
  AuthError,
  NetworkError,
  ApiConfig,
} from './types'
import {
  isTokenValid,
  isRefreshTokenValid,
  getAccessToken,
  getRefreshToken,
  storeTokens,
  clearTokens,
} from '@/lib/auth'

class ApiClient {
  private config: ApiConfig
  private abortController: AbortController | null = null

  constructor() {
    this.config = {
      baseURL:
        process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      retries: 2,
    }
  }

  // Refresh access token using refresh token
  private async refreshAccessToken(): Promise<string | null> {
    try {
      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        console.warn('No refresh token available')
        return null
      }

      // Check if refresh token is valid before attempting refresh
      if (!isRefreshTokenValid()) {
        console.warn('Refresh token is invalid or expired')
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
        return null
      }

      const data = await response.json()

      // Store new tokens
      storeTokens({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        expires_in: data.expires_in,
        token_type: data.token_type,
      })

      return data.access_token
    } catch (error) {
      console.error('Error refreshing token:', error)
      return null
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retryCount = 0,
  ): Promise<T> {
    const url = `${this.config.baseURL}${endpoint}`

    // Cancel previous request if it exists
    if (this.abortController) {
      this.abortController.abort()
    }

    this.abortController = new AbortController()

    // Get and validate access token
    let accessToken = getAccessToken()

    // Check if token is valid, if not try to refresh
    if (accessToken) {
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
        // Continue with the request even if token validation fails
      }
    }

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
        ...options.headers,
      },
      signal: this.abortController.signal,
      ...options,
    }

    try {
      // Add timeout
      const timeoutId = setTimeout(() => {
        this.abortController?.abort()
      }, this.config.timeout)

      const response = await fetch(url, config)
      clearTimeout(timeoutId)

      // Handle different response types
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))

        switch (response.status) {
          case 400:
            throw new ValidationError(
              errorData.detail || 'Validation failed',
              errorData,
            )
          case 401:
            // Try to refresh token and retry once
            if (retryCount === 0 && isRefreshTokenValid()) {
              console.log('401 error, attempting token refresh and retry...')
              const newToken = await this.refreshAccessToken()
              if (newToken) {
                console.log('Token refreshed, retrying request...')
                // Retry the request with new token
                return this.request(endpoint, options, retryCount + 1)
              }
            }
            // If refresh failed or already retried, clear tokens and redirect
            clearTokens()
            if (typeof window !== 'undefined') {
              window.location.href = '/signin'
            }
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

      // Parse response
      const data = await response.json()
      return data
    } catch (error: unknown) {
      // Handle network errors
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw new NetworkError()
      }

      // Handle abort errors
      if (error instanceof Error && error.name === 'AbortError') {
        throw new NetworkError('Request was cancelled')
      }

      // Re-throw API errors
      if (error instanceof ApiError) {
        throw error
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

  // Cancel ongoing requests
  cancel() {
    if (this.abortController) {
      this.abortController.abort()
    }
  }

  // Update config
  updateConfig(newConfig: Partial<ApiConfig>) {
    this.config = { ...this.config, ...newConfig }
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
