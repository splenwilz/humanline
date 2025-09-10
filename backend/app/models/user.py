from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Union
from datetime import datetime


class UserSignupRequest(BaseModel):
    """User signup request model."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password (min 6 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")


class UserSignupResponse(BaseModel):
    """User signup response model."""
    user_id: str = Field(..., description="Supabase user ID")
    email: str = Field(..., description="User's email address")
    message: str = Field(..., description="Success message")
    confirmation_sent: bool = Field(..., description="Whether confirmation email was sent")
    otp_sent: bool = Field(..., description="Whether OTP was sent to email")


class UserSigninRequest(BaseModel):
    """User signin request model."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")


class UserSigninResponse(BaseModel):
    """User signin response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserProfile" = Field(..., description="User profile information")


class UserProfile(BaseModel):
    """User profile model."""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="User's full name")
    email_confirmed_at: Optional[str] = Field(None, description="Email confirmation timestamp")
    created_at: str = Field(..., description="Account creation timestamp")


class EmailConfirmationResponse(BaseModel):
    """Email confirmation response model."""
    message: str = Field(..., description="Confirmation result message")
    confirmed: bool = Field(..., description="Whether email was confirmed")


class OTPVerificationRequest(BaseModel):
    """OTP verification request model."""
    email: EmailStr = Field(..., description="User's email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class OTPVerificationResponse(BaseModel):
    """OTP verification response model."""
    message: str = Field(..., description="Verification result message")
    verified: bool = Field(..., description="Whether OTP was verified")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserProfile = Field(..., description="User profile information")


class ResendOTPRequest(BaseModel):
    """Resend OTP request model."""
    email: EmailStr = Field(..., description="User's email address")


class ResendOTPResponse(BaseModel):
    """Resend OTP response model."""
    message: str = Field(..., description="OTP resend result message")
    otp_sent: bool = Field(..., description="Whether OTP was sent")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
