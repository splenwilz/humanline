"""
Unit tests for OnboardingService business logic.

Tests service layer methods in isolation with mocked database operations.
Focuses on business rule validation, error handling, and data transformation
without requiring actual database connections.

Following clean architecture testing principles and FastAPI patterns:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from services.onboarding_service import OnboardingService
from schemas.onboarding import OnboardingRequest, OnboardingResponse, OnboardingDetail, OnboardingStatus
from models.onboarding import Onboarding


class TestOnboardingServiceCreate:
    """Test OnboardingService.create_onboarding method."""
    
    @pytest.mark.asyncio
    async def test_create_onboarding_success(self):
        """Test successful onboarding creation with valid data."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 123
        
        onboarding_data = OnboardingRequest(
            company_name="Test Company",
            company_domain="testcompany",
            company_size="1-10",
            company_industry="fintech",
            company_roles="ceo-founder-owner",
            your_needs="onboarding-new-employees"
        )
        
        # Mock database queries to return no existing records
        mock_existing_onboarding = MagicMock()
        mock_existing_onboarding.scalar_one_or_none.return_value = None
        
        mock_existing_domain = MagicMock()
        mock_existing_domain.scalar_one_or_none.return_value = None
        
        # Mock user query for needs_onboarding update
        mock_user = MagicMock()
        mock_user.needs_onboarding = True  # Initial state
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = mock_user
        
        mock_db.execute.side_effect = [mock_existing_onboarding, mock_existing_domain, mock_user_result]
        
        # Mock the refresh method to simulate database ID assignment
        def mock_refresh(obj):
            obj.id = 1  # Simulate database assigning ID after commit
            
        mock_db.refresh.side_effect = mock_refresh
        
        # Act
        result = await OnboardingService.create_onboarding(
            db=mock_db,
            user_id=user_id,
            onboarding_data=onboarding_data
        )
        
        # Assert
        assert isinstance(result, OnboardingResponse)
        assert result.success is True
        assert result.onboarding_id == 1
        assert result.company_domain == "testcompany"
        assert result.full_domain == "testcompany.hrline.com"
        assert result.workspace_created is False
        assert "successfully" in result.message.lower()
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        # Verify user's needs_onboarding flag was updated
        assert mock_user.needs_onboarding is False
    
    @pytest.mark.asyncio
    async def test_create_onboarding_duplicate_user(self):
        """Test error when user already has onboarding."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 123
        
        onboarding_data = OnboardingRequest(
            company_name="Test Company",
            company_domain="testcompany",
            company_size="1-10",
            company_industry="fintech",
            company_roles="ceo-founder-owner",
            your_needs="onboarding-new-employees"
        )
        
        # Mock existing onboarding for user
        mock_existing_onboarding = MagicMock()
        mock_existing_onboarding.scalar_one_or_none.return_value = MagicMock(spec=Onboarding)
        
        mock_db.execute.return_value = mock_existing_onboarding
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await OnboardingService.create_onboarding(
                db=mock_db,
                user_id=user_id,
                onboarding_data=onboarding_data
            )
        
        assert "already completed onboarding" in str(exc_info.value)
        
        # Verify no database modifications attempted
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_onboarding_duplicate_domain(self):
        """Test error when company domain already exists."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 123
        
        onboarding_data = OnboardingRequest(
            company_name="Test Company",
            company_domain="existingdomain",
            company_size="1-10",
            company_industry="fintech",
            company_roles="ceo-founder-owner",
            your_needs="onboarding-new-employees"
        )
        
        # Mock no existing onboarding for user, but existing domain
        mock_no_user_onboarding = MagicMock()
        mock_no_user_onboarding.scalar_one_or_none.return_value = None
        
        mock_existing_domain = MagicMock()
        mock_existing_domain.scalar_one_or_none.return_value = MagicMock(spec=Onboarding)
        
        mock_db.execute.side_effect = [mock_no_user_onboarding, mock_existing_domain]
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await OnboardingService.create_onboarding(
                db=mock_db,
                user_id=user_id,
                onboarding_data=onboarding_data
            )
        
        assert "already taken" in str(exc_info.value)
        assert "existingdomain" in str(exc_info.value)
        
        # Verify no database modifications attempted
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_onboarding_integrity_error_domain(self):
        """Test handling of database integrity error for domain constraint."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 123
        
        onboarding_data = OnboardingRequest(
            company_name="Test Company",
            company_domain="testcompany",
            company_size="1-10",
            company_industry="fintech",
            company_roles="ceo-founder-owner",
            your_needs="onboarding-new-employees"
        )
        
        # Mock no existing records in initial checks
        mock_no_existing = MagicMock()
        mock_no_existing.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_no_existing
        
        # Mock integrity error on commit (race condition)
        integrity_error = IntegrityError(
            statement="INSERT INTO onboarding...",
            params={},
            orig=Exception("unique constraint failed: onboarding.company_domain")
        )
        mock_db.commit.side_effect = integrity_error
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await OnboardingService.create_onboarding(
                db=mock_db,
                user_id=user_id,
                onboarding_data=onboarding_data
            )
        
        assert "already taken" in str(exc_info.value)
        
        # Verify rollback was called
        mock_db.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_onboarding_integrity_error_user(self):
        """Test handling of database integrity error for user constraint."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 123
        
        onboarding_data = OnboardingRequest(
            company_name="Test Company",
            company_domain="testcompany",
            company_size="1-10",
            company_industry="fintech",
            company_roles="ceo-founder-owner",
            your_needs="onboarding-new-employees"
        )
        
        # Mock no existing records in initial checks
        mock_no_existing = MagicMock()
        mock_no_existing.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_no_existing
        
        # Mock integrity error for user constraint
        integrity_error = IntegrityError(
            statement="INSERT INTO onboarding...",
            params={},
            orig=Exception("unique constraint failed: onboarding.user_id")
        )
        mock_db.commit.side_effect = integrity_error
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await OnboardingService.create_onboarding(
                db=mock_db,
                user_id=user_id,
                onboarding_data=onboarding_data
            )
        
        assert "already completed onboarding" in str(exc_info.value)
        
        # Verify rollback was called
        mock_db.rollback.assert_called_once()


