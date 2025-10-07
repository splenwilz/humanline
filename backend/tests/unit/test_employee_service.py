"""Unit tests for employee service layer."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from services.employee import EmployeeService
from schemas.employee import (
    EmployeeRequest, EmployeeResponse, EmployeeFullRequest, EmployeeFullResponse,
    EmployeePersonalDetailsRequest, EmployeeBankInfoRequest, EmployeeJobTimelineRequest,
    EmployeeDependentRequest, EmployeeDocumentRequest
)
from models.employee import (
    Employee, EmployeePersonalDetails, EmployeeBankInfo, EmployeeJobTimeline,
    EmployeeDependent, EmployeeDocument
)
from models.user import User


class TestEmployeeServiceCreate:
    """Test EmployeeService.create_employee method."""
    
    @pytest.mark.asyncio
    async def test_create_employee_success(self):
        """Test successful employee creation."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        employee_data = EmployeeRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="(555) 123-4567",
            join_date=date(2024, 1, 15)
        )
        
        # Mock the refresh method to set the ID
        def mock_refresh(obj):
            obj.id = 1
            obj.user_id = 123
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)
        
        mock_db.refresh.side_effect = mock_refresh
        
        # Act
        result = await EmployeeService.create_employee(
            db=mock_db,
            employee_data=employee_data,
            current_user=current_user
        )
        
        # Assert
        assert isinstance(result, EmployeeResponse)
        assert result.id == 1
        assert result.user_id == 123
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.email == "john.doe@example.com"
        assert result.phone == "(555) 123-4567"
        assert result.join_date == date(2024, 1, 15)
        
        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_employee_email_duplicate(self):
        """Test error when email already exists."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        employee_data = EmployeeRequest(
            first_name="John",
            last_name="Doe",
            email="existing@example.com",
            phone="(555) 123-4567",
            join_date=date(2024, 1, 15)
        )
        
        # Mock integrity error for email constraint
        integrity_error = IntegrityError(
            statement="INSERT INTO employees...",
            params={},
            orig=Exception("unique constraint failed: employees.email")
        )
        mock_db.commit.side_effect = integrity_error
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await EmployeeService.create_employee(
                db=mock_db,
                employee_data=employee_data,
                current_user=current_user
            )
        
        assert "Email already exists" in str(exc_info.value)
        
        # Verify rollback was called
        mock_db.rollback.assert_called_once()


class TestEmployeeServiceGet:
    """Test EmployeeService.get_employee method."""
    
    @pytest.mark.asyncio
    async def test_get_employee_exists(self):
        """Test retrieving existing employee."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        # Mock employee
        mock_employee = MagicMock(spec=Employee)
        mock_employee.id = 1
        mock_employee.user_id = 123
        mock_employee.first_name = "John"
        mock_employee.last_name = "Doe"
        mock_employee.email = "john.doe@example.com"
        mock_employee.phone = "(555) 123-4567"
        mock_employee.join_date = date(2024, 1, 15)
        mock_employee.created_at = datetime.now(timezone.utc)
        mock_employee.updated_at = datetime.now(timezone.utc)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_employee
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await EmployeeService.get_employee(
            db=mock_db,
            employee_id=1,
            current_user=current_user
        )
        
        # Assert
        assert isinstance(result, EmployeeResponse)
        assert result.id == 1
        assert result.user_id == 123
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.email == "john.doe@example.com"
        assert result.phone == "(555) 123-4567"
        assert result.join_date == date(2024, 1, 15)
    
    @pytest.mark.asyncio
    async def test_get_employee_not_exists(self):
        """Test retrieving non-existent employee."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await EmployeeService.get_employee(
            db=mock_db,
            employee_id=999,
            current_user=current_user
        )
        
        # Assert
        assert result is None


# Note: update_employee and delete_employee methods don't exist in the service
# Only create_employee, get_employee, get_employee_full, list_employees, 
# create_employee_full, and update_employee_full are available


class TestEmployeeServiceList:
    """Test EmployeeService.list_employees method."""
    
    @pytest.mark.asyncio
    async def test_list_employees_success(self):
        """Test successful employee listing."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        # Mock employees
        mock_employee1 = MagicMock(spec=Employee)
        mock_employee1.id = 1
        mock_employee1.user_id = 123
        mock_employee1.first_name = "John"
        mock_employee1.last_name = "Doe"
        mock_employee1.email = "john.doe@example.com"
        mock_employee1.phone = "(555) 123-4567"
        mock_employee1.join_date = date(2024, 1, 15)
        mock_employee1.created_at = datetime.now(timezone.utc)
        mock_employee1.updated_at = datetime.now(timezone.utc)
        
        mock_employee2 = MagicMock(spec=Employee)
        mock_employee2.id = 2
        mock_employee2.user_id = 123
        mock_employee2.first_name = "Jane"
        mock_employee2.last_name = "Smith"
        mock_employee2.email = "jane.smith@example.com"
        mock_employee2.phone = "(555) 987-6543"
        mock_employee2.join_date = date(2024, 2, 1)
        mock_employee2.created_at = datetime.now(timezone.utc)
        mock_employee2.updated_at = datetime.now(timezone.utc)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_employee1, mock_employee2]
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await EmployeeService.list_employees(
            db=mock_db,
            current_user=current_user,
            skip=0,
            limit=10
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(emp, EmployeeResponse) for emp in result)
        assert result[0].first_name == "John"
        assert result[1].first_name == "Jane"


