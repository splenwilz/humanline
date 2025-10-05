// Types for auth requests and responses
export interface SignupRequest {
  email: string
  password: string
  first_name: string
  last_name: string
  [key: string]: unknown
}

// Union type for signup response - can be either immediate login or email confirmation
export type SignupResponse = 
  | SignupImmediateLoginResponse 
  | SignupEmailConfirmationResponse

// Response when email confirmation is disabled (immediate login)
export interface SignupImmediateLoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user?: {
    id: string
    email: string
    full_name?: string
    role: string
    email_confirmed_at?: string
    permissions?: string[]
    created_at: string
    needs_onboarding?: boolean
  }
}

// Response when email confirmation is enabled
export interface SignupEmailConfirmationResponse {
  message: string
  email: string
  email_sent: boolean
  expires_in_hours: number
  next_step: string
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
    role: string
    email_confirmed_at?: string
    permissions?: string[]
    created_at: string
    needs_onboarding?: boolean
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
    role: string
    email_confirmed_at?: string
    permissions?: string[]
    created_at: string
    needs_onboarding?: boolean
  }
}
