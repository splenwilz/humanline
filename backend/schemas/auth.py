"""
Authentication-related Pydantic schemas.

These schemas handle authentication requests and responses,
ensuring proper validation of login credentials and token data.
"""

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
