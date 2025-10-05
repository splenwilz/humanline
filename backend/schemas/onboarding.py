"""
Pydantic schemas for onboarding API endpoints.

This module defines request/response models for the onboarding system:
- Input validation with business rules
- Output serialization for API responses
- Type safety and documentation
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import re
from typing import Optional


class OnboardingRequest(BaseModel):
    """
    Request schema for creating onboarding data.
    
    Validates all required fields from the frontend form:
    - Company information with business rules
    - Domain format validation for subdomain creation
    - Enum-like validation for predefined choices
    """
    
    company_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Company name as entered by user"
    )
    
    company_domain: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Company subdomain (will be prefixed to .hrline.com)"
    )
    
    company_size: str = Field(
        ...,
        description="Company size category"
    )
    
    company_industry: str = Field(
        ...,
        description="Company industry (predefined options or custom text)"
    )
    
    company_roles: str = Field(
        ...,
        description="User's role in the company (predefined options or custom text)"
    )
    
    your_needs: str = Field(
        ...,
        description="Primary HR system use case (predefined options or custom text)"
    )
    
    @field_validator('company_domain')
    @classmethod
    def validate_domain_format(cls, v):
        """
        Validate company domain format for subdomain creation.
        
        Rules:
        - Only alphanumeric characters and hyphens
        - Cannot start or end with hyphen
        - No consecutive hyphens
        - Case insensitive (converted to lowercase)
        
        This ensures valid subdomain creation for multi-tenant architecture.
        """
        if not v:
            raise ValueError('Company domain is required')
        
        # Convert to lowercase for consistency
        v = v.lower().strip()
        
        # Check format with regex
        # ^[a-z0-9] - must start with alphanumeric
        # [a-z0-9-]* - can contain alphanumeric and hyphens
        # [a-z0-9]$ - must end with alphanumeric
        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', v) and len(v) > 1:
            raise ValueError(
                'Domain must contain only letters, numbers, and hyphens. '
                'Cannot start or end with hyphen.'
            )
        elif len(v) == 1 and not re.match(r'^[a-z0-9]$', v):
            raise ValueError('Single character domain must be alphanumeric')
        
        # Prevent consecutive hyphens
        if '--' in v:
            raise ValueError('Domain cannot contain consecutive hyphens')
        
        # Reserved domain check
        reserved_domains = {'www', 'api', 'admin', 'app', 'mail', 'ftp', 'blog'}
        if v in reserved_domains:
            raise ValueError(f'Domain "{v}" is reserved and cannot be used')
        
        return v
    
    @field_validator('company_size')
    @classmethod
    def validate_company_size(cls, v):
        """Validate company size against predefined options."""
        valid_sizes = {'1-10', '11-50', '51-100', '101-200', '201-500', '500+'}
        if v not in valid_sizes:
            raise ValueError(f'Invalid company size. Must be one of: {", ".join(valid_sizes)}')
        return v
    
    @field_validator('company_industry')
    @classmethod
    def validate_company_industry(cls, v):
        """Validate company industry - accepts predefined options or custom text."""
        if not v or not v.strip():
            raise ValueError('Company industry cannot be empty')
        
        # Allow any non-empty string (predefined or custom)
        return v.strip()
    
    @field_validator('company_roles')
    @classmethod
    def validate_company_roles(cls, v):
        """Validate company roles - accepts predefined options or custom text."""
        if not v or not v.strip():
            raise ValueError('Company role cannot be empty')
        
        # Allow any non-empty string (predefined or custom)
        return v.strip()
    
    @field_validator('your_needs')
    @classmethod
    def validate_your_needs(cls, v):
        """Validate your needs - accepts predefined options or custom text."""
        if not v or not v.strip():
            raise ValueError('Your needs cannot be empty')
        
        # Allow any non-empty string (predefined or custom)
        return v.strip()
    


class OnboardingResponse(BaseModel):
    """
    Response schema for successful onboarding creation.
    
    Provides confirmation and next steps for the frontend:
    - Success confirmation with unique identifier
    - Workspace creation status for progressive flow
    - Clear messaging for user experience
    """
    
    success: bool = Field(
        default=True,
        description="Whether onboarding was successful"
    )
    
    message: str = Field(
        ...,
        description="Success message for user feedback"
    )
    
    onboarding_id: int = Field(
        ...,
        description="Unique identifier for the onboarding record"
    )
    
    workspace_created: bool = Field(
        default=False,
        description="Whether company workspace has been created"
    )
    
    company_domain: str = Field(
        ...,
        description="Confirmed company domain"
    )
    
    full_domain: str = Field(
        ...,
        description="Full domain with hrline.com suffix"
    )


class OnboardingDetail(BaseModel):
    """
    Detailed onboarding information for GET requests.
    
    Includes all onboarding data plus metadata:
    - Complete form data for frontend display
    - Status information for flow control
    - Timestamps for audit purposes
    """
    
    onboarding_id: int = Field(..., description="Unique onboarding identifier")
    user_id: int = Field(..., description="Associated user ID")
    
    # Company information
    company_name: str = Field(..., description="Company name")
    company_domain: str = Field(..., description="Company subdomain")
    company_size: str = Field(..., description="Company size category")
    company_industry: str = Field(..., description="Company industry")
    company_roles: str = Field(..., description="User's company role")
    your_needs: str = Field(..., description="Primary use case")
    
    # Status fields
    onboarding_completed: bool = Field(..., description="Completion status")
    workspace_created: bool = Field(..., description="Workspace creation status")
    
    # Computed fields
    full_domain: str = Field(..., description="Full domain with suffix")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class OnboardingStatus(BaseModel):
    """
    Lightweight status check for onboarding completion.
    
    Used for quick status checks without full data transfer:
    - Minimal payload for performance
    - Essential status information only
    """
    
    has_onboarding: bool = Field(..., description="Whether user has onboarding record")
    onboarding_completed: bool = Field(default=False, description="Whether onboarding is completed")
    workspace_created: bool = Field(default=False, description="Whether workspace is created")
    company_domain: Optional[str] = Field(None, description="Company domain if exists")
