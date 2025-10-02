import useSWR from 'swr'
import useSWRMutation from 'swr/mutation'
import { mutate } from 'swr'
import { onboardingApi } from '../api/onboarding'
import { createCacheKey } from '@/lib/swr-config'
import { toast } from 'sonner'
import type { OnboardingRequest } from '@/types/onboarding'

// Mutation fetcher
async function submitOnboardingFetcher(_: string, { arg }: { arg: OnboardingRequest }) {
  return onboardingApi.post(arg)
}

// Hook to get onboarding data
export const useOnboarding = () => {
  const {
    data: onboarding,
    error,
    isLoading,
    mutate: refetch
  } = useSWR(
    createCacheKey.onboarding(),
    () => onboardingApi.get(),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      // Don't retry if user hasn't completed onboarding yet
      shouldRetryOnError: (error) => {
        if (error?.status === 404) return false
        return true
      }
    }
  )

  return {
    onboarding,
    loading: isLoading,
    error: error?.message || null,
    refetch,
  }
}

// Hook to submit onboarding
export const useSubmitOnboarding = () => {
  const { trigger, data, error, isMutating } = useSWRMutation('/onboarding', submitOnboardingFetcher)

  const submitOnboarding = async (onboardingData: OnboardingRequest) => {
    try {
      const result = await trigger(onboardingData)
      
      // Invalidate onboarding cache
      await mutate(createCacheKey.onboarding())

      toast.success('Onboarding completed successfully!')
      return { success: true, data: result }
    } catch (error: any) {
      const errorMessage = error?.message || 'Failed to submit onboarding'
      toast.error(errorMessage)
      throw error
    }
  }

  return {
    submitOnboarding,
    data,
    error,
    isLoading: isMutating,
  }
}
