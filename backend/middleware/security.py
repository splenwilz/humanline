"""
Security middleware for enhanced API protection.

This middleware adds security headers and implements rate limiting
to protect against common web vulnerabilities and abuse.
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware that adds protective headers and basic rate limiting.
    
    Features:
    - Security headers for XSS, clickjacking, and content type protection
    - Basic rate limiting per IP address
    - Request timing for performance monitoring
    """
    
    def __init__(self, app, rate_limit_requests: int = 100, rate_limit_window: int = 60):
        """
        Initialize security middleware.
        
        Args:
            app: FastAPI application instance
            rate_limit_requests: Maximum requests per window
            rate_limit_window: Time window in seconds
        """
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        
        # Simple in-memory rate limiting storage
        # In production, use Redis or similar distributed cache
        self.request_counts: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request through security middleware.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain
            
        Returns:
            Response: HTTP response with security headers
        """
        # Skip security headers for docs and debug toolbar routes to avoid CSP conflicts
        is_docs_route = request.url.path in ["/docs", "/redoc", "/openapi.json"]
        is_debug_route = request.url.path.startswith("/_debug_toolbar")
        
        # Get client IP address
        client_ip = self._get_client_ip(request)
        
        # Check rate limit (but be more lenient for docs and debug routes)
        if not (is_docs_route or is_debug_route) and self._is_rate_limited(client_ip):
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=429,
                headers={"Retry-After": str(self.rate_limit_window)}
            )
        
        # Record request timestamp for rate limiting
        if not (is_docs_route or is_debug_route):
            self._record_request(client_ip)
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add security headers (skip CSP for docs and debug routes)
        if not (is_docs_route or is_debug_route):
            self._add_security_headers(response)
        elif is_docs_route:
            # Add minimal security headers for docs
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"  # Allow iframe for docs
        # Debug routes get no security headers to avoid conflicts
        
        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.
        
        Checks X-Forwarded-For header first (for proxy/load balancer setups),
        then falls back to direct client IP.
        
        Args:
            request: HTTP request object
            
        Returns:
            str: Client IP address
        """
        # Check for forwarded IP (from proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in case of multiple proxies
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header (some proxies use this)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """
        Check if client IP has exceeded rate limit.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            bool: True if rate limited, False otherwise
        """
        current_time = time.time()
        window_start = current_time - self.rate_limit_window
        
        # Get requests within current window
        requests_in_window = [
            timestamp for timestamp in self.request_counts[client_ip]
            if timestamp > window_start
        ]
        
        return len(requests_in_window) >= self.rate_limit_requests
    
    def _record_request(self, client_ip: str) -> None:
        """
        Record request timestamp for rate limiting.
        
        Args:
            client_ip: Client IP address
        """
        current_time = time.time()
        window_start = current_time - self.rate_limit_window
        
        # Clean old requests outside window
        self.request_counts[client_ip] = [
            timestamp for timestamp in self.request_counts[client_ip]
            if timestamp > window_start
        ]
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
    
    def _add_security_headers(self, response: Response) -> None:
        """
        Add security headers to response.
        
        Args:
            response: HTTP response object
        """
        # Prevent XSS attacks
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy (allow Swagger UI resources)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self'"
        )
        
        # HSTS for HTTPS (only add if using HTTPS)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
