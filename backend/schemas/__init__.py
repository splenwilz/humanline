"""
Pydantic schemas for request/response validation.

This package contains all Pydantic models used for API serialization,
validation, and documentation generation.
"""

from .auth import LoginRequest, RegisterRequest, TokenResponse
from .user import UserResponse, UserCreate, UserUpdate
from .onboarding import OnboardingRequest, OnboardingResponse, OnboardingDetail, OnboardingStatus

__all__ = [
    "LoginRequest",
    "RegisterRequest", 
    "TokenResponse",
    "UserResponse",
    "UserCreate",
    "UserUpdate",
    "OnboardingRequest",
    "OnboardingResponse", 
    "OnboardingDetail",
    "OnboardingStatus",
]
