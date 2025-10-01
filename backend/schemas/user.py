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
        Comprehensive validation for name fields to prevent XSS and ensure data quality.
        
        Uses multiple validation layers:
        1. HTML tag detection with regex
        2. Dangerous pattern detection
        3. Character whitelist approach
        4. Length validation
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
        
        # 3. Character whitelist approach (more secure than blacklist)
        # Allow: letters, numbers, spaces, hyphens, apostrophes, periods
        allowed_pattern = re.compile(r"^[a-zA-Z0-9\s\-'.]+$")
        if not allowed_pattern.match(v):
            raise ValueError("Name can only contain letters, numbers, spaces, hyphens, apostrophes, and periods.")
        
        # 4. Length validation (consistent with Field max_length)
        if len(v) > 50:
            raise ValueError("Name is too long. Please use 50 characters or less.")
        
        # 5. Prevent names that are only special characters
        if re.match(r'^[\s\-\'.]+$', v):
            raise ValueError("Name must contain at least one letter or number.")
            
        return v


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
        Apply the same comprehensive validation as UserCreate for security consistency.
        
        This ensures that updates cannot bypass the security validations applied during creation.
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
        
        # 3. Character whitelist approach (more secure than blacklist)
        # Allow: letters, numbers, spaces, hyphens, apostrophes, periods
        allowed_pattern = re.compile(r"^[a-zA-Z0-9\s\-'.]+$")
        if not allowed_pattern.match(v):
            raise ValueError("Name can only contain letters, numbers, spaces, hyphens, apostrophes, and periods.")
        
        # 4. Length validation (consistent with Field max_length)
        if len(v) > 50:
            raise ValueError("Name is too long. Please use 50 characters or less.")
        
        # 5. Prevent names that are only special characters
        if re.match(r'^[\s\-\'.]+$', v):
            raise ValueError("Name must contain at least one letter or number.")
            
        return v


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
