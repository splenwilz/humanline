"""
User-related Pydantic schemas for API serialization and validation.

These schemas define the structure for user data in API requests and responses,
providing automatic validation and documentation generation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(
        description="User's email address",
        example="user@example.com"
    )
    first_name: Optional[str] = Field(
        None,
        max_length=100,
        description="User's first name",
        example="John"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=100,
        description="User's last name", 
        example="Doe"
    )


class UserCreate(UserBase):
    """Schema for user creation requests."""
    
    password: str = Field(
        min_length=8,
        max_length=128,  # Reasonable maximum for security
        description="User's password (8-128 characters)",
        example="securepassword123"
    )
    
    @validator('first_name', 'last_name')
    def validate_name_fields(cls, v):
        """Validate name fields to prevent XSS and injection attacks."""
        if v is None:
            return v
            
        # Remove potentially dangerous characters that could be used for XSS
        dangerous_patterns = ['<script', '</script', 'javascript:', 'data:', 'vbscript:', 'onload=', 'onerror=', 'onclick=']
        v_lower = v.lower()
        
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError("Name contains invalid characters. Please use only letters, numbers, spaces, and basic punctuation.")
        
        # Check for HTML tags in general
        if '<' in v and '>' in v:
            raise ValueError("HTML tags are not allowed in names.")
            
        # Additional length check for security (beyond Field max_length)
        if len(v) > 50:
            raise ValueError("Name is too long. Please use 50 characters or less.")
            
        return v.strip()


class UserUpdate(BaseModel):
    """Schema for user update requests."""
    
    first_name: Optional[str] = Field(
        None,
        max_length=100,
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=100,
        description="User's last name"
    )


class UserResponse(UserBase):
    """Schema for user data in API responses."""
    
    id: int = Field(description="User's unique identifier")
    is_active: bool = Field(description="Whether the user account is active")
    is_verified: bool = Field(description="Whether the user's email is verified")
    created_at: datetime = Field(description="Account creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    
    # Configuration for Pydantic v2
    model_config = ConfigDict(
        from_attributes=True,  # Allow creation from SQLAlchemy models
        json_encoders={
            datetime: lambda v: v.isoformat(),  # Consistent datetime formatting
        }
    )
