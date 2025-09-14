// This is the response for the GET onboarding
export interface Onboarding {
  user_id: string
  onboarding_completed: boolean
  workspace_created: boolean
  onboarding_id: string
  company_name: string
  company_domain: string
  company_size: string
  company_industry: string
  company_roles: string
  your_needs: string
  last_updated: string
}

// This is the request for the POST onboarding
export type OnboardingRequest = Omit<
  Onboarding,
  | 'user_id'
  | 'onboarding_completed'
  | 'workspace_created'
  | 'last_updated'
  | 'onboarding_id'
>

// This is the response for the POST onboarding
export interface OnboardingResponse {
  success: boolean
  message: string
  onboarding_id: string
  workspace_created: boolean
}
