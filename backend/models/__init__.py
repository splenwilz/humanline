"""
Database models package.

This package contains all SQLAlchemy models for the application.
Models are imported here to ensure they're registered with the Base class.
"""

from .user import User

__all__ = ["User"]
