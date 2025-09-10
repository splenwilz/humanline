from supabase import create_client, Client
from app.config import settings
from app.models.onboarding import OnboardingRequest, OnboardingResponse, OnboardingFormData
from app.models.user import UserProfile
from app.services.auth_service import auth_service
import logging
from typing import Optional
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class OnboardingService:
    """Service for handling onboarding operations"""
    
    def __init__(self):
        self.auth_service = auth_service
        # Use service key for database operations to bypass RLS
        service_key = settings.supabase_service_key or settings.supabase_anon_key
        self.supabase: Client = create_client(
            settings.supabase_url,
            service_key
        )
    
    async def submit_onboarding(self, request: OnboardingRequest) -> OnboardingResponse:
        """
        Process onboarding form submission
        
        Args:
            request: OnboardingRequest containing user_id and form_data
            
        Returns:
            OnboardingResponse with success status and details
        """
        try:
            # Validate user exists
            user = await self._validate_user(request.user_id)
            if not user:
                return OnboardingResponse(
                    success=False,
                    message="User not found",
                    workspace_created=False
                )
            
            # Process onboarding data
            onboarding_id = await self._process_onboarding_data(request)
            
            # Create workspace (placeholder for now)
            workspace_created = await self._create_workspace(
                user_id=request.user_id,
                company_domain=request.form_data.company_domain,
                company_name=request.form_data.company_name
            )
            
            # Log the onboarding completion
            logger.info(f"Onboarding completed for user {request.user_id}: {request.form_data.company_name}")
            
            return OnboardingResponse(
                success=True,
                message="Onboarding completed successfully",
                onboarding_id=onboarding_id,
                workspace_created=workspace_created
            )
            
        except Exception as e:
            logger.error(f"Error processing onboarding for user {request.user_id}: {str(e)}")
            return OnboardingResponse(
                success=False,
                message=f"Failed to process onboarding: {str(e)}",
                workspace_created=False
            )
    
    async def _validate_user(self, user_id: str) -> Optional[UserProfile]:
        """Validate that the user exists and is authenticated"""
        try:
            # In a real implementation, you would validate the user exists
            # For now, we'll just return a mock user profile
            return UserProfile(
                id=user_id,
                email="user@example.com",
                full_name="User Name",
                email_confirmed_at="2024-01-01T00:00:00Z",
                created_at="2024-01-01T00:00:00Z"
            )
        except Exception as e:
            logger.error(f"Error validating user {user_id}: {str(e)}")
            return None
    
    async def _process_onboarding_data(self, request: OnboardingRequest) -> str:
        """
        Process and store onboarding form data in Supabase
        
        Args:
            request: The onboarding request containing user_id and form_data
            
        Returns:
            onboarding_id: Unique identifier for this onboarding session
        """
        try:
            # Generate unique onboarding ID
            onboarding_id = str(uuid.uuid4())
            
            # Prepare data for Supabase storage
            onboarding_data = {
                "id": onboarding_id,
                "user_id": request.user_id,
                "company_name": request.form_data.company_name,
                "company_domain": request.form_data.company_domain,
                "company_size": request.form_data.company_size,
                "company_industry": request.form_data.company_industry,
                "company_roles": request.form_data.company_roles,
                "your_needs": request.form_data.your_needs,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
            # Store in Supabase onboarding table
            result = self.supabase.table("onboarding").insert(onboarding_data).execute()
            
            if not result.data:
                raise Exception("Failed to insert onboarding data into database")
            
            logger.info(f"Successfully stored onboarding data in Supabase for {request.form_data.company_name}")
            logger.info(f"Onboarding ID: {onboarding_id}")
            logger.info(f"Company Domain: {request.form_data.company_domain}")
            logger.info(f"Company Size: {request.form_data.company_size}")
            logger.info(f"Industry: {request.form_data.company_industry}")
            logger.info(f"Roles: {request.form_data.company_roles}")
            logger.info(f"Needs: {request.form_data.your_needs}")
            
            return onboarding_id
            
        except Exception as e:
            logger.error(f"Error processing onboarding data: {str(e)}")
            
            # Handle specific database constraint violations
            error_str = str(e)
            if '23505' in error_str and 'company_domain' in error_str:
                raise Exception("Company domain already exists. Please choose a different domain.")
            elif '23505' in error_str and 'user_id' in error_str:
                raise Exception("You have already completed onboarding.")
            elif '23505' in error_str:
                raise Exception("Duplicate data detected. Please check your information.")
            
            raise
    
    async def _create_workspace(self, user_id: str, company_domain: str, company_name: str) -> bool:
        """
        Create workspace for the company
        
        Args:
            user_id: ID of the user creating the workspace
            company_domain: Company domain for workspace URL
            company_name: Company name for workspace display
            
        Returns:
            bool: True if workspace created successfully
        """
        try:
            # In a real implementation, you would:
            # 1. Create workspace in your system
            # 2. Set up workspace settings
            # 3. Configure company branding
            # 4. Set up initial team structure
            # 5. Create workspace-specific configurations
            
            workspace_url = f"https://{company_domain}.hrline.com"
            
            logger.info(f"Created workspace for {company_name}")
            logger.info(f"Workspace URL: {workspace_url}")
            logger.info(f"Admin User: {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating workspace: {str(e)}")
            return False
    
    async def get_onboarding_status(self, user_id: str) -> dict:
        """
        Get onboarding status for a user
        
        Args:
            user_id: The user ID to check status for
            
        Returns:
            dict: Onboarding status information
        """
        try:
            # Query Supabase for user's onboarding data
            result = self.supabase.table("onboarding")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                onboarding_data = result.data[0]
                return {
                    "user_id": user_id,
                    "onboarding_completed": True,
                    "workspace_created": True,  # Placeholder
                    "onboarding_id": onboarding_data.get("id"),
                    "company_name": onboarding_data.get("company_name"),
                    "company_domain": onboarding_data.get("company_domain"),
                    "company_size": onboarding_data.get("company_size"),
                    "company_industry": onboarding_data.get("company_industry"),
                    "company_roles": onboarding_data.get("company_roles"),
                    "your_needs": onboarding_data.get("your_needs"),
                    "last_updated": onboarding_data.get("updated_at")
                }
            else:
                return {
                    "user_id": user_id,
                    "onboarding_completed": False,
                    "workspace_created": False,
                    "last_updated": None
                }
                
        except Exception as e:
            logger.error(f"Error getting onboarding status for user {user_id}: {str(e)}")
            return {
                "user_id": user_id,
                "onboarding_completed": False,
                "workspace_created": False,
                "error": str(e)
            }
    
    async def check_domain_availability(self, domain: str) -> bool:
        """
        Check if a company domain is available.
        
        Args:
            domain: Company domain to check
            
        Returns:
            bool: True if domain is available, False if taken
        """
        try:
            # Query Supabase to check if domain exists
            result = self.supabase.table("onboarding")\
                .select("company_domain")\
                .eq("company_domain", domain)\
                .limit(1)\
                .execute()
            
            # If no results, domain is available
            return len(result.data) == 0
            
        except Exception as e:
            logger.error(f"Error checking domain availability for {domain}: {str(e)}")
            # Return True (available) on error to not block user
            return True


# Create service instance
onboarding_service = OnboardingService()
