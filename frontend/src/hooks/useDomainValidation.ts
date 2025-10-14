import useSWR from 'swr'
import { apiClient } from '@/data/api/client'

interface DomainValidationResult {
  isValid: boolean
  isChecking: boolean
  message: string
  error?: Error
}

interface DomainCheckResponse {
  available: boolean
  message: string
}

export const useDomainValidation = (domain: string) => {
  // Only validate if domain is long enough
  const shouldValidate = domain && domain.length >= 3

  const { data, isLoading, error } = useSWR<DomainCheckResponse>(
    shouldValidate
      ? `/onboarding/check-domain?domain=${encodeURIComponent(domain)}`
      : null,
    async (url: string) => {
      const response = await apiClient.get<DomainCheckResponse>(url)
      return response
    },
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      dedupingInterval: 1000, // Debounce by 1 second
    },
  )

  const result: DomainValidationResult = {
    isValid: shouldValidate ? (error ? false : (data?.available ?? false)) : true,
    isChecking: isLoading,
    message: shouldValidate
      ? (error ? 'Failed to validate domain. Please try again.' : (data?.message ?? ''))
      : domain && domain.length < 3
        ? 'Domain too short'
        : '',
    error: error,
  }

  return result
}
