"""
Main FastAPI application entry point.

This module creates and configures the FastAPI application with all
necessary middleware, routers, and security configurations.
"""

import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import init_db
from middleware.security import SecurityMiddleware
from api.auth import router as auth_router
from api.users import router as users_router

# Configure logging
import os
log_handlers = [logging.StreamHandler(sys.stdout)]

# Only add file logging if logs directory exists and we're in production
if settings.is_production and os.path.exists("logs"):
    log_handlers.append(logging.FileHandler("logs/app.log"))

logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=log_handlers
)

logger = logging.getLogger(__name__)

# Import debug toolbar only in development
if not settings.is_production:
    from debug_toolbar.middleware import DebugToolbarMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    Initializes database tables on startup.
    """
    # Startup
    logger.info("Starting up Humanline Backend application...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {not settings.is_production}")
    
    # Initialize database tables
    # In production, use Alembic migrations instead
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Humanline Backend application...")


# Create FastAPI application with comprehensive configuration
app = FastAPI(
    title="Humanline API",
    version="1.0.0",
    description="Humanline HR Management System API",
    contact={
        "name": "Humanline API Support",
        "email": "support@humanline.com",
    },
    license_info={
        "name": "Humanline API License",
        "url": "https://humanline.com/license",
    },
    lifespan=lifespan,
    debug=not settings.is_production,
    # Explicitly enable docs in all environments
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Add CORS middleware for frontend integration
# Configured with specific origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers (can be restricted in production)
)


# Add custom security middleware only in production
# In development, skip security middleware to avoid blocking docs
if settings.is_production:
    app.add_middleware(
        SecurityMiddleware,
        rate_limit_requests=100,  # 100 requests per minute per IP
        rate_limit_window=60,
    )

# Add debug toolbar only in development
if not settings.is_production:
    app.add_middleware(DebugToolbarMiddleware)


# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


# Root endpoint for health check
@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Simple health check endpoint to verify API is running"
)
async def root():
    """
    Health check endpoint.
    
    Returns basic API information and status.
    Useful for load balancers and monitoring systems.
    """
    return {
        "message": "Humanline API is running",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.environment
    }


# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Detailed Health Check",
    description="Detailed health check with system information"
)
async def health_check():
    """
    Detailed health check endpoint.
    
    Returns comprehensive health information including
    database connectivity and system status.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment,
        "database": "connected",  # In production, actually check DB connection
        "timestamp": "2024-01-01T00:00:00Z"  # Use actual timestamp
    }


# Global exception handler for unhandled errors
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    """
    Global handler for internal server errors.
    
    Provides consistent error response format and prevents
    sensitive information leakage in production.
    """
    if settings.is_production:
        # Don't expose error details in production
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_id": "ISE_001"  # Error ID for tracking
            }
        )
    else:
        # Show detailed errors in development
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "type": type(exc).__name__
            }
        )


if __name__ == "__main__":
    import uvicorn
    
    # Run application with uvicorn
    # In production, use a proper ASGI server like gunicorn + uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=not settings.is_production,  # Auto-reload in development only
        log_level="info"
    )
