'use client'

/**
 * Enhanced Onboarding Context with comprehensive API integration
 * Implements best practices for React context with TypeScript
 */

import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
  useCallback,
} from 'react'
import { toast } from 'sonner'

// Import new API integration and types
import {
  useSubmitOnboarding,
  useDomainAvailability,
  useOnboardingValidation,
} from '@/data/hooks/useOnboarding'
import { domainValidation } from '@/data/api/onboarding'
import type { OnboardingFormData, CompanySize } from '@/types/onboarding'

/**
 * Enhanced onboarding context interface with comprehensive validation and error handling
 */
interface OnboardingContextType {
  // Current step management
  currentStep: number
  setCurrentStep: (step: number) => void
  totalSteps: number

  // Form data management with type safety
  formData: OnboardingFormData
  updateFormData: (data: Partial<OnboardingFormData>) => void
  resetFormData: () => void

  // Navigation with validation
  nextStep: () => void
  prevStep: () => void
  canGoNext: () => boolean
  canGoPrev: () => boolean
  goToStep: (step: number) => void

  // Form submission with enhanced error handling
  submitCurrentStep: () => void
  submitForm: () => Promise<void>
  isSubmitting: boolean

  // Real-time validation and feedback
  validation: {
    errors: Record<string, string>
    validateField: (field: keyof OnboardingFormData, value: string) => boolean
    validateAll: () => boolean
    clearError: (field: keyof OnboardingFormData) => void
    hasErrors: boolean
    isValid: boolean
  }

  // Domain availability checking
  domainAvailability: {
    isChecking: boolean
    isAvailable: boolean
    error: string | null
    fullDomain: string | null
    checkNow: () => void
  }

  // Step-specific validation helpers
  getStepValidation: (step: number) => {
    isValid: boolean
    errors: string[]
    requiredFields: string[]
  }

  // Progress tracking
  completedSteps: Set<number>
  markStepCompleted: (step: number) => void
}

/**
 * Initial form data with proper typing
 */
const initialFormData: OnboardingFormData = {
  companyName: '',
  companyDomain: '',
  companySize: '1-10' as CompanySize, // Default to smallest size
  companyIndustry: '',
  companyRoles: '',
  yourNeeds: '',
}

/**
 * Configuration constants
 */
const TOTAL_STEPS = 4

const OnboardingContext = createContext<OnboardingContextType | undefined>(
  undefined,
)

export const useOnboarding = () => {
  const context = useContext(OnboardingContext)
  if (!context) {
    throw new Error('useOnboarding must be used within an OnboardingProvider')
  }
  return context
}

interface OnboardingProviderProps {
  children: ReactNode
}

