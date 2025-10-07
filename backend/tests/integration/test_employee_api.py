"""
Integration tests for employee API endpoints.

Tests complete request/response cycles with real database operations.
Verifies authentication, validation, business rules, and error handling
in realistic scenarios using FastAPI TestClient.

Following FastAPI testing documentation:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timezone

from tests.conftest import OnboardingDataFactory


class EmployeeDataFactory:
    """Factory for creating consistent employee test data."""
    
    @staticmethod
    def valid_employee_data(email: str = "john.doe@example.com") -> dict:
        """Create valid employee data for testing."""
        return {
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15"
        }
    
    @staticmethod
    def invalid_employee_data() -> dict:
        """Create invalid employee data for validation testing."""
        return {
            "first_name": "",  # Too short
            "last_name": "Doe123",  # Invalid characters
            "email": "invalid-email",  # Invalid format
            "phone": "123",  # Too short
            "join_date": "invalid-date"  # Invalid format
        }
    
    @staticmethod
    def valid_personal_details_data() -> dict:
        """Create valid personal details data for testing."""
        return {
            "gender": "MALE",
            "date_of_birth": "1990-01-15",
            "nationality": "American",
            "health_care_provider": "Blue Cross",
            "marital_status": "SINGLE",
            "personal_tax_id": "123-45-6789",
            "social_insurance_number": "123456789",
            "primary_address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10001"
        }
    
    @staticmethod
    def valid_job_timeline_data() -> dict:
        """Create valid job timeline data for testing."""
        return {
            "effective_date": "2024-01-15",
            "end_date": "2024-12-31",
            "job_title": "Software Engineer",
            "position_type": "Individual Contributor",
            "employment_type": "FULL_TIME",
            "line_manager_id": 123,
            "department": "Engineering",
            "office": "New York",
            "is_current": True
        }
    
    @staticmethod
    def valid_bank_info_data() -> dict:
        """Create valid bank info data for testing."""
        return {
            "bank_name": "Chase Bank",
            "account_number": "1234567890",
            "routing_number": "021000021",
            "account_type": "CHECKING",
            "account_holder_name": "John Doe",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": True,
            "is_active": True
        }
    
    @staticmethod
    def valid_dependent_data() -> dict:
        """Create valid dependent data for testing."""
        return {
            "name": "Jane Doe",
            "relationship_type": "SPOUSE",
            "date_of_birth": "1992-05-20",
            "gender": "FEMALE",
            "nationality": "American",
            "primary_address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10001",
            "is_active": True
        }
    
    @staticmethod
    def valid_document_data() -> dict:
        """Create valid document data for testing."""
        return {
            "document_type": "PASSPORT",
            "file_name": "passport.pdf",
            "file_path": "/uploads/passport_123.pdf",
            "file_size": 1024000,
            "mime_type": "application/pdf",
            "is_active": True
        }
    
    @staticmethod
    def valid_full_employee_data(email: str = "john.doe@example.com") -> dict:
        """Create valid full employee data for testing."""
        return {
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15",
            "personal_details": EmployeeDataFactory.valid_personal_details_data(),
            "bank_info": EmployeeDataFactory.valid_bank_info_data(),
            "job_timeline": [EmployeeDataFactory.valid_job_timeline_data()],
            "dependents": [EmployeeDataFactory.valid_dependent_data()],
            "documents": [EmployeeDataFactory.valid_document_data()]
        }


class TestEmployeeBasicEndpoints:
    """Test basic employee CRUD endpoints."""
    
    def test_create_employee_requires_authentication(self, client: TestClient):
        """Test that create employee endpoint requires authentication."""
        data = EmployeeDataFactory.valid_employee_data()
        
        response = client.post("/api/v1/employee", json=data)
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_create_employee_success(self, client: TestClient, auth_headers: dict):
        """Test successful employee creation."""
        data = EmployeeDataFactory.valid_employee_data("new.employee@example.com")
        
        response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        
        # Verify response structure
        assert response_data["id"] > 0
        assert response_data["user_id"] > 0
        assert response_data["first_name"] == "John"
        assert response_data["last_name"] == "Doe"
        assert response_data["email"] == "new.employee@example.com"
        assert response_data["phone"] == "(555) 123-4567"
        assert response_data["join_date"] == "2024-01-15"
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    def test_create_employee_validation_errors(self, client: TestClient, auth_headers: dict):
        """Test validation errors with invalid data."""
        invalid_data = EmployeeDataFactory.invalid_employee_data()
        
        response = client.post("/api/v1/employee", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
        error_data = response.json()
        
        assert "detail" in error_data
        # Should have multiple validation errors
        assert len(error_data["detail"]) > 0
    
    def test_create_employee_duplicate_email(self, client: TestClient, auth_headers: dict):
        """Test duplicate email prevention."""
        data = EmployeeDataFactory.valid_employee_data("duplicate@example.com")
        
        # First creation should succeed
        response1 = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert response1.status_code == 201
        
        # Second creation should fail
        data2 = EmployeeDataFactory.valid_employee_data("duplicate@example.com")
        response2 = client.post("/api/v1/employee", json=data2, headers=auth_headers)
        
        assert response2.status_code == 400
        error_data = response2.json()
        assert "Email already exists" in error_data["detail"]
    
    def test_list_employees_requires_authentication(self, client: TestClient):
        """Test that list employees endpoint requires authentication."""
        response = client.get("/api/v1/employee")
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_list_employees_success(self, client: TestClient, auth_headers: dict):
        """Test successful employee listing."""
        # First create an employee
        data = EmployeeDataFactory.valid_employee_data("list.test@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        
        # Then list employees
        response = client.get("/api/v1/employee", headers=auth_headers)
        
        assert response.status_code == 200
        employees = response.json()
        
        assert isinstance(employees, list)
        assert len(employees) >= 1
        
        # Verify the created employee is in the list
        employee_emails = [emp["email"] for emp in employees]
        assert "list.test@example.com" in employee_emails
    
    def test_get_employee_requires_authentication(self, client: TestClient):
        """Test that get employee endpoint requires authentication."""
        response = client.get("/api/v1/employee/1")
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_get_employee_success(self, client: TestClient, auth_headers: dict):
        """Test successful employee retrieval."""
        # First create an employee
        data = EmployeeDataFactory.valid_employee_data("get.test@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/employee/{employee_id}", headers=auth_headers)
        
        assert response.status_code == 200
        employee_data = response.json()
        
        assert employee_data["id"] == employee_id
        assert employee_data["first_name"] == "John"
        assert employee_data["email"] == "get.test@example.com"
    
    def test_get_employee_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent employee."""
        response = client.get("/api/v1/employee/99999", headers=auth_headers)
        
        assert response.status_code == 404
        error_data = response.json()
        assert "Employee not found" in error_data["detail"]