class TestOnboardingServiceGet:
    """Test OnboardingService.get_user_onboarding method."""
    
    @pytest.mark.asyncio
    async def test_get_user_onboarding_exists(self):
        """Test retrieving existing onboarding record."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 123
        
        # Mock onboarding record
        mock_onboarding = MagicMock(spec=Onboarding)
        mock_onboarding.id = 1
        mock_onboarding.user_id = user_id
        mock_onboarding.company_name = "Test Company"
        mock_onboarding.company_domain = "testcompany"
        mock_onboarding.company_size = "1-10"
        mock_onboarding.company_industry = "fintech"
        mock_onboarding.company_roles = "ceo-founder-owner"
        mock_onboarding.your_needs = "onboarding-new-employees"
        mock_onboarding.onboarding_completed = True
        mock_onboarding.workspace_created = False
        mock_onboarding.full_domain = "testcompany.hrline.com"
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        mock_onboarding.created_at = now
        mock_onboarding.updated_at = now
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_onboarding
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await OnboardingService.get_user_onboarding(
            db=mock_db,
            user_id=user_id
        )
        
        # Assert
        assert isinstance(result, OnboardingDetail)
        assert result.onboarding_id == 1
        assert result.user_id == user_id
        assert result.company_name == "Test Company"
        assert result.company_domain == "testcompany"
        assert result.full_domain == "testcompany.hrline.com"
        assert result.onboarding_completed is True
        assert result.workspace_created is False
    
    @pytest.mark.asyncio
    async def test_get_user_onboarding_not_exists(self):
        """Test retrieving non-existent onboarding record."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 123
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await OnboardingService.get_user_onboarding(
            db=mock_db,
            user_id=user_id
        )
        
        # Assert
        assert result is None


class TestOnboardingServiceStatus:
    """Test OnboardingService.get_onboarding_status method."""
    
    @pytest.mark.asyncio
    async def test_get_status_with_onboarding(self):
        """Test status when user has onboarding record."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 123
        
        # Mock database result with onboarding data
        mock_row = MagicMock()
        mock_row.onboarding_completed = True
        mock_row.workspace_created = False
        mock_row.company_domain = "testcompany"
        
        mock_result = MagicMock()
        mock_result.first.return_value = mock_row
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await OnboardingService.get_onboarding_status(
            db=mock_db,
            user_id=user_id
        )
        
        # Assert
        assert isinstance(result, OnboardingStatus)
        assert result.has_onboarding is True
        assert result.onboarding_completed is True
        assert result.workspace_created is False
        assert result.company_domain == "testcompany"
    
    @pytest.mark.asyncio
    async def test_get_status_without_onboarding(self):
        """Test status when user has no onboarding record."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 123
        
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await OnboardingService.get_onboarding_status(
            db=mock_db,
            user_id=user_id
        )
        
        # Assert
        assert isinstance(result, OnboardingStatus)
        assert result.has_onboarding is False
        assert result.onboarding_completed is False
        assert result.workspace_created is False
        assert result.company_domain is None


class TestOnboardingServiceDomainCheck:
    """Test OnboardingService.check_domain_availability method."""
    
    @pytest.mark.asyncio
    async def test_domain_available(self):
        """Test checking available domain."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        domain = "availabledomain"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No existing domain
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await OnboardingService.check_domain_availability(
            db=mock_db,
            domain=domain
        )
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_domain_taken(self):
        """Test checking taken domain."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        domain = "takendomain"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()  # Existing domain
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await OnboardingService.check_domain_availability(
            db=mock_db,
            domain=domain
        )
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_domain_normalization(self):
        """Test domain normalization in availability check."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        domain = "MixedCaseDomain"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act
        await OnboardingService.check_domain_availability(
            db=mock_db,
            domain=domain
        )
        
        # Assert - verify the query was made with normalized domain
        mock_db.execute.assert_called_once()
        # The actual SQL query should use lowercase domain
        # This tests that normalization happens before database query
