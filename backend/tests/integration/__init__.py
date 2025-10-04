"""
Integration tests for onboarding system.

Integration tests verify the interaction between multiple components:
- API endpoints with database operations
- Authentication flow with protected endpoints
- End-to-end request/response cycles
- Database constraints and transactions

These tests use real database connections (in-memory SQLite) but are still fast.
"""
