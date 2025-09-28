"""
FastAPI dependencies for authentication and authorization.

This module provides dependency functions that can be injected into
FastAPI endpoints to handle authentication and user context.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import verify_token
from models.user import User
from services.user_service import UserService


# HTTP Bearer token security scheme
# This creates the "Authorize" button in FastAPI docs
security = HTTPBearer(
    scheme_name="JWT",
    description="Enter JWT token (without 'Bearer' prefix)"
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    This dependency:
    1. Extracts JWT token from Authorization header
    2. Verifies token signature and expiration
    3. Loads user from database
    4. Validates user is active
    
    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found/inactive
    """
    # Verify JWT token
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from token
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Load user from database
    user = await UserService.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user.
    
    This is an alias for get_current_user since we already check
    for active status there. Kept for semantic clarity.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        User: Current active user
    """
    return current_user


def get_optional_current_user():
    """
    Dependency factory for optional authentication.
    
    Returns a dependency that provides the current user if authenticated,
    or None if no valid token is provided. Useful for endpoints that
    work differently for authenticated vs anonymous users.
    
    Returns:
        Callable: Dependency function that returns Optional[User]
    """
    async def _get_optional_current_user(
        db: AsyncSession = Depends(get_db),
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer(auto_error=False)
        )
    ) -> Optional[User]:
        if credentials is None:
            return None
        
        # Verify token
        payload = verify_token(credentials.credentials)
        if payload is None:
            return None
        
        # Extract user ID
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            return None
        
        # Load user
        user = await UserService.get_user_by_id(db, user_id)
        if user is None or not user.is_active:
            return None
        
        return user
    
    return _get_optional_current_user
