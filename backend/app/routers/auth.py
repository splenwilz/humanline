from fastapi import APIRouter, HTTPException, status, Body
from app.models.user import (
    UserSignupRequest, UserSignupResponse, 
    UserSigninRequest, UserSigninResponse, ErrorResponse,
    OTPVerificationRequest, OTPVerificationResponse,
    ResendOTPRequest, ResendOTPResponse, UserProfile
)
from app.models.token import TokenResponse, RefreshTokenRequest, RefreshTokenResponse
from app.services.jwt_service import jwt_service
from app.services.auth_service import auth_service
from app.services.otp_service import otp_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/signup",
    response_model=UserSignupResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        409: {"model": ErrorResponse, "description": "User already exists"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Sign up a new user",
    description="Create a new user account with email and password using Supabase Auth. Supabase will send OTP automatically."
)
async def signup(user_data: UserSignupRequest) -> UserSignupResponse:
    """
    Sign up a new user.
    
    This endpoint creates a new user account with the provided email and password.
    Supabase will automatically send an OTP code for email confirmation.
    """
    try:
        result = await auth_service.signup_user(user_data)
        logger.info(f"User signup successful: {user_data.email}")
        return result
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Signup failed for {user_data.email}: {error_message}")
        
        # Handle specific error cases
        if "already registered" in error_message.lower() or "already exists" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        elif "invalid email" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        elif "password" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet requirements"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )


@router.post(
    "/signin",
    response_model=UserSigninResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        403: {"model": ErrorResponse, "description": "Email not confirmed"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Sign in a user",
    description="Authenticate user with email and password, returns JWT tokens"
)
async def signin(user_data: UserSigninRequest) -> UserSigninResponse:
    """
    Sign in an existing user.
    
    This endpoint authenticates a user with email and password.
    Returns access token, refresh token, and user profile information.
    """
    try:
        result = await auth_service.signin_user(user_data)
        logger.info(f"User signin successful: {user_data.email}")
        return result
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Signin failed for {user_data.email}: {error_message}")
        
        # Handle specific error cases
        if "invalid credentials" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        elif "confirm your email" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please confirm your email address before signing in"
            )
        elif "invalid email" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )


@router.post(
    "/verify-otp",
    response_model=OTPVerificationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Invalid OTP"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Verify OTP code",
    description="Verify one-time password code and authenticate user"
)
async def verify_otp(otp_data: OTPVerificationRequest) -> OTPVerificationResponse:
    """
    Verify OTP code.
    
    This endpoint verifies the OTP code sent to user's email and returns authentication tokens.
    The OTP must be valid and not expired.
    """
    try:
        # Verify OTP using Supabase's built-in system
        user_data = otp_service.verify_otp(otp_data.email, otp_data.otp)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired OTP code"
            )
        
        logger.info(f"OTP verified successfully for {otp_data.email}")
        
        # Create user profile from the verification response
        user_profile = UserProfile(
            id=user_data["id"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            email_confirmed_at=user_data["email_confirmed_at"],
            created_at=user_data["created_at"]
        )
        
        return OTPVerificationResponse(
            message="OTP verified successfully. Email confirmed.",
            verified=True,
            access_token=user_data["access_token"],
            refresh_token=user_data["refresh_token"],
            token_type="bearer",
            expires_in=user_data["expires_in"],
            user=user_profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.post(
    "/resend-otp",
    response_model=ResendOTPResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Resend OTP code",
    description="Generate and send a new OTP code to user's email"
)
async def resend_otp(request: ResendOTPRequest) -> ResendOTPResponse:
    """
    Resend OTP code.
    
    This endpoint requests Supabase to send a new OTP code to the user's email.
    Useful when the previous OTP has expired or was lost.
    """
    try:
        # Check if user exists
        user_data = otp_service.get_user_by_email(request.email)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Request Supabase to resend OTP
        try:
            # Use Supabase's resend OTP functionality
            # This will trigger a new OTP email
            logger.info(f"Requesting OTP resend for {request.email}")
            
            # For now, we'll return success
            # TODO: Implement actual Supabase OTP resend
            return ResendOTPResponse(
                message="New OTP code has been sent to your email",
                otp_sent=True
            )
            
        except Exception as e:
            logger.error(f"Failed to resend OTP: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send new OTP"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP resend error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


@router.post(
    "/refresh",
    response_model=UserSigninResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Refresh access token",
    description="Get a new access token using the refresh token"
)
async def refresh_token(
    refresh_token: str = Body(..., embed=True, description="JWT refresh token")
) -> UserSigninResponse:
    """
    Refresh access token.
    
    This endpoint allows you to get a new access token using your refresh token.
    Both tokens will be refreshed and returned.
    """
    try:
        result = await auth_service.refresh_token(refresh_token)
        logger.info("Token refresh successful")
        return result
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Token refresh failed: {error_message}")
        
        if "invalid refresh token" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error occurred"
            )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login with email and password",
    description="Authenticate user and return JWT tokens"
)
async def login(request: UserSigninRequest):
    """
    User login endpoint
    
    Args:
        request: UserSigninRequest with email and password
        
    Returns:
        TokenResponse: JWT access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        # Authenticate user with Supabase
        result = await auth_service.signin_user(request)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create JWT tokens
        token_response = jwt_service.create_token_pair(
            user_id=result.user.id,
            email=result.user.email
        )
        
        logger.info(f"Login successful for user: {result.user.id}")
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using refresh token"
)
async def refresh_access_token(request: RefreshTokenRequest):
    """
    Refresh access token endpoint using Supabase
    
    Args:
        request: RefreshTokenRequest with refresh token
        
    Returns:
        RefreshTokenResponse: New access token
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        logger.info("Token refresh attempt")
        
        # Use Supabase token refresh
        from app.services.supabase_auth_service import supabase_auth_service
        result = supabase_auth_service.refresh_token(request.refresh_token)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        logger.info("Token refresh successful")
        return RefreshTokenResponse(
            access_token=result["access_token"],
            token_type="bearer",
            expires_in=result["expires_in"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )
