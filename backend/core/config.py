"""
Core configuration settings for the backend3 application.

This module centralizes all configuration management using Pydantic Settings
for type safety and validation. Environment variables are loaded from .env file.
"""

from pydantic import Field
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
        default=30,
        description="JWT token expiration time in minutes"
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )
    
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
