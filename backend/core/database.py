"""
Database configuration and session management.

This module sets up SQLAlchemy async engine and session factory for PostgreSQL.
Uses async patterns for better performance under load.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from core.config import settings


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    Provides common functionality and ensures consistent table naming.
    """
    pass


# Async engine for PostgreSQL with asyncpg driver
# pool_pre_ping=True ensures connections are validated before use
# echo=True in development for SQL query logging (disabled in production for security)

# Convert sync PostgreSQL URL to async URL if needed (for Railway compatibility)
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    database_url,
    pool_pre_ping=True,
    echo=not settings.is_production,  # Only log SQL queries in development
    # Production-optimized connection pooling
    pool_size=5,  # Good for async workloads
    max_overflow=10,  # Allow burst capacity
    pool_recycle=3600,  # Recycle connections every hour
    pool_timeout=30,  # Connection timeout
)

# Async session factory
# expire_on_commit=False prevents lazy loading issues with async sessions
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides database sessions to FastAPI endpoints.
    
    Ensures proper session lifecycle management:
    - Creates new session for each request
    - Automatically closes session after request completion
    - Handles exceptions gracefully
    
    Yields:
        AsyncSession: Database session for the request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            # Rollback on any exception to maintain data consistency
            await session.rollback()
            raise
        finally:
            # Session is automatically closed by async context manager
            pass


async def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined in models if they don't exist.
    Uses checkfirst=True to avoid duplicate table errors.
    """
    try:
        async with engine.begin() as conn:
            # Import all models here to ensure they're registered with Base
            from models import user  # noqa: F401
            
            # Create all tables only if they don't exist (checkfirst=True)
            await conn.run_sync(
                lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True)
            )
    except Exception as e:
        # Log the error but don't fail startup if tables already exist
        import logging
        logger = logging.getLogger(__name__)
        if "already exists" in str(e) or "duplicate" in str(e).lower():
            logger.info("Database tables already exist, skipping creation")
        else:
            logger.error(f"Database initialization failed: {e}")
            raise
