"""
Authentication API endpoints.

This module provides endpoints for user authentication including
login, registration, and token management with comprehensive error handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from services.auth_service import AuthService


# Create router with authentication-specific configuration
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Authentication failed"},
        422: {"description": "Validation error"},
    }
)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticate user with email and password, returns JWT access token"
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and return JWT access token.
    
    This endpoint:
    1. Validates email and password format
    2. Checks user credentials against database
    3. Verifies account is active
    4. Returns JWT token for API access
    
    Args:
        login_data: User login credentials
        db: Database session dependency
        
    Returns:
        TokenResponse: JWT access token and metadata
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    token_response = await AuthService.login(db, login_data)
    
    if token_response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_response


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Create new user account and return JWT access token"
)
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Register new user account and return JWT access token.
    
    This endpoint:
    1. Validates registration data format
    2. Checks email is not already registered
    3. Creates new user account with hashed password
    4. Returns JWT token for immediate login
    
    Args:
        register_data: User registration data
        db: Database session dependency
        
    Returns:
        TokenResponse: JWT access token and metadata
        
    Raises:
        HTTPException: 400 if email already exists or validation fails
    """
    try:
        token_response = await AuthService.register(db, register_data)
        return token_response
        
    except ValueError as e:
        # Handle business logic errors (e.g., email already exists)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )
