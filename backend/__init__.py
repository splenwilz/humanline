"""
Backend3 - Secure FastAPI application with JWT authentication.

A modern, secure backend API built with FastAPI, SQLAlchemy, and PostgreSQL.
Features comprehensive authentication, security middleware, and clean architecture.
"""

__version__ = "1.0.0"

def main() -> None:
    """Entry point for the application."""
    import uvicorn
    from .core.config import settings
    
    uvicorn.run(
        "backend3.main:app",
        host=settings.host,
        port=settings.port,
        reload=not settings.is_production,
        log_level="info"
    )
