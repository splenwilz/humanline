import useSWRMutation from 'swr/mutation'
import { mutate } from 'swr'
import { authApi } from '../api/auth'
import {
  storeTokens,
  storeUserProfile,
  clearTokens,
  clearPendingEmail,
  storePendingEmail,
} from '@/lib/auth'
import { createCacheKey, invalidateCache } from '@/lib/swr-config'
import { toast } from 'sonner'
import { Role } from '@/lib/rbac'

// Mutation fetchers
async function signupFetcher(_: string, { arg }: { arg: { email: string; password: string; fullName?: string } }) {
  const { email, password, fullName } = arg
  
  // Split full name into first and last name for backend compatibility
  const trimmedName = fullName?.trim() || ''
  const nameParts = trimmedName.split(' ').filter(part => part.length > 0)
  
  const firstName = nameParts[0] || 'User'
  const lastName = nameParts.length > 1 
    ? nameParts.slice(1).join(' ') 
    : firstName

  return authApi.signup({
    email,
    password,
    first_name: firstName,
    last_name: lastName,
  })
}

async function signinFetcher(_: string, { arg }: { arg: { email: string; password: string } }) {
  return authApi.signin(arg)
}

async function confirmEmailFetcher(_: string, { arg }: { arg: { code: string } }) {
  return authApi.confirmEmail(arg.code)
}

async function resendConfirmationFetcher(_: string, { arg }: { arg: { email: string } }) {
  return authApi.resendConfirmation(arg.email)
}

async function refreshTokenFetcher(_: string, { arg }: { arg: { refreshToken: string } }) {
  return authApi.refreshToken(arg.refreshToken)
}

// Hook for user signup
export const useSignup = () => {
  const { trigger, data, error, isMutating } = useSWRMutation('/auth/register', signupFetcher)

  const signup = async (email: string, password: string, fullName?: string) => {
    try {
      const response = await trigger({ email, password, fullName })

      // Check response type to determine next action
      if ('access_token' in response) {
        // Immediate login response - store tokens and redirect to dashboard
        storeTokens({
          access_token: response.access_token,
          refresh_token: response.refresh_token || '',
          expires_in: response.expires_in,
          token_type: response.token_type,
        })

        // Store user profile if provided
        if (response.user) {
          storeUserProfile({
            ...response.user,
            role: response.user.role as Role
          })
        }

        // Invalidate user cache to trigger refetch
        await mutate(createCacheKey.user())

        toast.success('Registration successful! Welcome to Humanline.')
        
        return {
          success: true,
          data: response,
          type: 'immediate_login',
          message: 'Registration successful! Welcome to Humanline.'
        }
      } else {
        // Email confirmation response - store pending email
        storePendingEmail(email)

        toast.info('Please check your email for verification code.')
        
        return {
          success: true,
          data: response,
          type: 'email_confirmation_required',
          message: response.message
        }
      }
    } catch (error: any) {
      const errorMessage = error?.message || 'Registration failed'
      toast.error(errorMessage)
      throw error
    }
  }

  return {
    signup,
    data,
    error,
    isLoading: isMutating,
  }
}

// Hook for user signin
export const useSignin = () => {
  const { trigger, data, error, isMutating } = useSWRMutation('/auth/login', signinFetcher)

  const signin = async (email: string, password: string) => {
    try {
      const response = await trigger({ email, password })

      // Store tokens and user profile
      storeTokens({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        expires_in: response.expires_in,
        token_type: response.token_type,
      })

      // Store user profile from backend response
      if (response.user) {
        storeUserProfile({
          ...response.user,
          role: response.user.role as Role
        })
      } else {
        console.error('No user data provided by backend in signin response')
      }

      // Invalidate user cache to trigger refetch
      await mutate(createCacheKey.user())

      toast.success('Welcome back!')

      return { success: true, data: response }
    } catch (error: any) {
      const errorMessage = error?.message || 'Sign in failed'
      toast.error(errorMessage)
      throw error
    }
  }

  return {
    signin,
    data,
    error,
    isLoading: isMutating,
  }
}

// Hook for email confirmation
export const useEmailConfirmation = () => {
  const { trigger, data, error, isMutating } = useSWRMutation('/auth/confirm-email', confirmEmailFetcher)

  const confirmEmail = async (code: string) => {
    try {
      const response = await trigger({ code })

      // Clear pending email after successful confirmation
      clearPendingEmail()

      toast.success('Email confirmed successfully! You can now sign in.')

      return { success: true, data: response }
    } catch (error: any) {
      const errorMessage = error?.message || 'Email confirmation failed'
      toast.error(errorMessage)
      throw error
    }
  }

  return {
    confirmEmail,
    data,
    error,
    isLoading: isMutating,
  }
}

// Hook for resending confirmation
export const useResendConfirmation = () => {
  const { trigger, data, error, isMutating } = useSWRMutation('/auth/resend-confirmation', resendConfirmationFetcher)

  const resendConfirmation = async (email: string) => {
    try {
      const response = await trigger({ email })

      toast.success('Confirmation code sent! Please check your email.')

      return { 
        success: true, 
        data: {
          message: response.message,
          email: response.email,
          expires_in_hours: response.expires_in_hours
        }
      }
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to resend confirmation code'
      toast.error(errorMessage)
      throw error
    }
  }

  return {
    resendConfirmation,
    data,
    error,
    isLoading: isMutating,
  }
}

// Hook for token refresh
export const useTokenRefresh = () => {
  const { trigger, data, error, isMutating } = useSWRMutation('/auth/refresh', refreshTokenFetcher)

  const refreshToken = async (refreshToken: string) => {
    try {
      const response = await trigger({ refreshToken })

      // Store new tokens
      storeTokens({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        expires_in: response.expires_in,
        token_type: response.token_type,
      })

      if (response.user) {
        storeUserProfile({
          ...response.user,
          role: response.user.role as Role
        })
      }

      // Invalidate user cache to trigger refetch
      await mutate(createCacheKey.user())

      return { success: true, data: response }
    } catch (error: any) {
      // Clear tokens on refresh failure
      clearTokens()
      throw error
    }
  }

  return {
    refreshToken,
    data,
    error,
    isLoading: isMutating,
  }
}

// Hook for logout
export const useLogout = () => {
  const logout = async () => {
    try {
      // Clear tokens and user data
      clearTokens()
      clearPendingEmail()
      
      // Invalidate all user-related caches
      await mutate(
        key => typeof key === 'string' && (key.includes('/users') || key.includes('/auth')),
        undefined,
        { revalidate: false }
      )

      toast.success('Logged out successfully')
      
      // Redirect to signin page
      window.location.href = '/signin'
    } catch (error) {
      console.error('Logout error:', error)
      // Force redirect even if there's an error
      window.location.href = '/signin'
    }
  }

  return { logout }
}

// Legacy hooks for backward compatibility (deprecated)
export const useOTPVerification = useEmailConfirmation
export const useResendOTP = useResendConfirmation