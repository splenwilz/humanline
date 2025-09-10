from fastapi import APIRouter, HTTPException, status, Depends
from app.models.onboarding import OnboardingRequest, OnboardingResponse, OnboardingError, OnboardingFormData, OnboardingStatusResponse
from app.services.onboarding_service import onboarding_service
from app.dependencies.auth import get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post(
    "",
    response_model=OnboardingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit onboarding form data",
    description="Process and store onboarding form data for a new company workspace",
    responses={
        401: {"description": "Unauthorized - Invalid or expired token"},
        422: {"description": "Validation Error"}
    }
)
async def create_onboarding(
    form_data: OnboardingFormData,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Submit onboarding form data
    
    This endpoint processes the complete onboarding form data including:
    - Company information (name, domain, size)
    - Industry information
    - Company roles
    - User needs
    
    Args:
        request: OnboardingRequest containing form_data (user_id from JWT token)
        current_user_id: Authenticated user ID from JWT token
        
    Returns:
        OnboardingResponse with success status and details
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        # Use authenticated user ID from JWT token
        authenticated_request = OnboardingRequest(
            user_id=current_user_id,
            form_data=form_data
        )
        
        logger.info(f"Received onboarding submission for user: {current_user_id}")
        logger.info(f"Company: {form_data.company_name}")
        
        # Process the onboarding data
        result = await onboarding_service.submit_onboarding(authenticated_request)
        
        if not result.success:
            logger.warning(f"Onboarding failed for user {current_user_id}: {result.message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        logger.info(f"Onboarding successful for user {current_user_id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in onboarding submission for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during onboarding processing"
        )


@router.get(
    "",
    response_model=OnboardingStatusResponse,
    summary="Get onboarding data",
    description="Get onboarding data for the authenticated user"
)
async def get_onboarding(current_user_id: str = Depends(get_current_user_id)):
    """
    Get onboarding data for the authenticated user
        
    Returns:
        dict: Onboarding data and status information
    """
    try:
        # Get onboarding status from Supabase
        status_data = await onboarding_service.get_onboarding_status(current_user_id)
        return status_data
        
    except Exception as e:
        logger.error(f"Error getting onboarding status for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving onboarding status"
        )


@router.get(
    "/check-domain",
    response_model=dict,
    summary="Check domain availability",
    description="Check if a company domain is available for use"
)
async def check_domain_availability(domain: str):
    """
    Check if a company domain is available.
    
    This endpoint checks if the provided domain is already taken by another company.
    """
    try:
        if not domain or len(domain.strip()) < 3:
            return {
                "available": True,
                "message": "Domain too short"
            }
        
        # Check if domain exists in the database
        is_available = await onboarding_service.check_domain_availability(domain.strip())
        
        return {
            "available": is_available,
            "message": "Domain is available" if is_available else "Domain is already taken"
        }
        
    except Exception as e:
        logger.error(f"Error checking domain availability for {domain}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking domain availability"
        )