class TestEmployeeServiceCreateFull:
    """Test EmployeeService.create_employee_full method."""
    
    @pytest.mark.asyncio
    async def test_create_employee_full_success(self):
        """Test successful full employee creation."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        employee_data = EmployeeFullRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="(555) 123-4567",
            join_date=date(2024, 1, 15)
        )
        
        # Mock the refresh method for all objects
        def mock_refresh(obj):
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = 1
            if hasattr(obj, 'employee_id') and obj.employee_id is None:
                obj.employee_id = 1
            if hasattr(obj, 'user_id') and obj.user_id is None:
                obj.user_id = 123
            if hasattr(obj, 'uploaded_by_user_id') and obj.uploaded_by_user_id is None:
                obj.uploaded_by_user_id = 123
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)
            if hasattr(obj, 'upload_date'):
                obj.upload_date = datetime.now(timezone.utc)
            
        mock_db.refresh.side_effect = mock_refresh
        
        # Act
        result = await EmployeeService.create_employee_full(
            db=mock_db,
            employee_data=employee_data,
            current_user=current_user
        )
        
        # Assert
        assert isinstance(result, EmployeeFullResponse)
        assert result.id == 1
        assert result.user_id == 123
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.email == "john.doe@example.com"
        assert result.phone == "(555) 123-4567"
        assert result.join_date == date(2024, 1, 15)
        
        # Verify database operations
        assert mock_db.add.call_count >= 1  # At least the employee
        assert mock_db.commit.call_count >= 1
        assert mock_db.refresh.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_create_employee_full_email_duplicate(self):
        """Test error when email already exists in full creation."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        employee_data = EmployeeFullRequest(
            first_name="John",
            last_name="Doe",
            email="existing@example.com",
            phone="(555) 123-4567",
            join_date=date(2024, 1, 15)
        )
        
        # Mock integrity error for email constraint
        integrity_error = IntegrityError(
            statement="INSERT INTO employees...",
            params={},
            orig=Exception("unique constraint failed: employees.email")
        )
        mock_db.commit.side_effect = integrity_error
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await EmployeeService.create_employee_full(
                db=mock_db,
                employee_data=employee_data,
                current_user=current_user
            )
        
        assert "Email already exists" in str(exc_info.value)
        
        # Verify rollback was called
        mock_db.rollback.assert_called_once()


class TestEmployeeServiceGetFull:
    """Test EmployeeService.get_employee_full method."""
    
    @pytest.mark.asyncio
    async def test_get_employee_full_exists(self):
        """Test retrieving existing employee with full data."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        # Mock employee with related data
        mock_employee = MagicMock(spec=Employee)
        mock_employee.id = 1
        mock_employee.user_id = 123
        mock_employee.first_name = "John"
        mock_employee.last_name = "Doe"
        mock_employee.email = "john.doe@example.com"
        mock_employee.phone = "(555) 123-4567"
        mock_employee.join_date = date(2024, 1, 15)
        mock_employee.created_at = datetime.now(timezone.utc)
        mock_employee.updated_at = datetime.now(timezone.utc)
        
        # Mock personal details with all required fields
        mock_personal = MagicMock(spec=EmployeePersonalDetails)
        mock_personal.id = 1
        mock_personal.employee_id = 1
        mock_personal.gender = "MALE"
        mock_personal.date_of_birth = date(1990, 1, 1)
        mock_personal.nationality = "American"
        mock_personal.health_care_provider = "Blue Cross"
        mock_personal.marital_status = "SINGLE"
        mock_personal.personal_tax_id = "123-45-6789"
        mock_personal.social_insurance_number = "987-65-4321"
        mock_personal.primary_address = "123 Main St"
        mock_personal.city = "New York"
        mock_personal.state = "NY"
        mock_personal.country = "USA"
        mock_personal.postal_code = "10001"
        mock_personal.created_at = datetime.now(timezone.utc)
        mock_personal.updated_at = datetime.now(timezone.utc)
        mock_employee.personal_details = mock_personal
        
        # Mock bank info
        mock_bank = MagicMock(spec=EmployeeBankInfo)
        mock_bank.id = 1
        mock_bank.employee_id = 1
        mock_bank.bank_name = "Chase Bank"
        mock_bank.account_number = "1234567890"
        mock_bank.routing_number = "987654321"
        mock_bank.account_type = "CHECKING"
        mock_bank.account_holder_name = "John Doe"
        mock_bank.account_holder_type = "INDIVIDUAL"
        mock_bank.is_primary = True
        mock_bank.is_active = True
        mock_bank.created_at = datetime.now(timezone.utc)
        mock_bank.updated_at = datetime.now(timezone.utc)
        mock_employee.bank_info = mock_bank
        
        # Mock job timeline
        mock_job = MagicMock(spec=EmployeeJobTimeline)
        mock_job.id = 1
        mock_job.employee_id = 1
        mock_job.effective_date = date(2024, 1, 15)
        mock_job.end_date = None
        mock_job.job_title = "Software Engineer"
        mock_job.position_type = "FULL_TIME"
        mock_job.employment_type = "FULL_TIME"
        mock_job.line_manager_id = None
        mock_job.department = "Engineering"
        mock_job.office = "New York"
        mock_job.is_current = True
        mock_job.created_at = datetime.now(timezone.utc)
        mock_job.updated_at = datetime.now(timezone.utc)
        mock_employee.job_timeline = [mock_job]
        
        # Mock dependents
        mock_dependent = MagicMock(spec=EmployeeDependent)
        mock_dependent.id = 1
        mock_dependent.employee_id = 1
        mock_dependent.name = "Jane Doe"
        mock_dependent.relationship_type = "SPOUSE"
        mock_dependent.date_of_birth = date(1992, 5, 10)
        mock_dependent.gender = "FEMALE"
        mock_dependent.nationality = "American"
        mock_dependent.primary_address = "123 Main St"
        mock_dependent.city = "New York"
        mock_dependent.state = "NY"
        mock_dependent.country = "USA"
        mock_dependent.postal_code = "10001"
        mock_dependent.is_active = True
        mock_dependent.created_at = datetime.now(timezone.utc)
        mock_dependent.updated_at = datetime.now(timezone.utc)
        mock_employee.dependents = [mock_dependent]
        
        # Mock documents
        mock_document = MagicMock(spec=EmployeeDocument)
        mock_document.id = 1
        mock_document.employee_id = 1
        mock_document.document_type = "PASSPORT"
        mock_document.file_name = "passport.pdf"
        mock_document.file_path = "/uploads/passport.pdf"
        mock_document.file_size = 1024000
        mock_document.mime_type = "application/pdf"
        mock_document.uploaded_by_user_id = 123
        mock_document.upload_date = datetime.now(timezone.utc)
        mock_document.is_active = True
        mock_document.created_at = datetime.now(timezone.utc)
        mock_document.updated_at = datetime.now(timezone.utc)
        mock_employee.documents = [mock_document]
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_employee
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await EmployeeService.get_employee_full(
            db=mock_db,
            employee_id=1,
            current_user=current_user
        )
        
        # Assert
        assert isinstance(result, EmployeeFullResponse)
        assert result.id == 1
        assert result.user_id == 123
        assert result.first_name == "John"
        assert result.personal_details is not None
        assert result.bank_info is not None
        assert len(result.job_timeline) == 1
        assert len(result.dependents) == 1
        assert len(result.documents) == 1
    
    @pytest.mark.asyncio
    async def test_get_employee_full_not_exists(self):
        """Test retrieving non-existent employee with full data."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act
        result = await EmployeeService.get_employee_full(
            db=mock_db,
            employee_id=999,
            current_user=current_user
        )
        
        # Assert
        assert result is None


class TestEmployeeServiceUpdateFull:
    """Test EmployeeService.update_employee_full method."""
    
    @pytest.mark.asyncio
    async def test_update_employee_full_success(self):
        """Test successful full employee update."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        # Mock existing employee
        mock_employee = MagicMock(spec=Employee)
        mock_employee.id = 1
        mock_employee.user_id = 123
        mock_employee.first_name = "John"
        mock_employee.last_name = "Doe"
        mock_employee.email = "john.doe@example.com"
        mock_employee.phone = "(555) 123-4567"
        mock_employee.join_date = date(2024, 1, 15)
        mock_employee.created_at = datetime.now(timezone.utc)
        mock_employee.updated_at = datetime.now(timezone.utc)
        
        # Mock existing related data
        mock_personal = MagicMock(spec=EmployeePersonalDetails)
        mock_personal.employee_id = 1
        mock_employee.personal_details = mock_personal
        
        mock_bank = MagicMock(spec=EmployeeBankInfo)
        mock_bank.employee_id = 1
        mock_employee.bank_info = mock_bank
        
        mock_job = MagicMock(spec=EmployeeJobTimeline)
        mock_job.employee_id = 1
        mock_employee.job_timeline = [mock_job]
        
        mock_dependent = MagicMock(spec=EmployeeDependent)
        mock_dependent.employee_id = 1
        mock_employee.dependents = [mock_dependent]
        
        mock_document = MagicMock(spec=EmployeeDocument)
        mock_document.employee_id = 1
        mock_employee.documents = [mock_document]
        
        # Mock database queries
        mock_employee_result = MagicMock()
        mock_employee_result.scalar_one_or_none.return_value = mock_employee
        
        mock_personal_result = MagicMock()
        mock_personal_result.scalars.return_value = [mock_personal]
        
        mock_bank_result = MagicMock()
        mock_bank_result.scalars.return_value = [mock_bank]
        
        mock_job_result = MagicMock()
        mock_job_result.scalars.return_value = [mock_job]
        
        mock_dep_result = MagicMock()
        mock_dep_result.scalars.return_value = [mock_dependent]
        
        mock_doc_result = MagicMock()
        mock_doc_result.scalars.return_value = [mock_document]
        
        mock_db.execute.side_effect = [
            mock_employee_result,  # Get employee
            mock_personal_result,  # Delete personal details
            mock_bank_result,      # Delete bank info
            mock_job_result,       # Delete job timeline
            mock_dep_result,       # Delete dependents
            mock_doc_result        # Delete documents
        ]
        
        employee_data = EmployeeFullRequest(
            first_name="Updated John",
            last_name="Updated Doe",
            email="updated.john@example.com",
            phone="(555) 987-6543",
            join_date=date(2024, 2, 1)
        )
        
        # Mock the refresh method for all objects
        def mock_refresh(obj):
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = 1
            if hasattr(obj, 'employee_id') and obj.employee_id is None:
                obj.employee_id = 1
            if hasattr(obj, 'user_id') and obj.user_id is None:
                obj.user_id = 123
            if hasattr(obj, 'uploaded_by_user_id') and obj.uploaded_by_user_id is None:
                obj.uploaded_by_user_id = 123
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)
            if hasattr(obj, 'upload_date'):
                obj.upload_date = datetime.now(timezone.utc)
            
        mock_db.refresh.side_effect = mock_refresh
        
        # Act
        result = await EmployeeService.update_employee_full(
            db=mock_db,
            employee_id=1,
            employee_data=employee_data,
            current_user=current_user
        )
        
        # Assert
        assert isinstance(result, EmployeeFullResponse)
        assert result.id == 1
        assert result.user_id == 123
        assert result.first_name == "Updated John"
        assert result.last_name == "Updated Doe"
        assert result.email == "updated.john@example.com"
        
        # Verify database operations
        # Note: update_employee_full doesn't use db.add() for existing records
        assert mock_db.commit.call_count == 1
        assert mock_db.refresh.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_update_employee_full_not_found(self):
        """Test update non-existent employee."""
        # Arrange
        mock_db = AsyncMock(spec=AsyncSession)
        current_user = MagicMock(spec=User)
        current_user.id = 123
        
        # Mock no employee found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        employee_data = EmployeeFullRequest(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="(555) 123-4567",
            join_date=date(2024, 1, 15)
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await EmployeeService.update_employee_full(
                db=mock_db,
                employee_id=999,
                employee_data=employee_data,
                current_user=current_user
            )
        
        assert "Employee not found or access denied" in str(exc_info.value)
