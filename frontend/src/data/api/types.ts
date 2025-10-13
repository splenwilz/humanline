// Shared API types and interfaces

export interface ApiConfig {
  baseURL: string
  timeout: number
  retries: number
}

// Employee types



// Error types
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, public details?: unknown) {
    super(message, 400, 'VALIDATION_ERROR')
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
  constructor(message: string = 'Network error') {
    super(message, 0, 'NETWORK_ERROR')
    this.name = 'NetworkError'
  }
}

// Base API client interface
export interface BaseApiClient {
  get<T>(endpoint: string, options?: RequestInit): Promise<T>
  post<T>(endpoint: string, data?: Record<string, unknown>, options?: RequestInit): Promise<T>
  put<T>(endpoint: string, data?: Record<string, unknown>, options?: RequestInit): Promise<T>
  delete<T>(endpoint: string, options?: RequestInit): Promise<T>
}