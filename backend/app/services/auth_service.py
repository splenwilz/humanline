from supabase import create_client, Client
from app.config import settings
from app.models.user import (
    UserSignupRequest, UserSignupResponse, 
    UserSigninRequest, UserSigninResponse, UserProfile
)
from typing import Dict, Any, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def _convert_datetime_to_iso(value: Union[str, datetime, None]) -> Union[str, None]:
    """Convert datetime objects to ISO string format."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


class AuthService:
    """Authentication service using Supabase."""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
    
    async def signup_user(self, user_data: UserSignupRequest) -> UserSignupResponse:
        """
        Sign up a new user with Supabase Auth.
        
        Args:
            user_data: User signup information
            
        Returns:
            UserSignupResponse with user details
            
        Raises:
            Exception: If signup fails
        """
        try:
            # Prepare signup data
            signup_data = {
                "email": user_data.email,
                "password": user_data.password,
            }
            
            # Add user metadata if full_name is provided
            if user_data.full_name:
                signup_data["options"] = {
                    "data": {
                        "full_name": user_data.full_name
                    }
                }
            
            # Sign up user with Supabase
            response = self.supabase.auth.sign_up(signup_data)
            
            if response.user is None:
                raise Exception("Failed to create user")
            
            # Supabase will automatically send OTP email
            logger.info(f"User created successfully for {user_data.email}")
            logger.info("Supabase will send OTP email automatically")
            
            return UserSignupResponse(
                user_id=response.user.id,
                email=response.user.email,
                message="User created successfully. Check your email for the OTP code to confirm your account.",
                confirmation_sent=False,  # No email confirmation link sent
                otp_sent=True  # Supabase sends OTP automatically
            )
            
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            raise Exception(f"Signup failed: {str(e)}")

    async def signin_user(self, user_data: UserSigninRequest) -> UserSigninResponse:
        """
        Sign in an existing user with Supabase Auth.
        
        Args:
            user_data: User signin information
            
        Returns:
            UserSigninResponse with tokens and user info
            
        Raises:
            Exception: If signin fails
        """
        try:
            # Sign in with Supabase
            response = self.supabase.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if response.user is None or response.session is None:
                raise Exception("Invalid credentials")
            
            # Check if email is confirmed
            if not response.user.email_confirmed_at:
                raise Exception("Please confirm your email with the OTP code before signing in")
            
            # Create user profile
            user_profile = UserProfile(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name"),
                email_confirmed_at=_convert_datetime_to_iso(response.user.email_confirmed_at),
                created_at=_convert_datetime_to_iso(response.user.created_at)
            )
            
            return UserSigninResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",
                expires_in=response.session.expires_in,
                user=user_profile
            )
            
        except Exception as e:
            logger.error(f"Signin error for {user_data.email}: {str(e)}")
            raise Exception(f"Signin failed: {str(e)}")

    async def refresh_token(self, refresh_token: str) -> UserSigninResponse:
        """
        Refresh access token using JWT refresh token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            UserSigninResponse with new tokens
            
        Raises:
            Exception: If refresh fails
        """
        try:
            # Import JWT service
            from app.services.jwt_service import jwt_service
            
            # Use JWT service to refresh the token
            refresh_response = jwt_service.refresh_access_token(refresh_token)
            
            if not refresh_response:
                raise Exception("Invalid or expired refresh token")
            
            # Get user info from the refresh token
            from app.models.token import TokenData
            token_data = jwt_service.decode_token(refresh_token)
            
            if not token_data:
                raise Exception("Invalid refresh token")
            
            # Create user profile (simplified since we don't have full user data)
            user_profile = UserProfile(
                id=token_data.user_id,
                email=token_data.email,
                full_name=None,
                email_confirmed_at=None,
                created_at=None
            )
            
            return UserSigninResponse(
                access_token=refresh_response.access_token,
                refresh_token=refresh_token,  # Keep the same refresh token
                token_type="bearer",
                expires_in=refresh_response.expires_in,
                user=user_profile
            )
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise Exception(f"Token refresh failed: {str(e)}")


# Global auth service instance
auth_service = AuthService()
