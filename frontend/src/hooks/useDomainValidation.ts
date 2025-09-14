import useSWR from 'swr'
import { apiClient } from '@/data/api/client'

interface DomainValidationResult {
  isValid: boolean
  isChecking: boolean
  message: string
}

interface DomainCheckResponse {
  available: boolean
  message: string
}

export const useDomainValidation = (domain: string) => {
  // Only validate if domain is long enough
  const shouldValidate = domain && domain.length >= 3

  const { data, error, isLoading } = useSWR<DomainCheckResponse>(
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
    isValid: shouldValidate ? (data?.available ?? true) : true,
    isChecking: isLoading,
    message: shouldValidate
      ? (data?.message ?? '')
      : domain && domain.length < 3
        ? 'Domain too short'
        : '',
  }

  return result
}
