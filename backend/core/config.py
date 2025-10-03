"""
Core configuration settings for the backend3 application.

This module centralizes all configuration management using Pydantic Settings
for type safety and validation. Environment variables are loaded from .env file.
"""

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic Settings for automatic validation and type conversion.
    All sensitive data should be loaded from environment variables.
    """
    
    # Database Configuration
    # Using asyncpg driver for async PostgreSQL operations
    database_url: str = Field(
        description="PostgreSQL database URL with asyncpg driver"
    )
    
    # JWT Security Configuration
    # SECRET_KEY must be cryptographically secure in production
    secret_key: str = Field(
        description="Secret key for JWT token signing - MUST be secure in production"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm - HS256 is secure and widely supported"
    )
    access_token_expire_minutes: int = Field(
        default=60,  # 1 hour for access token
        description="JWT token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=30,  # 30 days for refresh token
        description="Refresh token expiration time in days"
    )
    
    # CORS Configuration
    # Restricts which origins can make requests to our API
    allowed_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed origins for CORS"
    )
    
    # Environment Configuration
    environment: str = Field(
        default="development",
        description="Application environment (development/production)"
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Email Configuration
    # SMTP settings for sending confirmation emails
    smtp_host: str = Field(
        default="smtp.gmail.com",
        description="SMTP server hostname for sending emails"
    )
    smtp_port: int = Field(
        default=587,
        description="SMTP server port (587 for TLS, 465 for SSL)"
    )
    smtp_user: str = Field(
        default="",
        description="SMTP username/email address for authentication"
    )
    smtp_password: str = Field(
        default="",
        description="SMTP password or app-specific password"
    )
    from_email: str = Field(
        default="humanlinehr@gmail.com",
        description="Default sender email address for system emails"
    )
    
    # Email Confirmation Feature Toggle
    # Controls whether email confirmation is required before account activation
    require_email_confirmation: bool = Field(
        default=False,  # Disabled for testing
        description="Whether to require email confirmation before activating user accounts"
    )
    
    # Email confirmation token expiration (in hours)
    # Tokens expire after this time for security
    email_confirmation_expire_hours: int = Field(
        default=24,
        description="Email confirmation token expiration time in hours"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    @model_validator(mode='after')
    def validate_email_config(self) -> 'Settings':
        """Validate that SMTP credentials are provided when email confirmation is required."""
        if self.require_email_confirmation:
            if not self.smtp_user or not self.smtp_password:
                raise ValueError(
                    "SMTP credentials (smtp_user and smtp_password) are required "
                    "when require_email_confirmation is enabled"
                )
        return self
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins string to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


# Global settings instance
# Instantiated once and reused throughout the application
settings = Settings()
