import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings
from app.models.token import TokenData, TokenResponse, RefreshTokenResponse
import logging

logger = logging.getLogger(__name__)


class JWTService:
    """Service for JWT token management"""
    
    def __init__(self):
        # JWT secret key (should be in environment variables)
        self.secret_key = getattr(settings, 'jwt_secret_key', 'your-secret-key-change-this')
        self.algorithm = "HS256"
        
        # Token expiration times
        self.access_token_expire_minutes = 60  # 60 minutes (1 hour)
        self.refresh_token_expire_days = 7     # 7 days
    
    def create_access_token(self, user_id: str, email: str) -> str:
        """
        Create a JWT access token
        
        Args:
            user_id: User ID
            email: User email
            
        Returns:
            str: JWT access token
        """
        try:
            now = datetime.utcnow()
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
            
            payload = {
                "user_id": user_id,
                "email": email,
                "exp": expire,
                "iat": now,
                "type": "access"
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created access token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise
    
    def create_refresh_token(self, user_id: str, email: str) -> str:
        """
        Create a JWT refresh token
        
        Args:
            user_id: User ID
            email: User email
            
        Returns:
            str: JWT refresh token
        """
        try:
            now = datetime.utcnow()
            expire = now + timedelta(days=self.refresh_token_expire_days)
            
            payload = {
                "user_id": user_id,
                "email": email,
                "exp": expire,
                "iat": now,
                "type": "refresh"
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created refresh token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}")
            raise
    
    def create_token_pair(self, user_id: str, email: str) -> TokenResponse:
        """
        Create both access and refresh tokens
        
        Args:
            user_id: User ID
            email: User email
            
        Returns:
            TokenResponse: Token pair with expiration info
        """
        try:
            access_token = self.create_access_token(user_id, email)
            refresh_token = self.create_refresh_token(user_id, email)
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=self.access_token_expire_minutes * 60  # Convert to seconds
            )
            
        except Exception as e:
            logger.error(f"Error creating token pair: {str(e)}")
            raise
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenData]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token to verify
            token_type: Expected token type ("access" or "refresh")
            
        Returns:
            TokenData: Decoded token data if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                logger.warning(f"Invalid token type. Expected: {token_type}, Got: {payload.get('type')}")
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                logger.warning("Token has expired")
                return None
            
            return TokenData(
                user_id=payload.get("user_id"),
                email=payload.get("email"),
                exp=payload.get("exp"),
                iat=payload.get("iat")
            )
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[RefreshTokenResponse]:
        """
        Create a new access token from a refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            RefreshTokenResponse: New access token if refresh token is valid
        """
        try:
            # Verify refresh token
            token_data = self.verify_token(refresh_token, "refresh")
            if not token_data:
                return None
            
            # Create new access token
            new_access_token = self.create_access_token(
                token_data.user_id, 
                token_data.email
            )
            
            return RefreshTokenResponse(
                access_token=new_access_token,
                token_type="bearer",
                expires_in=self.access_token_expire_minutes * 60
            )
            
        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            return None


# Create service instance
jwt_service = JWTService()
