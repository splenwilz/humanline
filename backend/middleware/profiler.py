"""
Performance profiling middleware for detailed timing analysis.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ProfilingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to profile request performance and log detailed timing.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.perf_counter()
        
        # Log request start
        logger.info(f"🚀 Starting request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate total time
        total_time = time.perf_counter() - start_time
        
        # Log detailed timing
        logger.info(
            f"⏱️  Request completed: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {total_time:.3f}s"
        )
        
        # Add timing header to response
        response.headers["X-Process-Time"] = f"{total_time:.3f}"
        
        return response


def time_operation(operation_name: str):
    """
    Decorator to time individual operations within endpoints.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            logger.info(f"🔄 Starting: {operation_name}")
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.perf_counter() - start_time
                logger.info(f"✅ Completed: {operation_name} | Time: {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.perf_counter() - start_time
                logger.error(f"❌ Failed: {operation_name} | Time: {execution_time:.3f}s | Error: {str(e)}")
                raise
        
        return wrapper
    return decorator
