"""
Security utilities for authentication and authorization.

This module provides secure password hashing, JWT token creation/verification,
and other security-related functionality using industry best practices.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings


# Password hashing context using Argon2
# Argon2 is the winner of the Password Hashing Competition and is more secure than bcrypt
# It has no length limitations and provides better resistance to GPU attacks
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    # Optimized for production speed while maintaining security
    argon2__memory_cost=8192,   # 8 MB memory usage (8x faster)
    argon2__time_cost=2,        # 2 iterations (1.5x faster)
    argon2__parallelism=1,      # Single thread (Railway containers have limited CPU)
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The stored hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using Argon2.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Hashed password suitable for storage
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),  # Issued at
        "type": "access_token",  # Token type for additional validation
    })
    
    # Encode token with secret key
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict: Decoded token payload if valid, None if invalid
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        # Validate token type
        if payload.get("type") != "access_token":
            return None
            
        return payload
        
    except JWTError:
        # Token is invalid (expired, malformed, wrong signature, etc.)
        return None


def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        str: JWT token if valid format, None otherwise
    """
    if not authorization:
        return None
        
    # Check for Bearer token format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
        
    return parts[1]
