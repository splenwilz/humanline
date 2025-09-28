"""
API routes package.

This package contains all FastAPI routers and endpoint definitions.
Routes are organized by feature/domain for better maintainability.
"""

from .auth import router as auth_router
from .users import router as users_router

__all__ = ["auth_router", "users_router"]
