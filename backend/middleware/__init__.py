"""
Middleware package for request/response processing.

This package contains middleware components for security, logging,
and other cross-cutting concerns.
"""

from .security import SecurityMiddleware

__all__ = ["SecurityMiddleware"]
