"""
Pytest configuration and fixtures for onboarding system tests.

This module provides shared test fixtures following FastAPI testing patterns:
- Database fixtures with transaction rollback for isolation
- Authentication fixtures for testing protected endpoints
- Test client fixtures for API testing
- Mock data factories for consistent test data

Based on FastAPI testing documentation:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from datetime import date, datetime, timezone

from fastapi import FastAPI
from main import app
from core.database import get_db, Base
from core.config import settings
from models.user import User
from models.onboarding import Onboarding
from services.auth_service import AuthService
from schemas.auth import RegisterRequest


# Test database configuration
# Use SQLite for tests - fast, isolated, and avoids async event loop issues
import os
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "sqlite+aiosqlite:///:memory:"
)


@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for async tests.
    
    Session-scoped to avoid issues with async fixtures.
    Required for pytest-asyncio compatibility.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    """
    Create test database engine with SQLite.
    
    Benefits of using SQLite for tests:
    - Fast test execution (in-memory database)
    - Complete isolation between test runs
    - No async event loop issues
    - Supports async operations via aiosqlite
    
    Session-scoped to reuse the same engine across tests.
    """
    from sqlalchemy.pool import StaticPool
    
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
        # Ensure connection sharing for in-memory database
        pool_pre_ping=True,
        pool_recycle=-1,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create database session with automatic cleanup.
    
    Each test gets a fresh session with proper cleanup after the test,
    ensuring complete isolation between tests.
    """
    # Create session factory
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        # Begin a transaction
        transaction = await session.begin()
        
        try:
            yield session
        finally:
            # Always rollback to ensure test isolation
            await transaction.rollback()
            await session.close()


