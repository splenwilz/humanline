'use client'

import React, { createContext, useContext, useState, ReactNode } from 'react'
import { onboardingApi } from '@/data/api/onboarding'
import { useRouter } from 'next/navigation'
import { toast } from "sonner"
// Define the form data interface for frontend (camelCase)
interface OnboardingFormData {
  companyName: string
  companyDomain: string
  companySize: string
  companyIndustry: string
  companyRoles: string
  yourNeeds: string
}




interface OnboardingContextType {
  // Current step
  currentStep: number
  setCurrentStep: (step: number) => void

  // Form data
  formData: OnboardingFormData
  updateFormData: (data: Partial<OnboardingFormData>) => void
  resetFormData: () => void

  // Navigation
  nextStep: () => void
  prevStep: () => void
  canGoNext: () => boolean
  canGoPrev: () => boolean

  // Form submission
  submitCurrentStep: () => void

  // Submission
  isSubmitting: boolean
  submitForm: () => Promise<void>
}

const initialFormData: OnboardingFormData = {
  companyName: '',
  companyDomain: '',
  companySize: '',
  companyIndustry: '',
  companyRoles: '',
  yourNeeds: '',
}

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
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<OnboardingFormData>(initialFormData)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const router = useRouter()

  const updateFormData = (data: Partial<OnboardingFormData>) => {
    setFormData((prev) => ({ ...prev, ...data }))
  }

  const resetFormData = () => {
    setFormData(initialFormData)
    setCurrentStep(1)
  }

  const nextStep = () => {
    if (currentStep < 4) {
      setCurrentStep((prev) => prev + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1)
    }
  }

  const canGoNext = () => {
    // Add validation logic for each step
    switch (currentStep) {
      case 1:
        return (
          formData.companyName.trim() !== '' &&
          formData.companyDomain.trim() !== '' &&
          formData.companySize.trim() !== ''
        )
      case 2:
        // Add step 2 validation
        const step2Valid =
          formData.companyDomain.trim() !== '' &&
          formData.companyIndustry.trim() !== ''

        return step2Valid
      case 3:
        const step3Valid = formData.companyRoles.trim() !== ''

        return step3Valid
      case 4:
        const step4Valid = formData.yourNeeds.trim() !== ''
        return step4Valid
      default:
        return false
    }
  }

  const canGoPrev = () => {
    return currentStep > 1
  }

  const submitCurrentStep = () => {
    if (currentStep === 4) {
      // For step 4, log all the data and then move to next step
      console.log('🎉 All Form Data Captured:', {
        formData,
      })
    }
    nextStep()
  }

  const submitForm = async () => {
    setIsSubmitting(true)
    try {
      console.log('Submitting complete form data:', formData)
      
      // Additional validation before submission
      if (!formData.companyDomain || formData.companyDomain.length < 3) {
        toast.error('Invalid Domain', {
          description: 'Please enter a valid company domain'
        })
        return
      }

      // Transform camelCase to snake_case for API
      const apiData = {
        company_name: formData.companyName,
        company_domain: formData.companyDomain,
        company_size: formData.companySize,
        company_industry: formData.companyIndustry,
        company_roles: formData.companyRoles,
        your_needs: formData.yourNeeds,
      }

      const response = await onboardingApi.post(apiData)
      
      // Show success toast
      toast.success('Onboarding completed!', {
        description: 'Welcome to Humanline! Your workspace is being set up.'
      })
      
      console.log('Form submitted successfully!', response)

      // Reset form after successful submission
      resetFormData()
      
      // Navigate to dashboard
      router.push('/dashboard')
    } catch (error) {
      console.error('Error submitting form:', error)
      
      let errorMessage = 'Failed to submit onboarding form. Please try again.'
      
      if (error instanceof Error) {
        const errorMsg = error.message.toLowerCase()
        
        if (errorMsg.includes('company domain already exists') || 
            errorMsg.includes('duplicate key value violates unique constraint') ||
            errorMsg.includes('already exists')) {
          errorMessage = 'This company domain is already taken. Please choose a different one.'
        } else if (errorMsg.includes('already completed onboarding')) {
          errorMessage = 'You have already completed onboarding.'
        } else if (errorMsg.includes('invalid or expired') || errorMsg.includes('unauthorized')) {
          errorMessage = 'Your session has expired. Please sign in again.'
          // Redirect to signin
          setTimeout(() => {
            router.push('/signin')
          }, 2000)
        } else if (errorMsg.includes('validation failed')) {
          errorMessage = 'Please check your form data and try again.'
        }
      }
      
      toast.error('Submission Failed', {
        description: errorMessage
      })
      
      throw error
    } finally {
      setIsSubmitting(false)
    }
  }

  const value: OnboardingContextType = {
    currentStep,
    setCurrentStep,
    formData,
    updateFormData,
    resetFormData,
    nextStep,
    prevStep,
    canGoNext,
    canGoPrev,
    submitCurrentStep,
    isSubmitting,
    submitForm,
  }

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  )
}
