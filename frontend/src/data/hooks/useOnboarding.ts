/**
 * Enhanced onboarding hooks with comprehensive error handling and validation
 * Implements React Query/SWR best practices for API state management
 */

import useSWR from 'swr'
import useSWRMutation from 'swr/mutation'
import { mutate } from 'swr'
import { useState, useCallback, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

import { onboardingApi, domainValidation as domainValidationUtils } from '../api/onboarding'
import { createCacheKey } from '@/lib/swr-config'
import { ValidationError } from '../api/types'
import { useTokenRefresh } from './useAuth'
import { getRefreshToken } from '@/lib/auth'
import type { 
  OnboardingRequest, 
  OnboardingFormData,
  DomainAvailabilityResponse,
  CompanySize
} from '@/types/onboarding'

/**
 * Transform camelCase frontend data to snake_case backend format
 */
const transformFormDataToRequest = (formData: OnboardingFormData): OnboardingRequest => ({
  company_name: formData.companyName,
  company_domain: formData.companyDomain,
  company_size: formData.companySize,
  company_industry: formData.companyIndustry,
  company_roles: formData.companyRoles,
  your_needs: formData.yourNeeds
})

/**
 * Hook to get detailed onboarding data with proper error handling
 */
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
      // Performance optimizations
      revalidateOnFocus: false,        // Don't refetch when window regains focus
      revalidateOnReconnect: true,     // Refetch when network reconnects
      dedupingInterval: 60000,         // Dedupe requests within 1 minute
      
      // Error handling - don't retry for expected 404s
      shouldRetryOnError: (error) => {
        // Don't retry if user hasn't completed onboarding (404 is expected)
        if (error instanceof ValidationError && error.message.includes('No onboarding record found')) {
          return false
        }
        // Don't retry for client errors (4xx)
        if (error?.status >= 400 && error?.status < 500) {
          return false
        }
        return true
      },
      
      // Retry configuration for server errors
      errorRetryCount: 3,
      errorRetryInterval: 1000
    }
  )

  return {
    onboarding,
    loading: isLoading,
    error: error?.message || null,
    refetch,
    // Helper to check if user has completed onboarding
    hasOnboarding: !!onboarding,
    isCompleted: onboarding?.onboarding_completed || false
  }
}

/**
 * Hook to get lightweight onboarding status for flow control
 * This should never fail and block user navigation
 */
export const useOnboardingStatus = () => {
  const {
    data: status,
    error,
    isLoading,
    mutate: refetch
  } = useSWR(
    createCacheKey.onboardingStatus(),
    () => onboardingApi.getStatus(),
    {
      // Aggressive caching for status checks
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      dedupingInterval: 30000,         // Cache for 30 seconds
      
      // Never retry on error - return default status instead
      shouldRetryOnError: () => false,
      
      // Fallback data if API fails
      fallbackData: {
        has_onboarding: false,
        onboarding_completed: false,
        workspace_created: false,
        company_domain: null
      }
    }
  )

  return {
    status: status || {
      has_onboarding: false,
      onboarding_completed: false,
      workspace_created: false,
      company_domain: null
    },
    loading: isLoading,
    error: error?.message || null,
    refetch
  }
}

/**
 * Hook to submit onboarding with comprehensive error handling and user feedback
 */
export const useSubmitOnboarding = () => {
  const router = useRouter()
  const { refreshToken } = useTokenRefresh()
  
  // SWR mutation for API call
  const { trigger, data, error, isMutating } = useSWRMutation(
    '/onboarding/create',
    async (_: string, { arg }: { arg: OnboardingRequest }) => {
      return onboardingApi.create(arg)
    }
  )

  const submitOnboarding = useCallback(async (formData: OnboardingFormData) => {
    try {
      // Transform frontend data to backend format
      const requestData = transformFormDataToRequest(formData)
      
      // Submit to API
      const result = await trigger(requestData)
      
      // Show success feedback with provisioning message
      toast.success('Onboarding completed!', {
        description: `Provisioning your workspace at ${result.full_domain}...`,
        duration: 4000
      })
      
      // Add a small delay to show provisioning state and prevent flash
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Refresh the access token to get updated needs_onboarding status
      // This must happen BEFORE navigation to prevent middleware redirect loop
      try {
        const currentRefreshToken = getRefreshToken()
        if (currentRefreshToken) {
          await refreshToken(currentRefreshToken)
        }
      } catch (tokenError) {
        console.warn('Failed to refresh token after onboarding:', tokenError)
        // Continue anyway - the backend has updated the user status
      }
      
      // Invalidate all onboarding-related cache and user cache
      await Promise.all([
        mutate(createCacheKey.onboarding()),
        mutate(createCacheKey.onboardingStatus()),
        mutate(createCacheKey.user()) // Refresh user data
      ])

      // Show final success message
      toast.success('Welcome to Humanline!', {
        description: 'Your workspace is ready. Redirecting to dashboard...',
        duration: 2000
      })

      // Navigate to dashboard after provisioning delay
      // The refreshed token now has needs_onboarding: false
      router.push('/dashboard')

      return { success: true, data: result }

    } catch (error) {
      // Enhanced error handling with specific user feedback
      let errorMessage = 'Failed to submit onboarding form. Please try again.'
      let errorDescription = ''

      if (error instanceof ValidationError) {
        errorMessage = error.message
        
        // Provide specific guidance based on error code
        if (error.details?.code === 'DOMAIN_TAKEN') {
          errorDescription = 'Try adding numbers or hyphens to make it unique.'
        } else if (error.details?.code === 'DUPLICATE_ONBOARDING') {
          errorDescription = 'Redirecting you to the dashboard...'
          setTimeout(() => router.push('/dashboard'), 2000)
        } else if (error.details?.field === 'company_domain') {
          errorDescription = 'Please check your domain format and try again.'
        }
      }

      // Show error toast with guidance
      toast.error(errorMessage, {
        description: errorDescription,
        duration: 6000
      })

      throw error
    }
  }, [trigger, router, refreshToken])

  return {
    submitOnboarding,
    data,
    error: error?.message || null,
    isLoading: isMutating
  }
}

/**
 * Hook for real-time domain availability checking with debouncing
 */
export const useDomainAvailability = (domain: string, debounceMs: number = 500) => {
  const [availability, setAvailability] = useState<DomainAvailabilityResponse | null>(null)
  const [isChecking, setIsChecking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  const checkAvailability = useCallback(async (domainToCheck: string) => {
    // Skip empty or invalid domains
    if (!domainToCheck || domainToCheck.length < 3) {
      setAvailability(null)
      setError(null)
      return
    }

    // Client-side validation first
    const validation = domainValidationUtils.validateFormat(domainToCheck)
    if (!validation.isValid) {
      setAvailability(null)
      setError(validation.error || 'Invalid domain format')
      return
    }

    setIsChecking(true)
    setError(null)

    try {
      const result = await onboardingApi.checkDomainAvailability(domainToCheck)
      setAvailability(result)
    } catch (err) {
      if (err instanceof ValidationError) {
        setError(err.message)
      } else {
        setError('Unable to check domain availability')
      }
      setAvailability(null)
    } finally {
      setIsChecking(false)
    }
  }, [])

  // Debounced effect for domain checking
  useEffect(() => {
    // Clear previous timeout
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    // Set new timeout for debounced checking
    debounceRef.current = setTimeout(() => {
      checkAvailability(domain)
    }, debounceMs)

    // Cleanup timeout on unmount or dependency change
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [domain, debounceMs, checkAvailability])

  return {
    availability,
    isChecking,
    error,
    // Helper properties for easy access
    isAvailable: availability?.available || false,
    fullDomain: availability?.full_domain || null,
    // Manual trigger for immediate checking
    checkNow: () => checkAvailability(domain)
  }
}

/**
 * Hook for form validation with real-time feedback
 */
export const useOnboardingValidation = (formData: OnboardingFormData) => {
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  const validateField = useCallback((field: keyof OnboardingFormData, value: string): boolean => {
    let error = ''

    switch (field) {
      case 'companyName':
        if (!value.trim()) {
          error = 'Company name is required'
        } else if (value.length < 2) {
          error = 'Company name must be at least 2 characters'
        } else if (value.length > 255) {
          error = 'Company name must be less than 255 characters'
        }
        break

      case 'companyDomain':
        const domainValidationResult = domainValidationUtils.validateFormat(value)
        if (!domainValidationResult.isValid) {
          error = domainValidationResult.error || 'Invalid domain format'
        }
        break

      case 'companySize':
        if (!value.trim()) {
          error = 'Company size is required'
        }
        break

      case 'companyIndustry':
        if (!value.trim()) {
          error = 'Company industry is required'
        }
        break

      case 'companyRoles':
        if (!value.trim()) {
          error = 'Your role is required'
        }
        break

      case 'yourNeeds':
        if (!value.trim()) {
          error = 'Your needs selection is required'
        }
        break
    }

    setErrors(prev => ({
      ...prev,
      [field]: error
    }))

    return error === ''
  }, [])

  const validateAll = useCallback(() => {
    let isValid = true

    // Validate all fields
    Object.entries(formData).forEach(([field, value]) => {
      const fieldValid = validateField(field as keyof OnboardingFormData, value)
      if (!fieldValid) {
        isValid = false
      }
    })

    return isValid
  }, [formData, validateField])

  const clearError = useCallback((field: keyof OnboardingFormData) => {
    setErrors(prev => ({
      ...prev,
      [field]: ''
    }))
  }, [])

  return {
    errors,
    validateField,
    validateAll,
    clearError,
    hasErrors: Object.values(errors).some(error => error !== ''),
    isValid: Object.values(errors).every(error => error === '') && 
             Object.values(formData).every(value => value.trim() !== '')
  }
}

/**
 * Legacy hooks for backward compatibility
 * @deprecated Use the new hooks above instead
 */
export const useSubmitOnboardingLegacy = () => {
  const { submitOnboarding, ...rest } = useSubmitOnboarding()
  
  return {
    ...rest,
    submitOnboarding: async (data: OnboardingRequest) => {
      // Convert snake_case to camelCase for new hook
      const formData: OnboardingFormData = {
        companyName: data.company_name,
        companyDomain: data.company_domain,
        companySize: data.company_size as CompanySize,
        companyIndustry: data.company_industry,
        companyRoles: data.company_roles,
        yourNeeds: data.your_needs
      }
      return submitOnboarding(formData)
    }
  }
}
