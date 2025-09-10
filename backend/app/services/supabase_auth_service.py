"""
Supabase authentication service for validating Supabase tokens.
"""

import logging
from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """Service for validating Supabase authentication tokens."""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key or settings.supabase_anon_key
        )
    
    def validate_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a Supabase access token and return user information.
        
        Args:
            access_token: Supabase access token
            
        Returns:
            Optional[Dict]: User data if token is valid, None otherwise
        """
        try:
            # Use Supabase's built-in token validation
            response = self.supabase.auth.get_user(access_token)
            
            if response.user:
                logger.info(f"Token validated for user: {response.user.email}")
                return {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "full_name": response.user.user_metadata.get("full_name"),
                    "email_confirmed_at": response.user.email_confirmed_at,
                    "created_at": response.user.created_at
                }
            else:
                logger.warning("Token validation failed: No user found")
                return None
                
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh a Supabase refresh token and return new tokens.
        
        Args:
            refresh_token: Supabase refresh token
            
        Returns:
            Optional[Dict]: New tokens and user data if refresh is successful
        """
        try:
            # Use Supabase's built-in token refresh
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.user and response.session:
                logger.info(f"Token refreshed for user: {response.user.email}")
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_in": response.session.expires_in,
                    "token_type": "bearer",
                    "user": {
                        "user_id": response.user.id,
                        "email": response.user.email,
                        "full_name": response.user.user_metadata.get("full_name"),
                        "email_confirmed_at": response.user.email_confirmed_at,
                        "created_at": response.user.created_at
                    }
                }
            else:
                logger.warning("Token refresh failed: No user or session found")
                return None
                
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None


# Global Supabase auth service instance
supabase_auth_service = SupabaseAuthService()
