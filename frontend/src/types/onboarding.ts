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
  onboarding_id: number
  workspace_created: boolean
  company_domain: string
  full_domain: string
}

// Company size options for validation
export type CompanySize =
  | '1-10'
  | '11-50'
  | '51-100'
  | '101-200'
  | '201-500'
  | '500+'

// Frontend form data interface (camelCase for React components)
export interface OnboardingFormData {
  companyName: string
  companyDomain: string
  companySize: CompanySize
  companyIndustry: string
  companyRoles: string
  yourNeeds: string
}

// Domain availability check response
export interface DomainAvailabilityResponse {
  domain: string
  available: boolean
  full_domain: string
  message: string
}
