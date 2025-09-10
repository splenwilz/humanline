import { Onboarding, OnboardingRequest, OnboardingResponse } from '@/types/onboarding'
import { apiClient } from './client'

export const onboardingApi = {
  post: async (data: OnboardingRequest): Promise<OnboardingResponse> => {
    const response = await apiClient.post('/onboarding', data) as { data: OnboardingResponse }
    return response.data
  },
  get: async (): Promise<Onboarding> => {
    const response = await apiClient.get('/onboarding') as { data: Onboarding }
    return response.data
  },
}