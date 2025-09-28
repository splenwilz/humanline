"""
User management API endpoints.

This module provides endpoints for user profile management and
user-related operations with proper authentication and authorization.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.dependencies import get_current_active_user
from models.user import User
from schemas.user import UserResponse, UserUpdate
from services.user_service import UserService


# Create router with user-specific configuration
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        401: {"description": "Authentication required"},
        404: {"description": "User not found"},
    }
)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get current authenticated user's profile information"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get current authenticated user's profile.
    
    This endpoint returns the profile information of the currently
    authenticated user based on the JWT token provided.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        UserResponse: User profile data
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update Current User",
    description="Update current authenticated user's profile information"
)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update current authenticated user's profile.
    
    This endpoint allows users to update their own profile information.
    Only the fields provided in the request will be updated.
    
    Args:
        user_update: Updated user data
        current_user: Current authenticated user from JWT token
        db: Database session dependency
        
    Returns:
        UserResponse: Updated user profile data
        
    Raises:
        HTTPException: 500 if update fails
    """
    try:
        updated_user = await UserService.update_user(
            db, current_user.id, user_update
        )
        
        if updated_user is None:
            # This shouldn't happen since we have the user from auth
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
        
        return UserResponse.model_validate(updated_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User by ID",
    description="Get user profile by user ID (admin or public profile view)"
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get user profile by ID.
    
    This endpoint allows authenticated users to view other users' profiles.
    In a production system, you might want to add privacy controls here.
    
    Args:
        user_id: ID of user to retrieve
        db: Database session dependency
        current_user: Current authenticated user (for authorization)
        
    Returns:
        UserResponse: User profile data
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = await UserService.get_user_by_id(db, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)
