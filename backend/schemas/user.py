"""
User-related Pydantic schemas for API serialization and validation.

These schemas define the structure for user data in API requests and responses,
providing automatic validation and documentation generation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional
import re
import unicodedata


def _validate_name_field(v: Optional[str]) -> Optional[str]:
    """
    Comprehensive validation for name fields to prevent XSS and ensure data quality.
    
    Uses multiple validation layers:
    1. HTML tag detection with regex
    2. Dangerous pattern detection
    3. Character whitelist that supports international characters
    4. Length validation
    5. Content requirements (must contain letters/numbers)
    
    Args:
        v: Name field value to validate
        
    Returns:
        Optional[str]: Validated and cleaned name, or None if empty
        
    Raises:
        ValueError: If validation fails
    """
    if v is None:
        return v
        
    # Strip whitespace first
    v = v.strip()
    
    # Check for empty string after stripping
    if not v:
        return None
        
    # 1. HTML tag detection using regex (more robust than string matching)
    html_pattern = re.compile(r'<[^>]*>', re.IGNORECASE)
    if html_pattern.search(v):
        raise ValueError("HTML tags are not allowed in names.")
    
    # 2. Check for dangerous patterns that could be used for XSS
    dangerous_patterns = [
        r'javascript:', r'data:', r'vbscript:', r'file:', r'ftp:',
        r'on\w+\s*=',  # Event handlers like onclick=, onload=, etc.
        r'expression\s*\(',  # CSS expressions
        r'url\s*\(',  # CSS url() functions
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, v, re.IGNORECASE):
            raise ValueError("Name contains invalid characters. Please use only letters, numbers, spaces, and basic punctuation.")
    
    # 3. Character whitelist that supports international characters
    # Use Unicode categories to allow letters from any language while maintaining security
    allowed_punctuation = set(" -'.")
    for char in v:
        category = unicodedata.category(char)
        # Allow letters (L*), numbers (N*), and specific safe punctuation
        if not (category.startswith('L') or category.startswith('N') or char in allowed_punctuation):
            raise ValueError("Name can only contain letters, numbers, spaces, hyphens, apostrophes, and periods.")
    
    # 4. Length validation (consistent with Field max_length)
    if len(v) > 50:
        raise ValueError("Name is too long. Please use 50 characters or less.")
    
    # 5. Prevent names that are only special characters
    # Check if name contains at least one letter or number using Unicode categories
    has_letter_or_number = any(
        unicodedata.category(char).startswith('L') or unicodedata.category(char).startswith('N')
        for char in v
    )
    if not has_letter_or_number:
        raise ValueError("Name must contain at least one letter or number.")
        
    return v


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(
        description="User's email address",
        example="user@example.com"
    )
    first_name: Optional[str] = Field(
        None,
        max_length=50,  # Consistent with validator
        description="User's first name",
        example="John"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=50,  # Consistent with validator
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
        """
        Validate name fields using shared validation logic.
        
        Delegates to _validate_name_field for consistent validation across all schemas.
        """
        return _validate_name_field(v)


class UserUpdate(BaseModel):
    """Schema for user update requests."""
    
    first_name: Optional[str] = Field(
        None,
        max_length=50,  # Consistent with UserCreate
        description="User's first name"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=50,  # Consistent with UserCreate
        description="User's last name"
    )
    
    @validator('first_name', 'last_name')
    def validate_name_fields(cls, v):
        """
        Validate name fields using shared validation logic.
        
        Delegates to _validate_name_field for consistent validation across all schemas.
        This ensures that updates cannot bypass the security validations applied during creation.
        """
        return _validate_name_field(v)


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
