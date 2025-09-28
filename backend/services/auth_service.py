"""
Authentication service for login, registration, and token management.

This service handles authentication business logic, including password
verification, token creation, and user registration with security checks.
"""

from datetime import timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from schemas.user import UserCreate
from core.security import verify_password, create_access_token
from core.config import settings
from services.user_service import UserService


class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            email: User's email address
            password: Plain text password
            
        Returns:
            User model if authentication successful, None otherwise
        """
        # Get user by email
        user = await UserService.get_user_by_email(db, email)
        if not user:
            return None
        
        # Check if account is active
        if not user.is_active:
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    async def login(db: AsyncSession, login_data: LoginRequest) -> Optional[TokenResponse]:
        """
        Handle user login and return JWT token.
        
        Args:
            db: Database session
            login_data: Login credentials
            
        Returns:
            TokenResponse with JWT token if successful, None otherwise
        """
        # Authenticate user
        user = await AuthService.authenticate_user(
            db, login_data.email, login_data.password
        )
        if not user:
            return None
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60  # Convert to seconds
        )
    
    @staticmethod
    async def register(db: AsyncSession, register_data: RegisterRequest) -> TokenResponse:
        """
        Handle user registration and return JWT token.
        
        Args:
            db: Database session
            register_data: Registration data
            
        Returns:
            TokenResponse with JWT token
            
        Raises:
            ValueError: If email already exists or validation fails
        """
        # Create user data object
        user_data = UserCreate(
            email=register_data.email,
            password=register_data.password,
            first_name=register_data.first_name,
            last_name=register_data.last_name
        )
        
        # Create user account
        user = await UserService.create_user(db, user_data)
        
        # Create access token for immediate login
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60  # Convert to seconds
        )
