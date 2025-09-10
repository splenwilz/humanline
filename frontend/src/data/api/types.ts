export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: Record<string, unknown>,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(message, 400, 'VALIDATION_ERROR', details)
    this.name = 'ValidationError'
  }
}

export class AuthError extends ApiError {
  constructor(message: string, status: number = 401) {
    super(message, status, 'AUTH_ERROR')
    this.name = 'AuthError'
  }
}

export class NetworkError extends ApiError {
  constructor(message: string = 'Network request failed') {
    super(message, 0, 'NETWORK_ERROR')
    this.name = 'NetworkError'
  }
}

export interface ApiResponse<T = unknown> {
  data?: T
  message?: string
  success: boolean
}

export interface ApiConfig {
  baseURL: string
  timeout: number
  retries: number
}
