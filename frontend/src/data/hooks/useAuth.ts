import useSWR from 'swr'
import { authApi } from '../api/auth'
import {
  storeTokens,
  storeUserProfile,
  clearTokens,
  clearPendingEmail,
} from '@/lib/auth'

// Hook for user signup
export const useSignup = () => {
  const { data, error, isLoading, mutate } = useSWR(
    null, // No key for mutations
    null,
    { revalidateOnFocus: false },
  )

  const signup = async (email: string, password: string, fullName?: string) => {
    try {
      const response = await authApi.signup({
        email,
        password,
        full_name: fullName,
      })

      // Store pending email for confirmation
      const { storePendingEmail } = await import('@/lib/auth')
      storePendingEmail(email)

      return { success: true, data: response }
    } catch (error) {
      return { success: false, error }
    }
  }

  return {
    signup,
    data,
    error,
    isLoading,
  }
}

// Hook for user signin
export const useSignin = () => {
  const { data, error, isLoading, mutate } = useSWR(null, null, {
    revalidateOnFocus: false,
  })

  const signin = async (email: string, password: string) => {
    try {
      const response = await authApi.signin({ email, password })

      // Store tokens and user profile
      storeTokens({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        expires_in: response.expires_in,
        token_type: response.token_type,
      })

      if (response.user) {
        storeUserProfile(response.user)
      }

      return { success: true, data: response }
    } catch (error) {
      return { success: false, error }
    }
  }

  return {
    signin,
    data,
    error,
    isLoading,
  }
}

// Hook for OTP verification
export const useOTPVerification = () => {
  const { data, error, isLoading, mutate } = useSWR(null, null, {
    revalidateOnFocus: false,
  })

  const verifyOTP = async (email: string, otp: string) => {
    try {
      const response = await authApi.verifyOTP({ email, otp })

      // Store tokens and user profile
      storeTokens({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        expires_in: response.expires_in,
        token_type: response.token_type,
      })

      if (response.user) {
        storeUserProfile(response.user)
      }

      // Clear pending email after successful verification
      clearPendingEmail()

      return { success: true, data: response }
    } catch (error) {
      return { success: false, error }
    }
  }

  return {
    verifyOTP,
    data,
    error,
    isLoading,
  }
}

// Hook for resending OTP
export const useResendOTP = () => {
  const { data, error, isLoading, mutate } = useSWR(null, null, {
    revalidateOnFocus: false,
  })

  const resendOTP = async (email: string) => {
    try {
      const response = await authApi.resendOTP(email)
      return { success: true, data: response }
    } catch (error) {
      return { success: false, error }
    }
  }

  return {
    resendOTP,
    data,
    error,
    isLoading,
  }
}

// Hook for token refresh
export const useTokenRefresh = () => {
  const { data, error, isLoading, mutate } = useSWR(null, null, {
    revalidateOnFocus: false,
  })

  const refreshToken = async (refreshToken: string) => {
    try {
      const response = await authApi.refreshToken(refreshToken)

      // Store new tokens
      storeTokens({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        expires_in: response.expires_in,
        token_type: response.token_type,
      })

      if (response.user) {
        storeUserProfile(response.user)
      }

      return { success: true, data: response }
    } catch (error) {
      return { success: false, error }
    }
  }

  return {
    refreshToken,
    data,
    error,
    isLoading,
  }
}

// Hook for logout
export const useLogout = () => {
  const logout = () => {
    clearTokens()
    // Redirect to home or signin page
    window.location.href = '/signin'
  }

  return { logout }
}