class TestEmployeePersonalDetailsEndpoints:
    """Test employee personal details endpoints."""
    
    def test_create_personal_details_requires_authentication(self, client: TestClient):
        """Test that personal details endpoint requires authentication."""
        data = EmployeeDataFactory.valid_personal_details_data()
        
        response = client.post("/api/v1/employee/1/personal", json=data)
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_create_personal_details_success(self, client: TestClient, auth_headers: dict):
        """Test successful personal details creation."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("personal.test@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Then add personal details
        personal_data = EmployeeDataFactory.valid_personal_details_data()
        response = client.post(f"/api/v1/employee/{employee_id}/personal", json=personal_data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["id"] > 0
        assert response_data["employee_id"] == employee_id
        assert response_data["gender"] == "MALE"
        assert response_data["nationality"] == "American"
        assert response_data["marital_status"] == "SINGLE"
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    def test_create_personal_details_employee_not_found(self, client: TestClient, auth_headers: dict):
        """Test personal details creation for non-existent employee."""
        personal_data = EmployeeDataFactory.valid_personal_details_data()
        
        response = client.post("/api/v1/employee/99999/personal", json=personal_data, headers=auth_headers)
        
        assert response.status_code == 400
        error_data = response.json()
        assert "Employee not found or access denied" in error_data["detail"]
    
    def test_create_personal_details_validation_errors(self, client: TestClient, auth_headers: dict):
        """Test validation errors with invalid personal details data."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("validation.test@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Invalid personal details data
        invalid_data = {
            "gender": "INVALID_GENDER",  # Invalid enum value
            "marital_status": "INVALID_STATUS",  # Invalid enum value
            "date_of_birth": "invalid-date"  # Invalid date format
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/personal", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data


class TestEmployeeJobTimelineEndpoints:
    """Test employee job timeline endpoints."""
    
    def test_create_job_timeline_requires_authentication(self, client: TestClient):
        """Test that job timeline endpoint requires authentication."""
        data = EmployeeDataFactory.valid_job_timeline_data()
        
        response = client.post("/api/v1/employee/1/job", json=data)
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_create_job_timeline_success(self, client: TestClient, auth_headers: dict):
        """Test successful job timeline creation."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("job.test@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Then add job timeline
        job_data = EmployeeDataFactory.valid_job_timeline_data()
        response = client.post(f"/api/v1/employee/{employee_id}/job", json=job_data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["id"] > 0
        assert response_data["employee_id"] == employee_id
        assert response_data["job_title"] == "Software Engineer"
        assert response_data["employment_type"] == "FULL_TIME"
        assert response_data["is_current"] is True
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    def test_create_job_timeline_validation_errors(self, client: TestClient, auth_headers: dict):
        """Test validation errors with invalid job timeline data."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("job.validation@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Invalid job timeline data
        invalid_data = {
            "effective_date": "invalid-date",  # Invalid date format
            "job_title": "",  # Empty required field
            "employment_type": "INVALID_TYPE",  # Invalid enum value
            "department": "",  # Empty required field
            "office": ""  # Empty required field
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/job", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data


class TestEmployeeBankInfoEndpoints:
    """Test employee bank info endpoints."""
    
    def test_create_bank_info_requires_authentication(self, client: TestClient):
        """Test that bank info endpoint requires authentication."""
        data = EmployeeDataFactory.valid_bank_info_data()
        
        response = client.post("/api/v1/employee/1/bank", json=data)
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_create_bank_info_success(self, client: TestClient, auth_headers: dict):
        """Test successful bank info creation."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("bank.test@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Then add bank info
        bank_data = EmployeeDataFactory.valid_bank_info_data()
        response = client.post(f"/api/v1/employee/{employee_id}/bank", json=bank_data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["id"] > 0
        assert response_data["employee_id"] == employee_id
        assert response_data["bank_name"] == "Chase Bank"
        assert response_data["account_number"] == "1234567890"
        assert response_data["is_primary"] is True
        assert response_data["is_active"] is True
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    def test_create_bank_info_duplicate(self, client: TestClient, auth_headers: dict):
        """Test duplicate bank info prevention."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("bank.duplicate@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # First bank info creation should succeed
        bank_data = EmployeeDataFactory.valid_bank_info_data()
        response1 = client.post(f"/api/v1/employee/{employee_id}/bank", json=bank_data, headers=auth_headers)
        assert response1.status_code == 201
        
        # Second bank info creation should fail
        response2 = client.post(f"/api/v1/employee/{employee_id}/bank", json=bank_data, headers=auth_headers)
        
        assert response2.status_code == 400
        error_data = response2.json()
        assert "Bank info already exists for this employee" in error_data["detail"]


class TestEmployeeDependentEndpoints:
    """Test employee dependent endpoints."""
    
    def test_create_dependent_requires_authentication(self, client: TestClient):
        """Test that dependent endpoint requires authentication."""
        data = EmployeeDataFactory.valid_dependent_data()
        
        response = client.post("/api/v1/employee/1/dependent", json=data)
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_create_dependent_success(self, client: TestClient, auth_headers: dict):
        """Test successful dependent creation."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.test@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Then add dependent
        dependent_data = EmployeeDataFactory.valid_dependent_data()
        response = client.post(f"/api/v1/employee/{employee_id}/dependent", json=dependent_data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["id"] > 0
        assert response_data["employee_id"] == employee_id
        assert response_data["name"] == "Jane Doe"
        assert response_data["relationship_type"] == "SPOUSE"
        assert response_data["is_active"] is True
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    def test_create_dependent_validation_errors(self, client: TestClient, auth_headers: dict):
        """Test validation errors with invalid dependent data."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.validation@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Invalid dependent data
        invalid_data = {
            "name": "",  # Empty required field
            "relationship_type": "INVALID_TYPE",  # Invalid enum value
            "date_of_birth": "invalid-date"  # Invalid date format
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/dependent", json=invalid_data, headers=auth_headers)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data


class TestEmployeeDocumentEndpoints:
    """Test employee document endpoints."""
    
    def test_create_document_requires_authentication(self, client: TestClient):
        """Test that document endpoint requires authentication."""
        data = EmployeeDataFactory.valid_document_data()
        
        response = client.post("/api/v1/employee/1/document", json=data)
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_create_document_success(self, client: TestClient, auth_headers: dict):
        """Test successful document creation."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("document.test@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Then add document
        document_data = EmployeeDataFactory.valid_document_data()
        response = client.post(f"/api/v1/employee/{employee_id}/document", json=document_data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["id"] > 0
        assert response_data["employee_id"] == employee_id
        assert response_data["document_type"] == "PASSPORT"
        assert response_data["file_name"] == "passport.pdf"
        assert response_data["file_size"] == 1024000
        assert response_data["is_active"] is True
        assert "upload_date" in response_data
        assert "uploaded_by_user_id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data


class TestEmployeeFullEndpoints:
    """Test employee full operations endpoints."""
    
    def test_create_employee_full_requires_authentication(self, client: TestClient):
        """Test that create employee full endpoint requires authentication."""
        data = EmployeeDataFactory.valid_full_employee_data()
        
        response = client.post("/api/v1/employee/full", json=data)
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_create_employee_full_success(self, client: TestClient, auth_headers: dict):
        """Test successful full employee creation."""
        data = EmployeeDataFactory.valid_full_employee_data("full.test@example.com")
        
        response = client.post("/api/v1/employee/full", json=data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        
        # Verify basic employee info
        assert response_data["id"] > 0
        assert response_data["user_id"] > 0
        assert response_data["first_name"] == "John"
        assert response_data["last_name"] == "Doe"
        assert response_data["email"] == "full.test@example.com"
        
        # Verify related data
        assert response_data["personal_details"] is not None
        assert response_data["personal_details"]["gender"] == "MALE"
        assert response_data["bank_info"] is not None
        assert response_data["bank_info"]["bank_name"] == "Chase Bank"
        assert len(response_data["job_timeline"]) == 1
        assert response_data["job_timeline"][0]["job_title"] == "Software Engineer"
        assert len(response_data["dependents"]) == 1
        assert response_data["dependents"][0]["name"] == "Jane Doe"
        assert len(response_data["documents"]) == 1
        assert response_data["documents"][0]["document_type"] == "PASSPORT"
    
    def test_create_employee_full_minimal(self, client: TestClient, auth_headers: dict):
        """Test full employee creation with only basic info."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "minimal.test@example.com",
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15"
        }
        
        response = client.post("/api/v1/employee/full", json=data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["id"] > 0
        assert response_data["first_name"] == "John"
        assert response_data["email"] == "minimal.test@example.com"
        assert response_data["personal_details"] is None
        assert response_data["bank_info"] is None
        assert response_data["job_timeline"] == []
        assert response_data["dependents"] == []
        assert response_data["documents"] == []
    
    def test_get_employee_full_requires_authentication(self, client: TestClient):
        """Test that get employee full endpoint requires authentication."""
        response = client.get("/api/v1/employee/1/full")
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_get_employee_full_success(self, client: TestClient, auth_headers: dict):
        """Test successful full employee retrieval."""
        # First create a full employee
        data = EmployeeDataFactory.valid_full_employee_data("get.full@example.com")
        create_response = client.post("/api/v1/employee/full", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/employee/{employee_id}/full", headers=auth_headers)
        
        assert response.status_code == 200
        employee_data = response.json()
        
        assert employee_data["id"] == employee_id
        assert employee_data["first_name"] == "John"
        assert employee_data["email"] == "get.full@example.com"
        assert employee_data["personal_details"] is not None
        assert employee_data["bank_info"] is not None
        assert len(employee_data["job_timeline"]) == 1
        assert len(employee_data["dependents"]) == 1
        assert len(employee_data["documents"]) == 1
    
    def test_update_employee_full_requires_authentication(self, client: TestClient):
        """Test that update employee full endpoint requires authentication."""
        data = EmployeeDataFactory.valid_full_employee_data()
        
        response = client.put("/api/v1/employee/1/full", json=data)
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_update_employee_full_success(self, client: TestClient, auth_headers: dict):
        """Test successful full employee update."""
        # First create a full employee
        data = EmployeeDataFactory.valid_full_employee_data("update.full@example.com")
        create_response = client.post("/api/v1/employee/full", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Then update it
        updated_data = EmployeeDataFactory.valid_full_employee_data("updated.full@example.com")
        updated_data["first_name"] = "Updated John"
        updated_data["personal_details"]["nationality"] = "Canadian"
        
        response = client.put(f"/api/v1/employee/{employee_id}/full", json=updated_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data["id"] == employee_id
        assert response_data["first_name"] == "Updated John"
        assert response_data["email"] == "updated.full@example.com"
        assert response_data["personal_details"]["nationality"] == "Canadian"
    
    def test_update_employee_full_not_found(self, client: TestClient, auth_headers: dict):
        """Test update non-existent employee."""
        data = EmployeeDataFactory.valid_full_employee_data()
        
        response = client.put("/api/v1/employee/99999/full", json=data, headers=auth_headers)
        
        assert response.status_code == 400
        error_data = response.json()
        assert "Employee not found or access denied" in error_data["detail"]


class TestEmployeeEndToEnd:
    """End-to-end integration tests for complete employee flow."""
    
    def test_complete_employee_management_flow(self, client: TestClient, auth_headers: dict):
        """Test complete employee management flow from creation to full details."""
        # 1. Create basic employee
        basic_data = EmployeeDataFactory.valid_employee_data("e2e.test@example.com")
        create_response = client.post("/api/v1/employee", json=basic_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # 2. Add personal details
        personal_data = EmployeeDataFactory.valid_personal_details_data()
        personal_response = client.post(f"/api/v1/employee/{employee_id}/personal", json=personal_data, headers=auth_headers)
        assert personal_response.status_code == 201
        
        # 3. Add job timeline
        job_data = EmployeeDataFactory.valid_job_timeline_data()
        job_response = client.post(f"/api/v1/employee/{employee_id}/job", json=job_data, headers=auth_headers)
        assert job_response.status_code == 201
        
        # 4. Add bank info
        bank_data = EmployeeDataFactory.valid_bank_info_data()
        bank_response = client.post(f"/api/v1/employee/{employee_id}/bank", json=bank_data, headers=auth_headers)
        assert bank_response.status_code == 201
        
        # 5. Add dependent
        dependent_data = EmployeeDataFactory.valid_dependent_data()
        dependent_response = client.post(f"/api/v1/employee/{employee_id}/dependent", json=dependent_data, headers=auth_headers)
        assert dependent_response.status_code == 201
        
        # 6. Add document
        document_data = EmployeeDataFactory.valid_document_data()
        document_response = client.post(f"/api/v1/employee/{employee_id}/document", json=document_data, headers=auth_headers)
        assert document_response.status_code == 201
        
        # 7. Get full employee details
        full_response = client.get(f"/api/v1/employee/{employee_id}/full", headers=auth_headers)
        assert full_response.status_code == 200
        full_data = full_response.json()
        
        # Verify all data is present
        assert full_data["id"] == employee_id
        assert full_data["personal_details"] is not None
        assert full_data["bank_info"] is not None
        assert len(full_data["job_timeline"]) == 1
        assert len(full_data["dependents"]) == 1
        assert len(full_data["documents"]) == 1
        
        # 8. Update full employee
        updated_data = EmployeeDataFactory.valid_full_employee_data("e2e.updated@example.com")
        updated_data["first_name"] = "Updated John"
        update_response = client.put(f"/api/v1/employee/{employee_id}/full", json=updated_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        # 9. Verify update
        verify_response = client.get(f"/api/v1/employee/{employee_id}/full", headers=auth_headers)
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["first_name"] == "Updated John"
        assert verify_data["email"] == "e2e.updated@example.com"
    
    @pytest.mark.asyncio
    async def test_employee_isolation_between_users(self, client: TestClient, auth_headers: dict, shared_db_session):
        """Test that employees are properly isolated between users."""
        # Create employee for first user
        data1 = EmployeeDataFactory.valid_employee_data("user1@example.com")
        response1 = client.post("/api/v1/employee", json=data1, headers=auth_headers)
        assert response1.status_code == 201
        employee_id = response1.json()["id"]
        
        # Create second user
        from schemas.user import UserCreate
        from services.user_service import UserService
        
        user_data2 = UserCreate(
            email="user2@example.com",
            password="testpassword123",
            first_name="User",
            last_name="Two"
        )
        user2 = await UserService.create_user_with_verification(
            shared_db_session,
            user_data2,
            is_verified=True
        )
        await shared_db_session.refresh(user2)
        
        # Generate auth token for second user
        from schemas.auth import LoginRequest
        from services.auth_service import AuthService
        login_data2 = LoginRequest(email=user2.email, password="testpassword123")
        token_response2 = await AuthService.login(shared_db_session, login_data2)
        
        auth_headers2 = {
            "Authorization": f"Bearer {token_response2.access_token}",
            "Content-Type": "application/json"
        }
        
        # Second user should not see first user's employee
        response2 = client.get(f"/api/v1/employee/{employee_id}", headers=auth_headers2)
        assert response2.status_code == 404
        
        # Second user should not see first user's employees in list
        list_response = client.get("/api/v1/employee", headers=auth_headers2)
        assert list_response.status_code == 200
        employees = list_response.json()
        assert len(employees) == 0
        
        # Second user should not be able to access first user's employee full details
        full_response = client.get(f"/api/v1/employee/{employee_id}/full", headers=auth_headers2)
        assert full_response.status_code == 404