@pytest_asyncio.fixture
async def shared_db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a shared database session for the entire test.
    
    This session is used by both test fixtures and the API client,
    ensuring data consistency across the test.
    """
    # Create session factory
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        # Begin a transaction that will be rolled back after the test
        transaction = await session.begin()
        
        try:
            yield session
        finally:
            # Always rollback to ensure test isolation
            try:
                if transaction.is_active:
                    await transaction.rollback()
            except Exception:
                # If rollback fails, just continue - the session will be closed anyway
                pass
            
            # Close session safely
            try:
                await session.close()
            except Exception:
                # If close fails, just continue - avoid event loop errors
                pass


@pytest_asyncio.fixture
async def client(shared_db_session: AsyncSession) -> AsyncGenerator[TestClient, None]:
    """
    Create FastAPI test client with database dependency override.
    
    This fixture:
    1. Creates a test app without lifespan events
    2. Overrides the database dependency to use shared test session
    3. Creates TestClient for making HTTP requests
    
    Usage in tests:
        def test_endpoint(client):
            response = client.get("/api/v1/onboarding/status")
            assert response.status_code == 403  # No auth
    """
    
    def override_get_db():
        """Override database dependency for testing."""
        # Return the shared session for all requests
        yield shared_db_session
    
    # Create a test app without lifespan events to avoid PostgreSQL connection
    test_app = FastAPI(
        title=app.title,
        description=app.description,
        version=app.version,
        # No lifespan to avoid database initialization
    )
    
    # Copy routes from the main app (but not the lifespan)
    for route in app.routes:
        test_app.routes.append(route)
    
    # Copy middleware from the main app
    for middleware in app.user_middleware:
        # Access middleware attributes correctly
        test_app.add_middleware(middleware.cls, **middleware.kwargs)
    
    # Override the database dependency in BOTH apps
    # This ensures ALL database requests use the test database
    app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_db] = override_get_db
    
    try:
        # Create test client using the test app
        with TestClient(test_app) as test_client:
            yield test_client
    finally:
        # Clean up the override from the main app
        if get_db in app.dependency_overrides:
            del app.dependency_overrides[get_db]


@pytest_asyncio.fixture
async def test_user(shared_db_session: AsyncSession) -> User:
    """
    Create a test user for authentication testing.
    
    Creates a verified, active user that can be used for testing
    protected endpoints. Password is 'testpassword123' for consistency.
    """
    register_data = RegisterRequest(
        email="testuser@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User"
    )
    
    # Create user using auth service to ensure proper hashing
    result = await AuthService.register(shared_db_session, register_data)
    
    # Get the created user
    from sqlalchemy import select
    result = await shared_db_session.execute(
        select(User).where(User.email == register_data.email)
    )
    user = result.scalar_one()
    
    # Ensure user is verified for testing
    user.is_verified = True
    await shared_db_session.commit()
    await shared_db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User, shared_db_session: AsyncSession) -> dict:
    """
    Create authentication headers for testing protected endpoints.
    
    Returns headers dict with Bearer token for the test user.
    This allows easy testing of protected endpoints.
    
    Usage:
        def test_protected_endpoint(client, auth_headers):
            response = client.get("/api/v1/onboarding", headers=auth_headers)
            assert response.status_code == 200
    """
    from schemas.auth import LoginRequest
    
    # Login to get token
    login_data = LoginRequest(
        email=test_user.email,
        password="testpassword123"
    )
    
    token_response = await AuthService.login(shared_db_session, login_data)
    
    return {
        "Authorization": f"Bearer {token_response.access_token}",
        "Content-Type": "application/json"
    }


@pytest_asyncio.fixture
async def test_user_with_onboarding(shared_db_session: AsyncSession) -> tuple[User, Onboarding]:
    """
    Create test user with completed onboarding.
    
    Useful for testing scenarios where onboarding already exists.
    Returns tuple of (user, onboarding) for convenience.
    """
    # Create user
    register_data = RegisterRequest(
        email="onboarded@example.com",
        password="testpassword123",
        first_name="Onboarded",
        last_name="User"
    )
    
    result = await AuthService.register(shared_db_session, register_data)
    
    # Get user
    from sqlalchemy import select
    result = await shared_db_session.execute(
        select(User).where(User.email == register_data.email)
    )
    user = result.scalar_one()
    user.is_verified = True
    
    # Create onboarding
    onboarding = Onboarding(
        user_id=user.id,
        company_name="Test Company",
        company_domain="testcompany",
        company_size="1-10",
        company_industry="fintech",
        company_roles="ceo-founder-owner",
        your_needs="onboarding-new-employees",
        onboarding_completed=True,
        workspace_created=False
    )
    
    shared_db_session.add(onboarding)
    await shared_db_session.commit()
    await shared_db_session.refresh(user)
    await shared_db_session.refresh(onboarding)
    
    return user, onboarding


# Test data factories for consistent test data
class OnboardingDataFactory:
    """Factory for creating consistent onboarding test data."""
    
    @staticmethod
    def valid_onboarding_data(domain: str = "testcompany") -> dict:
        """Create valid onboarding data for testing."""
        return {
            "company_name": "Test Company Inc",
            "company_domain": domain,
            "company_size": "1-10",
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
    
    @staticmethod
    def invalid_onboarding_data() -> dict:
        """Create invalid onboarding data for validation testing."""
        return {
            "company_name": "",  # Too short
            "company_domain": "invalid-domain!",  # Invalid characters
            "company_size": "invalid-size",  # Not in enum
            "company_industry": "",  # Empty string (now invalid)
            "company_roles": "",  # Empty string (now invalid)
            "your_needs": ""  # Empty string (now invalid)
        }


# Additional employee test fixtures
@pytest_asyncio.fixture
async def employee_id(shared_db_session: AsyncSession, test_user: User) -> int:
    """Create a test employee and return its ID."""
    from models.employee import Employee
    
    employee = Employee(
        user_id=test_user.id,
        first_name="Test",
        last_name="Employee",
        email="test.employee@example.com",
        phone="+1234567890",
        join_date=date(2024, 1, 15)
    )
    
    shared_db_session.add(employee)
    await shared_db_session.commit()
    await shared_db_session.refresh(employee)
    
    return employee.id

@pytest_asyncio.fixture
async def employee_with_personal_details(shared_db_session: AsyncSession, test_user: User) -> int:
    """Create a test employee with personal details and return employee ID."""
    from models.employee import Employee, EmployeePersonalDetails
    
    employee = Employee(
        user_id=test_user.id,
        first_name="John",
        last_name="Smith",
        email="john.smith@example.com",
        phone="+1234567890",
        join_date=date(2024, 1, 15)
    )
    
    shared_db_session.add(employee)
    await shared_db_session.flush()  # Get the employee ID
    
    personal_details = EmployeePersonalDetails(
        employee_id=employee.id,
        gender="MALE",
        date_of_birth=date(1990, 5, 15),
        nationality="American",
        health_care_provider="Blue Cross",
        marital_status="SINGLE",
        personal_tax_id="123-45-6789",
        social_insurance_number="987654321",
        primary_address="123 Main St, Apt 4B",
        city="New York",
        state="NY",
        country="USA",
        postal_code="10001"
    )
    
    shared_db_session.add(personal_details)
    await shared_db_session.commit()
    await shared_db_session.refresh(employee)
    
    return employee.id

@pytest_asyncio.fixture
async def employee_with_bank_info(shared_db_session: AsyncSession, test_user: User) -> int:
    """Create a test employee with bank info and return employee ID."""
    from models.employee import Employee, EmployeeBankInfo
    
    employee = Employee(
        user_id=test_user.id,
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone="+1234567890",
        join_date=date(2024, 1, 15)
    )
    
    shared_db_session.add(employee)
    await shared_db_session.flush()  # Get the employee ID
    
    bank_info = EmployeeBankInfo(
        employee_id=employee.id,
        bank_name="Chase Bank",
        account_number="1234567890",
        routing_number="021000021",
        account_type="CHECKING",
        account_holder_name="John Smith",
        account_holder_type="INDIVIDUAL",
        is_primary=True,
        is_active=True
    )
    
    shared_db_session.add(bank_info)
    await shared_db_session.commit()
    await shared_db_session.refresh(employee)
    
    return employee.id

@pytest_asyncio.fixture
async def employee_with_documents(shared_db_session: AsyncSession, test_user: User) -> int:
    """Create a test employee with documents and return employee ID."""
    from models.employee import Employee, EmployeeDocument
    
    employee = Employee(
        user_id=test_user.id,
        first_name="Alice",
        last_name="Johnson",
        email="alice.johnson@example.com",
        phone="+1234567890",
        join_date=date(2024, 1, 15)
    )
    
    shared_db_session.add(employee)
    await shared_db_session.flush()  # Get the employee ID
    
    # Create multiple documents
    documents = [
        EmployeeDocument(
            employee_id=employee.id,
            document_type="CONTRACT",
            file_name="employment_contract.pdf",
            file_path="/uploads/contracts/emp_contract.pdf",
            file_size=2048576,
            mime_type="application/pdf",
            upload_date=datetime.now(timezone.utc),
            uploaded_by_user_id=test_user.id,
            is_active=True
        ),
        EmployeeDocument(
            employee_id=employee.id,
            document_type="ID",
            file_name="drivers_license.pdf",
            file_path="/uploads/ids/drivers_license.pdf",
            file_size=1024768,
            mime_type="application/pdf",
            upload_date=datetime.now(timezone.utc),
            uploaded_by_user_id=test_user.id,
            is_active=True
        )
    ]
    
    for document in documents:
        shared_db_session.add(document)
    
    await shared_db_session.commit()
    await shared_db_session.refresh(employee)
    
    return employee.id

@pytest_asyncio.fixture
async def other_user_employee(shared_db_session: AsyncSession) -> int:
    """Create an employee belonging to a different user."""
    from models.employee import Employee
    from services.auth_service import AuthService
    
    # Create another user
    other_user_data = RegisterRequest(
        email="other.user@example.com",
        password="password123",
        first_name="Other",
        last_name="User"
    )
    
    other_user_response = await AuthService.register(shared_db_session, other_user_data)
    
    # Create employee for other user
    employee = Employee(
        user_id=other_user_response["token_response"].user["id"],
        first_name="Other",
        last_name="Employee",
        email="other.employee@example.com",
        phone="+9876543210",
        join_date=date(2024, 2, 1)
    )
    
    shared_db_session.add(employee)
    await shared_db_session.commit()
    await shared_db_session.refresh(employee)
    
    return employee.id

# Export fixtures for easy importing
__all__ = [
    "db_session",
    "client", 
    "test_user",
    "auth_headers",
    "test_user_with_onboarding",
    "OnboardingDataFactory",
    "employee_id",
    "employee_with_personal_details",
    "employee_with_bank_info", 
    "employee_with_documents",
    "other_user_employee"
]
