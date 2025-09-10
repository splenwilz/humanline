from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Supabase configuration
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: Optional[str] = None
    
    # JWT configuration
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    
    # Application settings
    app_name: str = "Humanline API"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
