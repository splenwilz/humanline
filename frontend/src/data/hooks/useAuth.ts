import useSWR from 'swr'
import { authApi } from '../api/auth'
import {
  storeTokens,
  storeUserProfile,
  clearTokens,
  clearPendingEmail,
} from '@/lib/auth'

// Hook for user signup - handles both immediate login and email confirmation flows
export const useSignup = () => {
  const { data, error, isLoading, mutate } = useSWR(
    null, // No key for mutations
    null,
    { revalidateOnFocus: false },
  )

  const signup = async (email: string, password: string, fullName?: string) => {
    try {
      // Split full name into first and last name for backend compatibility
      // Handle single names and empty inputs gracefully
      const trimmedName = fullName?.trim() || ''
      const nameParts = trimmedName.split(' ').filter(part => part.length > 0)
      
      const firstName = nameParts[0] || 'User'  // Fallback for empty names
      const lastName = nameParts.length > 1 
        ? nameParts.slice(1).join(' ') 
        : firstName  // Use first name as last name for single names

      const response = await authApi.signup({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
      })

      // Check response type to determine next action
      if ('access_token' in response) {
        // Immediate login response - store tokens and redirect to dashboard
        storeTokens({
          access_token: response.access_token,
          refresh_token: '', // Not provided in immediate login
          expires_in: response.expires_in,
          token_type: response.token_type,
        })

        return {
          success: true,
          data: response,
          type: 'immediate_login',
          message: 'Registration successful! Welcome to Humanline.'
        }
      } else {
        // Email confirmation response - store pending email and show confirmation message
        const { storePendingEmail } = await import('@/lib/auth')
        storePendingEmail(email)

        return {
          success: true,
          data: response,
          type: 'email_confirmation_required',
          message: response.message
        }
      }
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

// Hook for email confirmation
export const useEmailConfirmation = () => {
  const { data, error, isLoading, mutate } = useSWR(null, null, {
    revalidateOnFocus: false,
  })

  const confirmEmail = async (code: string) => {
    try {
      const response = await authApi.confirmEmail(code)

      // Clear pending email after successful confirmation
      clearPendingEmail()

      return { success: true, data: response }
    } catch (error) {
      console.error('Email confirmation error:', error)

      // Extract meaningful error message from different error types
      let errorMessage = 'Email confirmation failed'

      if (error && typeof error === 'object') {
        if ('message' in error && typeof error.message === 'string') {
          errorMessage = error.message
        } else if ('detail' in error && typeof error.detail === 'string') {
          errorMessage = error.detail
        }
      } else if (typeof error === 'string') {
        errorMessage = error
      }

      return {
        success: false,
        error: {
          message: errorMessage,
          originalError: error
        }
      }
    }
  }

  return {
    confirmEmail,
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

  const verifyOTP = async (email: string, code: string) => {
    try {
      // Use the email confirmation endpoint instead of the old OTP endpoint
      const response = await authApi.confirmEmail(code)

      // Clear pending email after successful confirmation
      clearPendingEmail()

      // Return success with user data (no tokens since this is just email confirmation)
      // The frontend will need to redirect to login after successful confirmation
      return { 
        success: true, 
        data: {
          message: response.message,
          user: {
            email: response.user_email
          },
          confirmed_at: response.confirmed_at
        }
      }
    } catch (error) {
      console.error('Email confirmation error:', error)

      // Extract meaningful error message from different error types
      let errorMessage = 'Email confirmation failed'

      if (error && typeof error === 'object') {
        if ('message' in error && typeof error.message === 'string') {
          errorMessage = error.message
        } else if ('detail' in error && typeof error.detail === 'string') {
          errorMessage = error.detail
        }
      } else if (typeof error === 'string') {
        errorMessage = error
      }

      return {
        success: false,
        error: new Error(errorMessage)
      }
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
      // Call the new resend confirmation endpoint
      const response = await authApi.resendConfirmation(email)

      return { 
        success: true, 
        data: {
          message: response.message,
          email: response.email,
          expires_in_hours: response.expires_in_hours
        }
      }
    } catch (error) {
      console.error('Resend confirmation error:', error)

      // Extract meaningful error message from different error types
      let errorMessage = 'Failed to resend confirmation code'

      if (error && typeof error === 'object') {
        if ('message' in error && typeof error.message === 'string') {
          errorMessage = error.message
        } else if ('detail' in error && typeof error.detail === 'string') {
          errorMessage = error.detail
        }
      } else if (typeof error === 'string') {
        errorMessage = error
      }

      return {
        success: false,
        error: new Error(errorMessage)
      }
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
