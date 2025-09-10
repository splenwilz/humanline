from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
    exp: int
    iat: int


class TokenResponse(BaseModel):
    """Response model for token operations"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Response model for token refresh"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenValidationResponse(BaseModel):
    """Response model for token validation"""
    valid: bool
    user_id: Optional[str] = None
    email: Optional[str] = None
    message: Optional[str] = None
