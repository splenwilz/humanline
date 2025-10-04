"""
Onboarding service for business logic and database operations.

This service handles:
- Onboarding creation with validation
- Domain uniqueness enforcement
- User association and status tracking
- Database transaction management
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.onboarding import Onboarding
from models.user import User
from schemas.onboarding import OnboardingRequest, OnboardingResponse, OnboardingDetail, OnboardingStatus


class OnboardingService:
    """Service class for onboarding operations with comprehensive error handling."""
    
    @staticmethod
    async def create_onboarding(
        db: AsyncSession, 
        user_id: int, 
        onboarding_data: OnboardingRequest
    ) -> OnboardingResponse:
        """
        Create new onboarding record with business rule validation.
        
        This method implements critical business logic:
        1. Prevents duplicate onboarding per user
        2. Enforces domain uniqueness across all tenants
        3. Associates onboarding with authenticated user
        4. Manages database transactions for consistency
        
        Args:
            db: Database session for transaction management
            user_id: Authenticated user ID from JWT token
            onboarding_data: Validated onboarding form data
            
        Returns:
            OnboardingResponse with success confirmation and metadata
            
        Raises:
            ValueError: For business rule violations (duplicate onboarding, domain conflicts)
            IntegrityError: For database constraint violations
        """
        
        # Check if user already has onboarding record
        # Prevents duplicate onboarding submissions per user
        existing_onboarding = await db.execute(
            select(Onboarding).where(Onboarding.user_id == user_id)
        )
        if existing_onboarding.scalar_one_or_none():
            raise ValueError("User has already completed onboarding")
        
        # Check domain uniqueness across all tenants
        # Critical for multi-tenant architecture - prevents subdomain conflicts
        existing_domain = await db.execute(
            select(Onboarding).where(
                Onboarding.company_domain == onboarding_data.company_domain
            )
        )
        if existing_domain.scalar_one_or_none():
            raise ValueError(f"Company domain '{onboarding_data.company_domain}' is already taken")
        
        try:
            # Create onboarding record with user association
            # All fields are required and validated by Pydantic schema
            onboarding = Onboarding(
                user_id=user_id,
                company_name=onboarding_data.company_name,
                company_domain=onboarding_data.company_domain,
                company_size=onboarding_data.company_size,
                company_industry=onboarding_data.company_industry,
                company_roles=onboarding_data.company_roles,
                your_needs=onboarding_data.your_needs,
                onboarding_completed=True,  # Mark as completed upon creation
                workspace_created=False,    # Workspace creation is separate process
            )
            
            # Add to session and commit transaction
            # Database handles constraint validation and rollback on error
            db.add(onboarding)
            await db.commit()
            await db.refresh(onboarding)  # Get updated fields (id, timestamps)
            
            # Return success response with confirmation data
            return OnboardingResponse(
                success=True,
                message="Onboarding completed successfully! Your workspace is being set up.",
                onboarding_id=onboarding.id,
                workspace_created=onboarding.workspace_created,
                company_domain=onboarding.company_domain,
                full_domain=onboarding.full_domain
            )
            
        except IntegrityError as e:
            # Handle database constraint violations
            # Rollback transaction to maintain consistency
            await db.rollback()
            
            # Parse specific constraint violations for user-friendly messages
            error_msg = str(e.orig).lower()
            if 'unique constraint' in error_msg and 'company_domain' in error_msg:
                raise ValueError(f"Company domain '{onboarding_data.company_domain}' is already taken")
            elif 'unique constraint' in error_msg and 'user_id' in error_msg:
                raise ValueError("User has already completed onboarding")
            else:
                # Generic constraint violation
                raise ValueError("Onboarding data violates system constraints")
    
    @staticmethod
    async def get_user_onboarding(
        db: AsyncSession, 
        user_id: int
    ) -> Optional[OnboardingDetail]:
        """
        Retrieve onboarding record for authenticated user.
        
        Args:
            db: Database session
            user_id: Authenticated user ID
            
        Returns:
            OnboardingDetail if exists, None otherwise
        """
        
        # Query onboarding record with user association
        result = await db.execute(
            select(Onboarding).where(Onboarding.user_id == user_id)
        )
        onboarding = result.scalar_one_or_none()
        
        if not onboarding:
            return None
        
        # Convert to response schema with computed fields
        return OnboardingDetail(
            onboarding_id=onboarding.id,
            user_id=onboarding.user_id,
            company_name=onboarding.company_name,
            company_domain=onboarding.company_domain,
            company_size=onboarding.company_size,
            company_industry=onboarding.company_industry,
            company_roles=onboarding.company_roles,
            your_needs=onboarding.your_needs,
            onboarding_completed=onboarding.onboarding_completed,
            workspace_created=onboarding.workspace_created,
            full_domain=onboarding.full_domain,
            created_at=onboarding.created_at,
            updated_at=onboarding.updated_at
        )
    
    @staticmethod
    async def get_onboarding_status(
        db: AsyncSession, 
        user_id: int
    ) -> OnboardingStatus:
        """
        Get lightweight onboarding status for quick checks.
        
        Used by frontend to determine user flow without full data transfer.
        Optimized for performance with minimal database queries.
        
        Args:
            db: Database session
            user_id: Authenticated user ID
            
        Returns:
            OnboardingStatus with completion flags
        """
        
        # Lightweight query for status only
        result = await db.execute(
            select(
                Onboarding.onboarding_completed,
                Onboarding.workspace_created,
                Onboarding.company_domain
            ).where(Onboarding.user_id == user_id)
        )
        onboarding_data = result.first()
        
        if not onboarding_data:
            # User has no onboarding record
            return OnboardingStatus(
                has_onboarding=False,
                onboarding_completed=False,
                workspace_created=False,
                company_domain=None
            )
        
        # User has onboarding record
        return OnboardingStatus(
            has_onboarding=True,
            onboarding_completed=onboarding_data.onboarding_completed,
            workspace_created=onboarding_data.workspace_created,
            company_domain=onboarding_data.company_domain
        )
    
    @staticmethod
    async def check_domain_availability(
        db: AsyncSession, 
        domain: str
    ) -> bool:
        """
        Check if company domain is available for registration.
        
        Utility method for real-time domain validation during form input.
        Can be used by frontend for immediate feedback.
        
        Args:
            db: Database session
            domain: Proposed company domain
            
        Returns:
            True if domain is available, False if taken
        """
        
        # Normalize domain for consistent checking
        domain = domain.lower().strip()
        
        # Query existing domains
        result = await db.execute(
            select(Onboarding.id).where(Onboarding.company_domain == domain)
        )
        existing = result.scalar_one_or_none()
        
        return existing is None
