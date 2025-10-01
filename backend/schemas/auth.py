"""
Authentication-related Pydantic schemas.

These schemas handle authentication requests and responses,
ensuring proper validation of login credentials and token data.
"""

from typing import Union
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for user login requests."""
    
    email: EmailStr = Field(
        description="User's email address",
        example="user@example.com"
    )
    password: str = Field(
        min_length=1,  # Allow any length for login (validation happens server-side)
        description="User's password",
        example="securepassword123"
    )


class RegisterRequest(BaseModel):
    """Schema for user registration requests."""
    
    email: EmailStr = Field(
        description="User's email address",
        example="user@example.com"
    )
    password: str = Field(
        min_length=8,
        max_length=128,  # Reasonable maximum for security
        description="User's password (8-128 characters)",
        example="securepassword123"
    )
    first_name: str = Field(
        min_length=1,
        max_length=100,
        description="User's first name",
        example="John"
    )
    last_name: str = Field(
        min_length=1,
        max_length=100,
        description="User's last name",
        example="Doe"
    )


class TokenResponse(BaseModel):
    """Schema for authentication token responses."""
    
    access_token: str = Field(
        description="JWT access token for API authentication"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer' for JWT)"
    )
    expires_in: int = Field(
        description="Token expiration time in seconds"
    )


class TokenData(BaseModel):
    """Schema for token payload data."""
    
    user_id: int = Field(description="User ID from token")
    email: str = Field(description="User email from token")


class EmailConfirmationRequest(BaseModel):
    """Schema for email confirmation requests."""
    
    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r'^\d{6}$',
        description="6-digit verification code from confirmation email",
        example="123456"
    )


class ResendConfirmationRequest(BaseModel):
    """Schema for resend confirmation email requests."""
    
    email: EmailStr = Field(
        description="Email address to resend confirmation code to",
        example="user@example.com"
    )


class EmailConfirmationResponse(BaseModel):
    """Schema for email confirmation required response."""
    
    message: str = Field(
        description="Success message about email confirmation",
        example="Registration successful! Please check your email for a confirmation link."
    )
    email: str = Field(
        description="Email address where confirmation was sent",
        example="user@example.com"
    )
    email_sent: bool = Field(
        description="Whether the confirmation email was successfully sent",
        example=True
    )
    expires_in_hours: int = Field(
        description="Hours until the confirmation code expires",
        example=24
    )
    next_step: str = Field(
        description="Next step for the user",
        example="check_email_for_confirmation_link"
    )


# Union type for registration responses
RegisterResponse = Union[TokenResponse, EmailConfirmationResponse]
