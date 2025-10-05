"""
Onboarding API endpoints for company setup and user preferences.

This module provides REST endpoints for the onboarding process:
- POST /onboarding: Create onboarding record
- GET /onboarding: Retrieve user's onboarding data
- GET /onboarding/status: Check onboarding completion status
- GET /onboarding/check-domain/{domain}: Check domain availability
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_active_user
from models.user import User
from schemas.onboarding import (
    OnboardingRequest, 
    OnboardingResponse, 
    OnboardingDetail, 
    OnboardingStatus
)
from services.onboarding_service import OnboardingService


# Create router with onboarding-specific configuration
router = APIRouter(
    prefix="/onboarding",
    tags=["Onboarding"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Access forbidden"},
        422: {"description": "Validation error"},
    }
)


@router.post(
    "",
    response_model=OnboardingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Onboarding Record",
    description="Complete onboarding process with company information and user preferences"
)
async def create_onboarding(
    onboarding_data: OnboardingRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> OnboardingResponse:
    """
    Create onboarding record for authenticated user.
    
    This endpoint handles the complete onboarding flow:
    1. Validates all form data using Pydantic schemas
    2. Checks for duplicate onboarding (one per user)
    3. Enforces domain uniqueness across all tenants
    4. Creates onboarding record with user association
    5. Returns success confirmation with next steps
    
    **Business Rules:**
    - Each user can only complete onboarding once
    - Company domains must be unique across all tenants
    - Domain format must be valid for subdomain creation
    - All form fields are required and validated
    
    **Security:**
    - Requires valid JWT authentication
    - User must have active account status
    - Input validation prevents injection attacks
    
    Args:
        onboarding_data: Complete onboarding form data
        current_user: Authenticated user from JWT token
        db: Database session dependency
        
    Returns:
        OnboardingResponse: Success confirmation with onboarding metadata
        
    Raises:
        HTTPException 400: Business rule violations (duplicate, domain taken)
        HTTPException 422: Validation errors in request data
        HTTPException 500: Unexpected server errors
    """
    try:
        # Create onboarding record using service layer
        # Service handles all business logic and database operations
        onboarding_response = await OnboardingService.create_onboarding(
            db=db,
            user_id=current_user.id,
            onboarding_data=onboarding_data
        )
        
        return onboarding_response
        
    except ValueError as e:
        # Handle business rule violations with user-friendly messages
        # These are expected errors from business logic validation
        error_message = str(e)
        
        # Provide specific error codes for frontend handling
        if "already completed onboarding" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": error_message,
                    "error_code": "DUPLICATE_ONBOARDING",
                    "field": "user"
                }
            )
        elif "domain" in error_message and "already taken" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": error_message,
                    "error_code": "DOMAIN_TAKEN",
                    "field": "company_domain"
                }
            )
        else:
            # Generic business rule violation
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": error_message,
                    "error_code": "VALIDATION_ERROR"
                }
            )
    
    except Exception as e:
        # Handle unexpected errors with generic message
        # Log actual error for debugging while hiding internals from user
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create onboarding record. Please try again."
        )


@router.get(
    "",
    response_model=OnboardingDetail,
    summary="Get User Onboarding",
    description="Retrieve complete onboarding information for authenticated user"
)
async def get_onboarding(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> OnboardingDetail:
    """
    Retrieve onboarding record for authenticated user.
    
    Returns complete onboarding data including:
    - All company information from forms
    - Status flags for flow control
    - Timestamps for audit purposes
    - Computed fields (full domain)
    
    **Use Cases:**
    - Frontend form pre-population
    - Dashboard company information display
    - Onboarding status verification
    - Audit and compliance reporting
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session dependency
        
    Returns:
        OnboardingDetail: Complete onboarding information
        
    Raises:
        HTTPException 404: User has no onboarding record
        HTTPException 500: Database or server errors
    """
    try:
        # Retrieve onboarding data using service layer
        onboarding = await OnboardingService.get_user_onboarding(
            db=db,
            user_id=current_user.id
        )
        
        if not onboarding:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "No onboarding record found for user",
                    "error_code": "ONBOARDING_NOT_FOUND"
                }
            )
        
        return onboarding
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 above)
        raise
    
    except Exception as e:
        # Handle unexpected database or server errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve onboarding information"
        )


@router.get(
    "/status",
    response_model=OnboardingStatus,
    summary="Check Onboarding Status",
    description="Get lightweight onboarding completion status for flow control"
)
async def get_onboarding_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> OnboardingStatus:
    """
    Get onboarding status for authenticated user.
    
    Lightweight endpoint for quick status checks:
    - Minimal data transfer for performance
    - Used by frontend for routing decisions
    - No sensitive data exposure
    
    **Performance Optimized:**
    - Single database query with selected fields only
    - No JOIN operations or complex calculations
    - Suitable for frequent polling or middleware checks
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session dependency
        
    Returns:
        OnboardingStatus: Completion flags and basic info
    """
    try:
        # Get status using optimized service method
        status_info = await OnboardingService.get_onboarding_status(
            db=db,
            user_id=current_user.id
        )
        
        return status_info
        
    except Exception as e:
        # Handle errors gracefully with default status
        # This endpoint should never fail completely
        return OnboardingStatus(
            has_onboarding=False,
            onboarding_completed=False,
            workspace_created=False,
            company_domain=None
        )


@router.get(
    "/check-domain/{domain}",
    summary="Check Domain Availability",
    description="Verify if company domain is available for registration"
)
async def check_domain_availability(
    domain: str = Path(..., min_length=3, max_length=50, description="Company domain to check"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Check if company domain is available for registration.
    
    Real-time domain validation for frontend form:
    - Immediate feedback during user input
    - Prevents form submission with taken domains
    - Validates domain format requirements
    
    **Rate Limiting Recommended:**
    - This endpoint may be called frequently during typing
    - Consider implementing rate limiting in production
    - Cache results for common domain checks
    
    Args:
        domain: Company domain to validate
        current_user: Authenticated user (required for rate limiting)
        db: Database session dependency
        
    Returns:
        dict: Availability status and validation info
        
    Raises:
        HTTPException 422: Invalid domain format
    """
    try:
        # Validate domain format using same rules as onboarding
        # This ensures consistency between validation and creation
        from schemas.onboarding import OnboardingRequest
        
        # Create temporary request object for validation
        # This reuses existing validation logic without duplication
        temp_request = OnboardingRequest(
            company_name="temp",  # Required but not used for domain validation
            company_domain=domain,
            company_size="1-10",  # Required but not used
            company_industry="fintech",  # Required but not used - use valid value
            company_roles="ceo-founder-owner",  # Required but not used - use valid value
            your_needs="onboarding-new-employees"  # Required but not used - use valid value
        )
        
        # If validation passes, check availability
        is_available = await OnboardingService.check_domain_availability(
            db=db,
            domain=temp_request.company_domain  # Use validated domain
        )
        
        return {
            "domain": temp_request.company_domain,
            "available": is_available,
            "full_domain": f"{temp_request.company_domain}.hrline.com",
            "message": "Domain is available" if is_available else "Domain is already taken"
        }
        
    except ValueError as e:
        # Handle domain format validation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": str(e),
                "error_code": "INVALID_DOMAIN_FORMAT",
                "field": "domain"
            }
        )
    
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check domain availability"
        )
