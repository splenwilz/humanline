/**
 * Onboarding API client with comprehensive error handling and validation
 * Implements best practices for React TypeScript applications
 */

import {
  OnboardingRequest,
  OnboardingResponse,
  OnboardingDetail,
  OnboardingStatus,
  DomainAvailabilityResponse,
  OnboardingApiError,
  CompanySize
} from '@/types/onboarding'
import { apiClient } from './client'
import { ApiError, ValidationError } from './types'

/**
 * Domain validation utilities matching backend validation rules
 */
export const domainValidation = {
  /**
   * Validate domain format according to backend rules
   * - Only alphanumeric characters and hyphens
   * - Cannot start or end with hyphen
   * - No consecutive hyphens
   * - Case insensitive (converted to lowercase)
   * - Reserved domains are blocked
   */
  validateFormat: (domain: string): { isValid: boolean; error?: string } => {
    // Check if domain is provided and not empty
    if (!domain || !domain.trim()) {
      return { isValid: false, error: 'Company domain is required' }
    }

    // Convert to lowercase and trim whitespace for consistency
    const cleanDomain = domain.toLowerCase().trim()

    // Check minimum and maximum length constraints
    if (cleanDomain.length < 3) {
      return { isValid: false, error: 'Domain must be at least 3 characters long' }
    }
    if (cleanDomain.length > 50) {
      return { isValid: false, error: 'Domain must be no more than 50 characters long' }
    }

    // Validate format with regex - must start and end with alphanumeric
    if (cleanDomain.length > 1) {
      if (!/^[a-z0-9][a-z0-9-]*[a-z0-9]$/.test(cleanDomain)) {
        return { 
          isValid: false, 
          error: 'Domain must contain only letters, numbers, and hyphens. Cannot start or end with hyphen.' 
        }
      }
    } else if (!/^[a-z0-9]$/.test(cleanDomain)) {
      return { isValid: false, error: 'Single character domain must be alphanumeric' }
    }

    // Check for consecutive hyphens
    if (cleanDomain.includes('--')) {
      return { isValid: false, error: 'Domain cannot contain consecutive hyphens' }
    }

    // Check against reserved domains
    const reservedDomains = new Set(['www', 'api', 'admin', 'app', 'mail', 'ftp', 'blog'])
    if (reservedDomains.has(cleanDomain)) {
      return { isValid: false, error: `Domain "${cleanDomain}" is reserved and cannot be used` }
    }

    return { isValid: true }
  },

  /**
   * Clean and normalize domain input
   */
  normalize: (domain: string): string => {
    return domain.toLowerCase().trim()
  }
}

/**
 * Company size validation
 */
export const companySizeValidation = {
  /**
   * Valid company size options matching backend validation
   */
  validSizes: ['1-10', '11-50', '51-100', '101-200', '201-500', '500+'] as const,

  /**
   * Validate company size selection
   */
  validate: (size: string): { isValid: boolean; error?: string } => {
    if (!size || !size.trim()) {
      return { isValid: false, error: 'Company size is required' }
    }

    if (!companySizeValidation.validSizes.includes(size as CompanySize)) {
      return { 
        isValid: false, 
        error: `Invalid company size. Must be one of: ${companySizeValidation.validSizes.join(', ')}` 
      }
    }

    return { isValid: true }
  }
}

/**
 * Enhanced onboarding API client with comprehensive error handling
 */
