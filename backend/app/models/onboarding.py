from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class OnboardingFormData(BaseModel):
    """Complete onboarding form data"""
    # Step 1: Company Information
    company_name: str
    company_domain: str
    company_size: str
    
    # Step 2: Industry Information
    company_industry: str
    
    # Step 3: Company Roles
    company_roles: str
    
    # Step 4: Your Needs
    your_needs: str


class OnboardingRequest(BaseModel):
    """Request model for onboarding submission"""
    user_id: Optional[str] = None  # Will be set from JWT token
    form_data: OnboardingFormData


class OnboardingResponse(BaseModel):
    """Response model for onboarding submission"""
    success: bool
    message: str
    onboarding_id: Optional[str] = None
    workspace_created: bool = False


class OnboardingError(BaseModel):
    """Error model for onboarding"""
    error: str
    message: str
    details: Optional[dict] = None


class OnboardingStatusResponse(BaseModel):
    """Response model for onboarding status/data retrieval"""
    user_id: str
    onboarding_completed: bool
    workspace_created: bool
    onboarding_id: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    company_roles: Optional[str] = None
    your_needs: Optional[str] = None
    last_updated: Optional[str] = None
