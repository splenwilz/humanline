import useSWR from 'swr'
import { getUserProfile, isAuthenticated } from '@/lib/auth'
import { createCacheKey } from '@/lib/swr-config'

// Hook for getting current user profile
export const useUser = () => {
  const {
    data: user,
    error,
    isLoading,
    mutate,
  } = useSWR(
    createCacheKey.user(),
    async () => {
      if (!isAuthenticated()) {
        return null
      }
      return getUserProfile()
    },
    {
      revalidateOnFocus: false, // Disable focus revalidation to prevent re-renders
      revalidateOnReconnect: true,
      refreshInterval: 0, // Don't auto-refresh
      dedupingInterval: 5000, // Dedupe requests for 5 seconds
      // Don't retry if user is not authenticated
      shouldRetryOnError: (error) => {
        if (error?.status === 401) return false
        return true
      },
    },
  )

  return {
    user,
    error,
    isLoading,
    isAuthenticated: !!user && !(error?.status === 401),
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
    'auth-status',
    async () => {
      return isAuthenticated()
    },
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      refreshInterval: 0,
      // Fast refresh for auth status
      dedupingInterval: 1000,
    },
  )

  return {
    isAuthenticated: isAuth || false,
    error,
    isLoading,
    mutate,
  }
}
