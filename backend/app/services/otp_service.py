import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Union
import logging
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)


def _convert_datetime_to_iso(value: Union[str, datetime, None]) -> Union[str, None]:
    """Convert datetime objects to ISO string format."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


class OTPService:
    """Service for handling OTP (One-Time Password) operations using Supabase's built-in system."""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key or settings.supabase_anon_key
        )
    
    def verify_otp(self, email: str, otp: str) -> Optional[Dict]:
        """
        Verify OTP code using Supabase's built-in OTP verification.
        
        Args:
            email: User's email address
            otp: OTP code to verify (from Supabase email)
            
        Returns:
            Optional[Dict]: User data if OTP is valid, None otherwise
        """
        try:
            # Use Supabase's verify_otp method
            response = self.supabase.auth.verify_otp({
                "email": email,
                "token": otp,
                "type": "signup"
            })
            
            if response.user and response.session:
                logger.info(f"OTP verified successfully for {email}")
                
                # Return user data directly from the verification response
                # Convert datetime objects to ISO strings for Pydantic compatibility
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "full_name": response.user.user_metadata.get("full_name"),
                    "email_confirmed_at": _convert_datetime_to_iso(response.user.email_confirmed_at),
                    "created_at": _convert_datetime_to_iso(response.user.created_at),
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_in": response.session.expires_in
                }
            else:
                logger.warning(f"OTP verification failed for {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error verifying OTP for {email}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user information by email from Supabase.
        
        Args:
            email: User's email address
            
        Returns:
            Optional[Dict]: User data if found
        """
        try:
            # Try to get user info using the service role
            # If this fails, we'll fall back to other methods
            result = self.supabase.auth.admin.list_users()
            
            for user in result.users:
                if user.email == email:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.user_metadata.get("full_name"),
                        "email_confirmed_at": _convert_datetime_to_iso(user.email_confirmed_at),
                        "created_at": _convert_datetime_to_iso(user.created_at)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            # If admin API fails, return None and let the calling code handle it
            return None


# Global OTP service instance
otp_service = OTPService()