export const OnboardingProvider: React.FC<OnboardingProviderProps> = ({
  children,
}) => {
  // State management
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<OnboardingFormData>(initialFormData)
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set())

  // Router for navigation (used in hooks)
  // const router = useRouter() // Removed - not used directly in context

  // Enhanced hooks for API integration
  const { submitOnboarding, isLoading: isSubmitting } = useSubmitOnboarding()
  const validation = useOnboardingValidation(formData)
  const domainAvailability = useDomainAvailability(formData.companyDomain, 500)

  // Form data management with validation
  const updateFormData = useCallback(
    (data: Partial<OnboardingFormData>) => {
      setFormData((prev) => {
        const newData = { ...prev, ...data }

        // Auto-validate changed fields
        Object.keys(data).forEach((key) => {
          validation.validateField(
            key as keyof OnboardingFormData,
            newData[key as keyof OnboardingFormData],
          )
        })

        return newData
      })
    },
    [validation],
  )

  const resetFormData = useCallback(() => {
    setFormData(initialFormData)
    setCurrentStep(1)
    setCompletedSteps(new Set())
  }, [])

  // Navigation with validation
  const nextStep = useCallback(() => {
    if (currentStep < TOTAL_STEPS) {
      setCompletedSteps((prev) => new Set(prev).add(currentStep))
      setCurrentStep((prev) => prev + 1)
    }
  }, [currentStep])

  const prevStep = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1)
    }
  }, [currentStep])

  const goToStep = useCallback((step: number) => {
    if (step >= 1 && step <= TOTAL_STEPS) {
      setCurrentStep(step)
    }
  }, [])

  // Step validation logic with comprehensive checks
  const getStepValidation = useCallback(
    (step: number) => {
      const errors: string[] = []
      let isValid = true
      let requiredFields: string[] = []

      switch (step) {
        case 1:
          requiredFields = ['companyName', 'companySize']

          if (!formData.companyName.trim()) {
            errors.push('Company name is required')
            isValid = false
          }
          if (!formData.companySize.trim()) {
            errors.push('Company size is required')
            isValid = false
          }
          break

        case 2:
          requiredFields = ['companyDomain', 'companyIndustry']

          if (!formData.companyDomain.trim()) {
            errors.push('Company domain is required')
            isValid = false
          } else {
            const domainValidationResult = domainValidation.validateFormat(
              formData.companyDomain,
            )
            if (!domainValidationResult.isValid) {
              errors.push(
                domainValidationResult.error || 'Invalid domain format',
              )
              isValid = false
            }
          }

          if (
            !domainAvailability.isAvailable &&
            formData.companyDomain.trim()
          ) {
            errors.push('Domain is not available')
            isValid = false
          }

          if (!formData.companyIndustry.trim()) {
            errors.push('Company industry is required')
            isValid = false
          }
          break

        case 3:
          requiredFields = ['companyRoles']

          if (!formData.companyRoles.trim()) {
            errors.push('Your role is required')
            isValid = false
          }
          break

        case 4:
          requiredFields = ['yourNeeds']

          if (!formData.yourNeeds.trim()) {
            errors.push('Your needs selection is required')
            isValid = false
          }
          break
      }

      return { isValid, errors, requiredFields }
    },
    [formData, domainAvailability.isAvailable],
  )

  const canGoNext = useCallback(() => {
    const stepValidation = getStepValidation(currentStep)
    return stepValidation.isValid && !domainAvailability.isChecking
  }, [currentStep, getStepValidation, domainAvailability.isChecking])

  const canGoPrev = useCallback(() => {
    return currentStep > 1
  }, [currentStep])

  // Enhanced form submission with comprehensive validation
  const submitForm = useCallback(async () => {
    try {
      // Final validation before submission
      const allStepsValid = Array.from(
        { length: TOTAL_STEPS },
        (_, i) => i + 1,
      ).every((step) => getStepValidation(step).isValid)

      if (!allStepsValid) {
        toast.error('Validation Error', {
          description: 'Please complete all required fields before submitting.',
        })
        return
      }

      // Check domain availability one more time
      if (!domainAvailability.isAvailable) {
        toast.error('Domain Not Available', {
          description: 'Please choose a different company domain.',
        })
        return
      }

      // Submit using the enhanced hook
      await submitOnboarding(formData)

      // Reset form after successful submission
      resetFormData()
    } catch (error) {
      // Error handling is done in the hook
      console.error('Form submission error:', error)
    }
  }, [
    formData,
    getStepValidation,
    domainAvailability.isAvailable,
    submitOnboarding,
    resetFormData,
  ])

  // Step completion with validation
  const submitCurrentStep = useCallback(async () => {
    // First, trigger form-specific validation if available
    let formValidationPassed = true
    
    const globalWindow = window as typeof window & {
      validateForm2?: () => Promise<boolean>
      validateForm3?: () => Promise<boolean>
      validateForm4?: () => Promise<boolean>
    }
    
    if (currentStep === 2 && globalWindow.validateForm2) {
      formValidationPassed = await globalWindow.validateForm2()
    } else if (currentStep === 3 && globalWindow.validateForm3) {
      formValidationPassed = await globalWindow.validateForm3()
    } else if (currentStep === 4 && globalWindow.validateForm4) {
      formValidationPassed = await globalWindow.validateForm4()
    }

    if (!formValidationPassed) {
      toast.error('Validation Error', { 
        description: 'Please fill in all required fields correctly.' 
      })
      return
    }

    // Then run context validation
    const stepValidation = getStepValidation(currentStep)

    if (!stepValidation.isValid) {
      // Show validation errors
      stepValidation.errors.forEach((error) => {
        toast.error('Validation Error', { description: error })
      })
      return
    }

    if (currentStep === TOTAL_STEPS) {
      // Final step - submit the form
      submitForm()
    } else {
      // Move to next step
      nextStep()
    }
  }, [currentStep, getStepValidation, nextStep, submitForm])

  // Mark step as completed
  const markStepCompleted = useCallback((step: number) => {
    setCompletedSteps((prev) => new Set(prev).add(step))
  }, [])

  // Context value with comprehensive API integration
  const value: OnboardingContextType = {
    // Step management
    currentStep,
    setCurrentStep,
    totalSteps: TOTAL_STEPS,

    // Form data management
    formData,
    updateFormData,
    resetFormData,

    // Navigation
    nextStep,
    prevStep,
    canGoNext,
    canGoPrev,
    goToStep,

    // Form submission
    submitCurrentStep,
    submitForm,
    isSubmitting,

    // Validation
    validation,

    // Domain availability
    domainAvailability,

    // Step validation helpers
    getStepValidation,

    // Progress tracking
    completedSteps,
    markStepCompleted,
  }

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  )
}
