import {
  SignupRequest,
  SignupResponse,
  SigninRequest,
  SigninResponse,
  OTPVerificationRequest,
  OTPVerificationResponse,
} from '@/types/auth'
import { apiClient } from './client'

// Auth API functions
export const authApi = {
  // Sign up a new user - now handles both immediate login and email confirmation
  async signup(data: SignupRequest): Promise<SignupResponse> {
    return apiClient.post<SignupResponse>('/auth/register', data)
  },

  // Sign in existing user
  async signin(data: SigninRequest): Promise<SigninResponse> {
    return apiClient.post<SigninResponse>('/auth/login', data)
  },

  // Confirm email address using 6-digit verification code
  async confirmEmail(code: string): Promise<{
    message: string
    user_email: string
    confirmed_at: string
  }> {
    // Send code in request body for better security (prevents logging in URLs)
    return apiClient.post('/auth/confirm-email', { code })
  },

  // Resend email confirmation code to unverified user
  async resendConfirmation(email: string): Promise<{
    message: string
    email: string
    expires_in_hours: number
  }> {
    return apiClient.post('/auth/resend-confirmation', { email })
  },

  // Verify OTP code (legacy - may be removed)
  async verifyOTP(
    data: OTPVerificationRequest,
  ): Promise<OTPVerificationResponse> {
    return apiClient.post<OTPVerificationResponse>('/auth/verify-otp', data)
  },

  // Resend OTP code (legacy - may be removed)
  async resendOTP(
    email: string,
  ): Promise<{ message: string; otp_sent: boolean }> {
    return apiClient.post('/auth/resend-otp', { email })
  },

  // Refresh access token
  async refreshToken(refreshToken: string): Promise<SigninResponse> {
    return apiClient.post<SigninResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
  },
}
