import useSWR from 'swr'
import { getUserProfile, isAuthenticated, getAccessToken } from '@/lib/auth'

// Hook for getting current user profile
export const useUser = () => {
  const {
    data: user,
    error,
    isLoading,
    mutate,
  } = useSWR(
    'user',
    async () => {
      if (!isAuthenticated()) {
        return null
      }
      return getUserProfile()
    },
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      refreshInterval: 0, // Don't auto-refresh
    },
  )

  return {
    user,
    error,
    isLoading,
    isAuthenticated: !!user,
    mutate,
  }
}

// Hook for checking authentication status
export const useAuth = () => {
  const {
    data: isAuth,
    error,
    isLoading,
    mutate,
  } = useSWR(
    'auth',
    async () => {
      return isAuthenticated()
    },
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      refreshInterval: 0,
    },
  )

  return {
    isAuthenticated: isAuth || false,
    error,
    isLoading,
    mutate,
  }
}

// Hook for getting access token
export const useAccessToken = () => {
  const {
    data: token,
    error,
    isLoading,
    mutate,
  } = useSWR(
    'accessToken',
    async () => {
      return getAccessToken()
    },
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      refreshInterval: 0,
    },
  )

  return {
    accessToken: token,
    error,
    isLoading,
    mutate,
  }
}