export const onboardingApi = {
  /**
   * Create onboarding record with comprehensive validation and error handling
   * Transforms camelCase frontend data to snake_case backend format
   */
  create: async (data: OnboardingRequest): Promise<OnboardingResponse> => {
    try {
      // Client-side validation before API call to provide immediate feedback
      const domainCheck = domainValidation.validateFormat(data.company_domain)
      if (!domainCheck.isValid) {
        throw new ValidationError(domainCheck.error!, { field: 'company_domain' })
      }

      const sizeCheck = companySizeValidation.validate(data.company_size)
      if (!sizeCheck.isValid) {
        throw new ValidationError(sizeCheck.error!, { field: 'company_size' })
      }

      // Normalize domain before sending to backend
      const normalizedData = {
        ...data,
        company_domain: domainValidation.normalize(data.company_domain)
      }

      // Make API request with normalized data
      const response = await apiClient.post<OnboardingResponse>('/onboarding', normalizedData)
      return response

    } catch (error) {
      // Enhanced error handling with specific error types
      if (error instanceof ValidationError) {
        throw error // Re-throw validation errors as-is
      }

      if (error instanceof ApiError) {
        // Handle specific API error codes from backend
        const apiError = error as ApiError & { detail?: OnboardingApiError }
        
        if (apiError.detail?.error_code === 'DUPLICATE_ONBOARDING') {
          throw new ValidationError('You have already completed onboarding', { 
            field: 'user',
            code: 'DUPLICATE_ONBOARDING' 
          })
        }
        
        if (apiError.detail?.error_code === 'DOMAIN_TAKEN') {
          throw new ValidationError('This company domain is already taken. Please choose a different one.', { 
            field: 'company_domain',
            code: 'DOMAIN_TAKEN' 
          })
        }

        // Generic API error with user-friendly message
        throw new ValidationError(
          apiError.detail?.message || 'Failed to create onboarding record. Please try again.',
          { code: apiError.detail?.error_code || 'API_ERROR' }
        )
      }

      // Handle unexpected errors
      console.error('Unexpected error in onboarding creation:', error)
      throw new ValidationError('An unexpected error occurred. Please try again.', { 
        code: 'UNKNOWN_ERROR' 
      })
    }
  },

  /**
   * Retrieve user's onboarding data with error handling
   */
  get: async (): Promise<OnboardingDetail> => {
    try {
      const response = await apiClient.get<OnboardingDetail>('/onboarding')
      return response

    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        // User hasn't completed onboarding yet - this is expected
        throw new ValidationError('No onboarding record found', { 
          code: 'ONBOARDING_NOT_FOUND' 
        })
      }

      // Handle other API errors
      console.error('Error fetching onboarding data:', error)
      throw new ValidationError('Failed to retrieve onboarding information', { 
        code: 'FETCH_ERROR' 
      })
    }
  },

  /**
   * Get lightweight onboarding status for flow control
   * This endpoint should never fail completely
   */
  getStatus: async (): Promise<OnboardingStatus> => {
    try {
      const response = await apiClient.get<OnboardingStatus>('/onboarding/status')
      return response

    } catch (error) {
      // Return default status if API fails - prevents blocking user flow
      console.warn('Failed to fetch onboarding status, returning default:', error)
      return {
        has_onboarding: false,
        onboarding_completed: false,
        workspace_created: false,
        company_domain: null
      }
    }
  },

  /**
   * Check domain availability with debouncing support
   * Used for real-time validation during user input
   */
  checkDomainAvailability: async (domain: string): Promise<DomainAvailabilityResponse> => {
    try {
      // Client-side validation first to avoid unnecessary API calls
      const validation = domainValidation.validateFormat(domain)
      if (!validation.isValid) {
        throw new ValidationError(validation.error!, { 
          field: 'domain',
          code: 'INVALID_DOMAIN_FORMAT' 
        })
      }

      // Normalize domain before checking
      const normalizedDomain = domainValidation.normalize(domain)
      
      // Make API request to check availability
      const response = await apiClient.get<DomainAvailabilityResponse>(
        `/onboarding/check-domain/${encodeURIComponent(normalizedDomain)}`
      )
      
      return response

    } catch (error) {
      if (error instanceof ValidationError) {
        throw error // Re-throw validation errors
      }

      if (error instanceof ApiError) {
        const apiError = error as ApiError & { detail?: OnboardingApiError }
        
        if (apiError.status === 422) {
          throw new ValidationError(
            apiError.detail?.message || 'Invalid domain format',
            { field: 'domain', code: 'INVALID_DOMAIN_FORMAT' }
          )
        }
      }

      // Handle unexpected errors gracefully
      console.error('Error checking domain availability:', error)
      throw new ValidationError('Unable to check domain availability. Please try again.', { 
        code: 'AVAILABILITY_CHECK_ERROR' 
      })
    }
  }
}

/**
 * Legacy API methods for backward compatibility
 * @deprecated Use onboardingApi.create and onboardingApi.get instead
 */
export const legacyOnboardingApi = {
  post: onboardingApi.create,
  get: onboardingApi.get
}
