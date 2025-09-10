// Types for auth requests and responses
export interface SignupRequest {
  email: string
  password: string
  full_name?: string
  [key: string]: unknown
}

export interface SignupResponse {
  user_id: string
  email: string
  message: string
  confirmation_sent: boolean
  otp_sent: boolean
}

export interface SigninRequest {
  email: string
  password: string
  [key: string]: unknown
}

export interface SigninResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    email: string
    full_name?: string
    email_confirmed_at?: string
    created_at: string
  }
}

export interface OTPVerificationRequest {
  email: string
  otp: string
  [key: string]: unknown
}

export interface OTPVerificationResponse {
  message: string
  verified: boolean
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    email: string
    full_name?: string
    email_confirmed_at?: string
    created_at: string
  }
}
