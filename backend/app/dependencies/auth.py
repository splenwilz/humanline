from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.supabase_auth_service import supabase_auth_service
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from Supabase token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Dict: Current user data from Supabase token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    # Validate the Supabase access token
    user_data = supabase_auth_service.validate_token(token)
    if not user_data:
        logger.warning("Authentication failed: Invalid or expired Supabase access token.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data


async def get_current_user_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Dependency to get current user ID from Supabase token
    
    Args:
        current_user: Current user data from token
        
    Returns:
        str: Current user ID
    """
    return current_user["user_id"]


async def get_current_user_email(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    Dependency to get current user email from Supabase token
    
    Args:
        current_user: Current user data from token
        
    Returns:
        str: Current user email
    """
    return current_user["email"]


# Optional authentication (doesn't raise error if no token)
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Optional dependency to get current user (returns None if no token)
    
    Args:
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        Optional[Dict]: Current user data or None
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return supabase_auth_service.validate_token(token)
