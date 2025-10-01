"""
Authentication API endpoints.

This module provides endpoints for user authentication including
login, registration, and token management with comprehensive error handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, EmailConfirmationRequest, ResendConfirmationRequest
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
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Create new user account - returns JWT token or email confirmation message"
)
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user account with flexible response based on email confirmation setting.
    
    This endpoint behavior depends on the REQUIRE_EMAIL_CONFIRMATION setting:
    
    If email confirmation is DISABLED:
    1. Validates registration data format
    2. Checks email is not already registered  
    3. Creates active user account with hashed password
    4. Returns JWT token for immediate login
    
    If email confirmation is ENABLED:
    1. Validates registration data format
    2. Checks email is not already registered
    3. Creates inactive user account with verification token
    4. Sends confirmation email to user
    5. Returns confirmation message (no JWT token)
    
    Args:
        register_data: User registration data
        db: Database session dependency
        
    Returns:
        Either TokenResponse (immediate login) or confirmation message
        
    Raises:
        HTTPException: 400 if email already exists or validation fails
    """
    try:
        # Call the updated register method that handles both flows
        # The response format depends on the email confirmation setting
        result = await AuthService.register(db, register_data)
        
        # Handle different response types based on confirmation requirement
        if result["type"] == "immediate_login":
            # Email confirmation disabled - return JWT token for immediate login
            # This maintains backward compatibility with existing clients
            return result["token_response"]
        elif result["type"] == "email_confirmation_required":
            # Email confirmation enabled - return confirmation message
            # Client should redirect user to check email
            return {
                "message": result["message"],
                "email": result["email"],
                "email_sent": result["email_sent"],
                "expires_in_hours": result["expires_in_hours"],
                "next_step": "check_email_for_confirmation_link"
            }
        else:
            # Unexpected response type - should not happen
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected registration response type"
            )
        
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


@router.post(
    "/confirm-email",
    summary="Email Confirmation", 
    description="Confirm user email address using 6-digit verification code"
)
async def confirm_email(
    request: EmailConfirmationRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Confirm user email address and activate account.

    This endpoint:
    1. Validates the 6-digit verification code
    2. Checks code hasn't expired
    3. Activates the user account
    4. Marks email as verified
    5. Clears the verification code

    Args:
        request: Email confirmation request containing the 6-digit code
        db: Database session dependency

    Returns:
        dict: Success message and user status

    Raises:
        HTTPException: 400 if code is invalid/expired, 404 if user not found
    """
    try:
        # Attempt to confirm the email using the provided code from request body
        # This handles all validation and database updates
        result = await AuthService.confirm_email(db, request.code)
        
        if result["success"]:
            return {
                "message": result["message"],
                "user_email": result["user_email"],
                "confirmed_at": result["confirmed_at"]
            }
        else:
            # Code validation failed - return appropriate error with proper status code
            # Use 400 for client errors (invalid/expired codes)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions (don't catch our own exceptions)
        raise
    except Exception as e:
        # Handle unexpected database or system errors
        # Log the actual error for debugging but don't expose internal details
        print(f"Email confirmation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email confirmation failed due to a server error. Please try again."
        )


@router.post(
    "/resend-confirmation",
    summary="Resend Email Confirmation",
    description="Resend 6-digit verification code to unverified email address"
)
async def resend_confirmation(
    request: ResendConfirmationRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Resend email confirmation code to an unverified user.

    This endpoint:
    1. Validates the email address exists and is unverified
    2. Implements rate limiting to prevent abuse (1 minute cooldown)
    3. Generates a new unique 6-digit verification code
    4. Updates the user's verification code and expiration
    5. Sends a new confirmation email

    Args:
        request: Resend confirmation request containing email address
        db: Database session dependency

    Returns:
        dict: Success message and email details

    Raises:
        HTTPException: 400 if user not found/verified/rate limited, 500 for server errors
    """
    try:
        # Attempt to resend confirmation email using the provided email address
        # This handles all validation, rate limiting, and email sending
        result = await AuthService.resend_confirmation(db, request.email)
        
        if result["success"]:
            return {
                "message": result["message"],
                "email": result["email"],
                "expires_in_hours": result["expires_in_hours"]
            }
        else:
            # Resend failed - return appropriate error with proper status code
            # Use 400 for client errors (user not found, already verified, rate limited)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions (don't catch our own exceptions)
        raise
    except Exception as e:
        # Handle unexpected database or system errors
        # Log the actual error for debugging but don't expose internal details
        print(f"Resend confirmation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend confirmation email due to a server error. Please try again."
        )
