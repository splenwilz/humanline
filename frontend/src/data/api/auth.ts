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
  // Sign up a new user
  async signup(data: SignupRequest): Promise<SignupResponse> {
    return apiClient.post<SignupResponse>('/auth/signup', data)
  },

  // Sign in existing user
  async signin(data: SigninRequest): Promise<SigninResponse> {
    return apiClient.post<SigninResponse>('/auth/signin', data)
  },

  // Verify OTP code
  async verifyOTP(
    data: OTPVerificationRequest,
  ): Promise<OTPVerificationResponse> {
    return apiClient.post<OTPVerificationResponse>('/auth/verify-otp', data)
  },

  // Resend OTP code
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
