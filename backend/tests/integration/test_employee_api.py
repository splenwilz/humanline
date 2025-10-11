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
            "line_manager_id": None,
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

    def test_update_employee_success(self, client: TestClient, auth_headers: dict):
        """Test successful employee update."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("update.test@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Update the employee
        updated_data = EmployeeDataFactory.valid_employee_data("updated.test@example.com")
        updated_data["first_name"] = "Jane"
        updated_data["last_name"] = "Smith"
        updated_data["phone"] = "(555) 999-8888"
        
        update_response = client.put(f"/api/v1/employee/{employee_id}", json=updated_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        updated_employee = update_response.json()
        assert updated_employee["id"] == employee_id
        assert updated_employee["first_name"] == "Jane"
        assert updated_employee["last_name"] == "Smith"
        assert updated_employee["email"] == "updated.test@example.com"
        assert updated_employee["phone"] == "(555) 999-8888"
        
        # Verify updated_at timestamp changed
        assert updated_employee["updated_at"] != create_response.json()["updated_at"]

    def test_update_employee_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating a non-existent employee."""
        updated_data = EmployeeDataFactory.valid_employee_data("notfound.update@example.com")
        response = client.put("/api/v1/employee/99999", json=updated_data, headers=auth_headers)
        assert response.status_code == 404
        assert "Employee not found or access denied" in response.json()["detail"]

    def test_partial_update_employee_success(self, client: TestClient, auth_headers: dict):
        """Test successful partial employee update."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("partial.update@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Partially update the employee (only phone)
        partial_data = {
            "first_name": "John",  # Keep same
            "last_name": "Doe",  # Keep same
            "email": "partial.update@example.com",  # Keep same
            "phone": "(555) 777-6666",  # Update this
            "join_date": "2024-01-15"  # Keep same
        }
        
        patch_response = client.patch(f"/api/v1/employee/{employee_id}", json=partial_data, headers=auth_headers)
        assert patch_response.status_code == 200
        
        updated_employee = patch_response.json()
        assert updated_employee["id"] == employee_id
        assert updated_employee["first_name"] == "John"  # Unchanged
        assert updated_employee["phone"] == "(555) 777-6666"  # Updated
        
        # Verify updated_at timestamp changed
        assert updated_employee["updated_at"] != create_response.json()["updated_at"]

    def test_partial_update_employee_not_found(self, client: TestClient, auth_headers: dict):
        """Test partial updating a non-existent employee."""
        partial_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "notfound.partial@example.com",
            "phone": "(555) 777-6666",
            "join_date": "2024-01-15"
        }
        response = client.patch("/api/v1/employee/99999", json=partial_data, headers=auth_headers)
        assert response.status_code == 404
        assert "Employee not found or access denied" in response.json()["detail"]

    def test_delete_employee_success(self, client: TestClient, auth_headers: dict):
        """Test successful employee deletion."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("delete.test@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Delete the employee
        delete_response = client.delete(f"/api/v1/employee/{employee_id}", headers=auth_headers)
        assert delete_response.status_code == 204
        
        # Verify employee was deleted
        get_response = client.get(f"/api/v1/employee/{employee_id}", headers=auth_headers)
        assert get_response.status_code == 404
        assert "Employee not found or access denied" in get_response.json()["detail"]

    def test_delete_employee_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting a non-existent employee."""
        response = client.delete("/api/v1/employee/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "Employee not found or access denied" in response.json()["detail"]

    def test_employee_crud_workflow(self, client: TestClient, auth_headers: dict):
        """Test complete CRUD workflow for employees."""
        # 1. CREATE - Add an employee
        employee_data = EmployeeDataFactory.valid_employee_data("workflow.test@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # 2. READ - Get the employee
        get_response = client.get(f"/api/v1/employee/{employee_id}", headers=auth_headers)
        assert get_response.status_code == 200
        employee = get_response.json()
        assert employee["email"] == "workflow.test@example.com"
        
        # 3. UPDATE - Full update
        updated_data = EmployeeDataFactory.valid_employee_data("workflow.updated@example.com")
        updated_data["first_name"] = "Jane"
        updated_data["last_name"] = "Smith"
        
        update_response = client.put(f"/api/v1/employee/{employee_id}", json=updated_data, headers=auth_headers)
        assert update_response.status_code == 200
        updated_employee = update_response.json()
        assert updated_employee["first_name"] == "Jane"
        assert updated_employee["email"] == "workflow.updated@example.com"
        
        # 4. UPDATE - Partial update
        partial_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "workflow.updated@example.com",
            "phone": "(555) 888-7777",
            "join_date": "2024-01-15"
        }
        
        patch_response = client.patch(f"/api/v1/employee/{employee_id}", json=partial_data, headers=auth_headers)
        assert patch_response.status_code == 200
        patched_employee = patch_response.json()
        assert patched_employee["phone"] == "(555) 888-7777"
        
        # 5. DELETE - Remove employee
        delete_response = client.delete(f"/api/v1/employee/{employee_id}", headers=auth_headers)
        assert delete_response.status_code == 204
        
        # 6. Verify deletion
        get_response = client.get(f"/api/v1/employee/{employee_id}", headers=auth_headers)
        assert get_response.status_code == 404


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
        assert response_data["account_number"] == "******7890"
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

    def test_get_dependents_success(self, client: TestClient, auth_headers: dict):
        """Test successful retrieval of all dependents for an employee."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependents.list@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create multiple dependents
        dependent1_data = EmployeeDataFactory.valid_dependent_data()
        dependent1_data["name"] = "Alice Johnson"
        dependent1_data["relationship_type"] = "SPOUSE"
        
        dependent2_data = EmployeeDataFactory.valid_dependent_data()
        dependent2_data["name"] = "Bob Johnson"
        dependent2_data["relationship_type"] = "CHILD"
        
        # Create first dependent
        response1 = client.post(f"/api/v1/employee/{employee_id}/dependent", json=dependent1_data, headers=auth_headers)
        assert response1.status_code == 201
        
        # Create second dependent
        response2 = client.post(f"/api/v1/employee/{employee_id}/dependent", json=dependent2_data, headers=auth_headers)
        assert response2.status_code == 201
        
        # Get all dependents
        get_response = client.get(f"/api/v1/employee/{employee_id}/dependent", headers=auth_headers)
        assert get_response.status_code == 200
        
        dependents = get_response.json()
        assert len(dependents) == 2
        
        # Check that dependents are ordered by creation date (newest first)
        assert dependents[0]["name"] == "Bob Johnson"  # Created second
        assert dependents[1]["name"] == "Alice Johnson"  # Created first
        
        # Verify dependent data
        for dependent in dependents:
            assert dependent["employee_id"] == employee_id
            assert dependent["is_active"] is True
            assert "created_at" in dependent
            assert "updated_at" in dependent

    def test_get_dependents_empty_list(self, client: TestClient, auth_headers: dict):
        """Test getting dependents when none exist."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependents.empty@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Get dependents (should be empty)
        get_response = client.get(f"/api/v1/employee/{employee_id}/dependent", headers=auth_headers)
        assert get_response.status_code == 200
        
        dependents = get_response.json()
        assert dependents == []

    def test_get_dependents_employee_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting dependents for non-existent employee."""
        response = client.get("/api/v1/employee/99999/dependent", headers=auth_headers)
        assert response.status_code == 404
        assert "Employee not found or access denied" in response.json()["detail"]

    def test_get_dependent_success(self, client: TestClient, auth_headers: dict):
        """Test successful retrieval of a specific dependent."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.get@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create a dependent
        dependent_data = EmployeeDataFactory.valid_dependent_data()
        dependent_data["name"] = "Alice Johnson"
        dependent_data["relationship_type"] = "SPOUSE"
        
        create_dependent_response = client.post(f"/api/v1/employee/{employee_id}/dependent", json=dependent_data, headers=auth_headers)
        assert create_dependent_response.status_code == 201
        dependent_id = create_dependent_response.json()["id"]
        
        # Get the specific dependent
        get_response = client.get(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        dependent = get_response.json()
        assert dependent["id"] == dependent_id
        assert dependent["employee_id"] == employee_id
        assert dependent["name"] == "Alice Johnson"
        assert dependent["relationship_type"] == "SPOUSE"
        assert dependent["is_active"] is True

    def test_get_dependent_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting a non-existent dependent."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.notfound@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Try to get non-existent dependent
        response = client.get(f"/api/v1/employee/{employee_id}/dependent/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "Dependent not found" in response.json()["detail"]

    def test_update_dependent_success(self, client: TestClient, auth_headers: dict):
        """Test successful dependent update."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.update@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create a dependent
        dependent_data = EmployeeDataFactory.valid_dependent_data()
        dependent_data["name"] = "Alice Johnson"
        dependent_data["relationship_type"] = "SPOUSE"
        dependent_data["nationality"] = "American"
        dependent_data["city"] = "New York"
        
        create_dependent_response = client.post(f"/api/v1/employee/{employee_id}/dependent", json=dependent_data, headers=auth_headers)
        assert create_dependent_response.status_code == 201
        dependent_id = create_dependent_response.json()["id"]
        
        # Update the dependent
        updated_data = EmployeeDataFactory.valid_dependent_data()
        updated_data["name"] = "Alice Johnson-Smith"
        updated_data["relationship_type"] = "SPOUSE"
        updated_data["nationality"] = "Canadian"
        updated_data["city"] = "Boston"
        updated_data["state"] = "MA"
        updated_data["postal_code"] = "02101"
        
        update_response = client.put(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", json=updated_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        updated_dependent = update_response.json()
        assert updated_dependent["id"] == dependent_id
        assert updated_dependent["name"] == "Alice Johnson-Smith"
        assert updated_dependent["nationality"] == "Canadian"
        assert updated_dependent["city"] == "Boston"
        assert updated_dependent["state"] == "MA"
        assert updated_dependent["postal_code"] == "02101"
        
        # Verify updated_at timestamp changed
        assert updated_dependent["updated_at"] != create_dependent_response.json()["updated_at"]

    def test_update_dependent_not_found(self, client: TestClient, auth_headers: dict):
        """Test updating a non-existent dependent."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.update.notfound@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Try to update non-existent dependent
        updated_data = EmployeeDataFactory.valid_dependent_data()
        response = client.put(f"/api/v1/employee/{employee_id}/dependent/99999", json=updated_data, headers=auth_headers)
        assert response.status_code == 404
        assert "Dependent not found" in response.json()["detail"]

    def test_partial_update_dependent_success(self, client: TestClient, auth_headers: dict):
        """Test successful partial dependent update."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.patch@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create a dependent
        dependent_data = EmployeeDataFactory.valid_dependent_data()
        dependent_data["name"] = "Alice Johnson"
        dependent_data["relationship_type"] = "SPOUSE"
        dependent_data["nationality"] = "American"
        dependent_data["city"] = "New York"
        
        create_dependent_response = client.post(f"/api/v1/employee/{employee_id}/dependent", json=dependent_data, headers=auth_headers)
        assert create_dependent_response.status_code == 201
        dependent_id = create_dependent_response.json()["id"]
        
        # Partially update the dependent (only nationality)
        partial_data = {
            "name": "Alice Johnson",  # Keep same
            "relationship_type": "SPOUSE",  # Keep same
            "nationality": "Canadian"  # Update this
        }
        
        patch_response = client.patch(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", json=partial_data, headers=auth_headers)
        assert patch_response.status_code == 200
        
        updated_dependent = patch_response.json()
        assert updated_dependent["id"] == dependent_id
        assert updated_dependent["name"] == "Alice Johnson"  # Unchanged
        assert updated_dependent["nationality"] == "Canadian"  # Updated
        assert updated_dependent["city"] == "New York"  # Unchanged
        
        # Verify updated_at timestamp changed
        assert updated_dependent["updated_at"] != create_dependent_response.json()["updated_at"]

    def test_partial_update_dependent_not_found(self, client: TestClient, auth_headers: dict):
        """Test partial updating a non-existent dependent."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.patch.notfound@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Try to partially update non-existent dependent
        partial_data = {
            "name": "Alice Johnson",
            "relationship_type": "SPOUSE",
            "nationality": "Canadian"
        }
        response = client.patch(f"/api/v1/employee/{employee_id}/dependent/99999", json=partial_data, headers=auth_headers)
        assert response.status_code == 404
        assert "Dependent not found" in response.json()["detail"]

    def test_delete_dependent_success(self, client: TestClient, auth_headers: dict):
        """Test successful dependent deletion."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.delete@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create a dependent
        dependent_data = EmployeeDataFactory.valid_dependent_data()
        create_dependent_response = client.post(f"/api/v1/employee/{employee_id}/dependent", json=dependent_data, headers=auth_headers)
        assert create_dependent_response.status_code == 201
        dependent_id = create_dependent_response.json()["id"]
        
        # Delete the dependent
        delete_response = client.delete(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", headers=auth_headers)
        assert delete_response.status_code == 204
        
        # Verify dependent was deleted
        get_response = client.get(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", headers=auth_headers)
        assert get_response.status_code == 404
        assert "Dependent not found" in get_response.json()["detail"]
        
        # Verify dependent is not in the list
        list_response = client.get(f"/api/v1/employee/{employee_id}/dependent", headers=auth_headers)
        assert list_response.status_code == 200
        dependents = list_response.json()
        assert dependents == []

    def test_delete_dependent_not_found(self, client: TestClient, auth_headers: dict):
        """Test deleting a non-existent dependent."""
        # First create an employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.delete.notfound@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Try to delete non-existent dependent
        response = client.delete(f"/api/v1/employee/{employee_id}/dependent/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "Dependent not found" in response.json()["detail"]

    def test_dependent_endpoints_require_authentication(self, client: TestClient):
        """Test that all dependent endpoints require authentication."""
        # Test GET all dependents
        response = client.get("/api/v1/employee/1/dependent")
        assert response.status_code == 403
        
        # Test GET specific dependent
        response = client.get("/api/v1/employee/1/dependent/1")
        assert response.status_code == 403
        
        # Test PUT update dependent
        response = client.put("/api/v1/employee/1/dependent/1", json=EmployeeDataFactory.valid_dependent_data())
        assert response.status_code == 403
        
        # Test PATCH partial update dependent
        response = client.patch("/api/v1/employee/1/dependent/1", json=EmployeeDataFactory.valid_dependent_data())
        assert response.status_code == 403
        
        # Test DELETE dependent
        response = client.delete("/api/v1/employee/1/dependent/1")
        assert response.status_code == 403

    def test_dependent_crud_workflow(self, client: TestClient, auth_headers: dict):
        """Test complete CRUD workflow for dependents."""
        # Create employee
        employee_data = EmployeeDataFactory.valid_employee_data("dependent.workflow@example.com")
        create_response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # 1. CREATE - Add a dependent
        dependent_data = EmployeeDataFactory.valid_dependent_data()
        dependent_data["name"] = "Alice Johnson"
        dependent_data["relationship_type"] = "SPOUSE"
        
        create_response = client.post(f"/api/v1/employee/{employee_id}/dependent", json=dependent_data, headers=auth_headers)
        assert create_response.status_code == 201
        dependent_id = create_response.json()["id"]
        
        # 2. READ - Get all dependents
        list_response = client.get(f"/api/v1/employee/{employee_id}/dependent", headers=auth_headers)
        assert list_response.status_code == 200
        dependents = list_response.json()
        assert len(dependents) == 1
        assert dependents[0]["name"] == "Alice Johnson"
        
        # 3. READ - Get specific dependent
        get_response = client.get(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", headers=auth_headers)
        assert get_response.status_code == 200
        dependent = get_response.json()
        assert dependent["name"] == "Alice Johnson"
        
        # 4. UPDATE - Full update
        updated_data = EmployeeDataFactory.valid_dependent_data()
        updated_data["name"] = "Alice Johnson-Smith"
        updated_data["relationship_type"] = "SPOUSE"
        updated_data["nationality"] = "Canadian"
        
        update_response = client.put(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", json=updated_data, headers=auth_headers)
        assert update_response.status_code == 200
        updated_dependent = update_response.json()
        assert updated_dependent["name"] == "Alice Johnson-Smith"
        assert updated_dependent["nationality"] == "Canadian"
        
        # 5. UPDATE - Partial update
        partial_data = {
            "name": "Alice Johnson-Smith",
            "relationship_type": "SPOUSE",
            "city": "Boston"
        }
        
        patch_response = client.patch(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", json=partial_data, headers=auth_headers)
        assert patch_response.status_code == 200
        patched_dependent = patch_response.json()
        assert patched_dependent["city"] == "Boston"
        assert patched_dependent["nationality"] == "Canadian"  # Should remain unchanged
        
        # 6. DELETE - Remove dependent
        delete_response = client.delete(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", headers=auth_headers)
        assert delete_response.status_code == 204
        
        # 7. Verify deletion
        get_response = client.get(f"/api/v1/employee/{employee_id}/dependent/{dependent_id}", headers=auth_headers)
        assert get_response.status_code == 404
        
        list_response = client.get(f"/api/v1/employee/{employee_id}/dependent", headers=auth_headers)
        assert list_response.status_code == 200
        dependents = list_response.json()
        assert dependents == []


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

    @pytest.mark.asyncio
    async def test_line_manager_id_tenant_isolation(self, client: TestClient, auth_headers: dict, shared_db_session):
        """Test that line_manager_id validation enforces tenant isolation."""
        # Create employee for first user
        data1 = EmployeeDataFactory.valid_employee_data("user1@tenant1.com")
        response1 = client.post("/api/v1/employee", json=data1, headers=auth_headers)
        assert response1.status_code == 201
        employee1_id = response1.json()["id"]
        
        # Create second user
        from schemas.user import UserCreate
        from services.user_service import UserService
        
        user_data2 = UserCreate(
            email="user2@tenant2.com",
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
        
        # Create employee for second user
        data2 = EmployeeDataFactory.valid_employee_data("emp2@tenant2.com")
        response2 = client.post("/api/v1/employee", json=data2, headers=auth_headers2)
        assert response2.status_code == 201
        employee2_id = response2.json()["id"]
        
        # Try to create job timeline for user2's employee with user1's employee as line_manager
        # This should fail due to tenant isolation
        job_data = EmployeeDataFactory.valid_job_timeline_data()
        job_data["line_manager_id"] = employee1_id  # Cross-tenant reference
        
        response = client.post(
            f"/api/v1/employee/{employee2_id}/job",
            json=job_data,
            headers=auth_headers2
        )
        assert response.status_code == 400
        assert "line_manager_id not found or access denied" in response.json()["detail"]
        
        # Try to create full employee with cross-tenant line_manager_id
        full_employee_data = EmployeeDataFactory.valid_full_employee_data("emp3@tenant2.com")
        full_employee_data["job_timeline"][0]["line_manager_id"] = employee1_id  # Cross-tenant reference
        
        response = client.post(
            "/api/v1/employee/full",
            json=full_employee_data,
            headers=auth_headers2
        )
        assert response.status_code == 400
        assert "line_manager_id not found or access denied" in response.json()["detail"]
        
        # Valid case: user2 can reference their own employee as line_manager
        job_data_valid = EmployeeDataFactory.valid_job_timeline_data()
        job_data_valid["line_manager_id"] = employee2_id  # Same tenant
        
        response = client.post(
            f"/api/v1/employee/{employee2_id}/job",
            json=job_data_valid,
            headers=auth_headers2
        )
        assert response.status_code == 201

    def test_delete_employee_requires_authentication(self, client: TestClient):
        """Test that delete employee endpoint requires authentication."""
        response = client.delete("/api/v1/employee/1")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth headers

    def test_delete_employee_success(self, client: TestClient, auth_headers: dict):
        """Test successful employee deletion."""
        # First create an employee
        data = EmployeeDataFactory.valid_employee_data()
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Add some related data to test cascade deletion
        personal_data = EmployeeDataFactory.valid_personal_details_data()
        client.post(f"/api/v1/employee/{employee_id}/personal", json=personal_data, headers=auth_headers)
        
        bank_data = EmployeeDataFactory.valid_bank_info_data()
        client.post(f"/api/v1/employee/{employee_id}/bank", json=bank_data, headers=auth_headers)
        
        job_data = EmployeeDataFactory.valid_job_timeline_data()
        client.post(f"/api/v1/employee/{employee_id}/job", json=job_data, headers=auth_headers)
        
        # Now delete the employee
        delete_response = client.delete(f"/api/v1/employee/{employee_id}", headers=auth_headers)
        assert delete_response.status_code == 204
        
        # Verify employee is deleted
        get_response = client.get(f"/api/v1/employee/{employee_id}", headers=auth_headers)
        assert get_response.status_code == 404
        
        # Verify related data is also deleted
        personal_response = client.get(f"/api/v1/employee/{employee_id}/personal", headers=auth_headers)
        assert personal_response.status_code == 404
        
        bank_response = client.get(f"/api/v1/employee/{employee_id}/bank", headers=auth_headers)
        assert bank_response.status_code == 404

    def test_delete_employee_not_found(self, client: TestClient, auth_headers: dict):
        """Test delete employee with non-existent ID."""
        response = client.delete("/api/v1/employee/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "Employee not found" in response.json()["detail"]


class TestEmployeePartialUpdateAPI:
    """Test cases for PATCH /employee/{employee_id}/full endpoint."""
    
    def test_partial_update_employee_requires_authentication(self, client: TestClient):
        """Test that partial update employee endpoint requires authentication."""
        data = {"first_name": "Updated"}
        
        response = client.patch("/api/v1/employee/1/full", json=data)
        
        assert response.status_code == 403
        assert "detail" in response.json()
    
    def test_partial_update_employee_success_single_field(self, client: TestClient, auth_headers: dict):
        """Test successful partial update with single field."""
        # First create an employee
        data = EmployeeDataFactory.valid_employee_data("partial.single@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Update only first name
        update_data = {"first_name": "Updated John"}
        response = client.patch(f"/api/v1/employee/{employee_id}/full", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["first_name"] == "Updated John"
        assert response_data["last_name"] == "Doe"  # Should remain unchanged
        assert response_data["email"] == "partial.single@example.com"  # Should remain unchanged
        assert response_data["phone"] == "(555) 123-4567"  # Should remain unchanged
        assert response_data["join_date"] == "2024-01-15"  # Should remain unchanged
    
    def test_partial_update_employee_success_multiple_fields(self, client: TestClient, auth_headers: dict):
        """Test successful partial update with multiple fields."""
        # First create an employee
        data = EmployeeDataFactory.valid_employee_data("partial.multiple@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Update multiple fields
        update_data = {
            "first_name": "Updated John",
            "last_name": "Updated Doe",
            "phone": "(555) 999-8888"
        }
        response = client.patch(f"/api/v1/employee/{employee_id}/full", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["first_name"] == "Updated John"
        assert response_data["last_name"] == "Updated Doe"
        assert response_data["phone"] == "(555) 999-8888"
        assert response_data["email"] == "partial.multiple@example.com"  # Should remain unchanged
        assert response_data["join_date"] == "2024-01-15"  # Should remain unchanged
    
    def test_partial_update_employee_email_change(self, client: TestClient, auth_headers: dict):
        """Test successful partial update with email change."""
        # First create an employee
        data = EmployeeDataFactory.valid_employee_data("partial.email@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Update email
        update_data = {"email": "updated.email@example.com"}
        response = client.patch(f"/api/v1/employee/{employee_id}/full", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["email"] == "updated.email@example.com"
        assert response_data["first_name"] == "John"  # Should remain unchanged
    
    def test_partial_update_employee_email_duplicate(self, client: TestClient, auth_headers: dict):
        """Test partial update with duplicate email fails."""
        # Create first employee
        data1 = EmployeeDataFactory.valid_employee_data("employee1@example.com")
        create_response1 = client.post("/api/v1/employee", json=data1, headers=auth_headers)
        assert create_response1.status_code == 201
        employee1_id = create_response1.json()["id"]
        
        # Create second employee
        data2 = EmployeeDataFactory.valid_employee_data("employee2@example.com")
        create_response2 = client.post("/api/v1/employee", json=data2, headers=auth_headers)
        assert create_response2.status_code == 201
        employee2_id = create_response2.json()["id"]
        
        # Try to update second employee with first employee's email
        update_data = {"email": "employee1@example.com"}
        response = client.patch(f"/api/v1/employee/{employee2_id}/full", json=update_data, headers=auth_headers)
        
        assert response.status_code == 400
        error_data = response.json()
        assert "Email 'employee1@example.com' is already in use by another employee" in error_data["detail"]
    
    def test_partial_update_employee_invalid_data(self, client: TestClient, auth_headers: dict):
        """Test partial update with invalid data fails validation."""
        # First create an employee
        data = EmployeeDataFactory.valid_employee_data("partial.invalid@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Try to update with invalid data
        update_data = {
            "first_name": "",  # Too short
            "email": "invalid-email",  # Invalid format
            "phone": "123"  # Too short
        }
        response = client.patch(f"/api/v1/employee/{employee_id}/full", json=update_data, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error
        error_data = response.json()
        assert "detail" in error_data
    
    def test_partial_update_employee_not_found(self, client: TestClient, auth_headers: dict):
        """Test partial update of non-existent employee."""
        update_data = {"first_name": "Updated"}
        
        response = client.patch("/api/v1/employee/99999/full", json=update_data, headers=auth_headers)
        
        assert response.status_code == 400
        error_data = response.json()
        assert "Employee not found or access denied" in error_data["detail"]
    
    def test_partial_update_employee_preserves_related_data(self, client: TestClient, auth_headers: dict):
        """Test that partial update preserves all related data."""
        # Create a full employee with all related data
        data = EmployeeDataFactory.valid_full_employee_data("partial.preserve@example.com")
        create_response = client.post("/api/v1/employee/full", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Verify related data exists
        full_response = client.get(f"/api/v1/employee/{employee_id}/full", headers=auth_headers)
        assert full_response.status_code == 200
        full_data = full_response.json()
        assert full_data["personal_details"] is not None
        assert full_data["bank_info"] is not None
        assert len(full_data["job_timeline"]) > 0
        assert len(full_data["dependents"]) > 0
        assert len(full_data["documents"]) > 0
        
        # Update only basic fields
        update_data = {"first_name": "Updated John"}
        response = client.patch(f"/api/v1/employee/{employee_id}/full", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["first_name"] == "Updated John"
        
        # Verify all related data is still there
        full_response_after = client.get(f"/api/v1/employee/{employee_id}/full", headers=auth_headers)
        assert full_response_after.status_code == 200
        full_data_after = full_response_after.json()
        
        # All related data should be preserved
        assert full_data_after["personal_details"] is not None
        assert full_data_after["bank_info"] is not None
        assert len(full_data_after["job_timeline"]) == len(full_data["job_timeline"])
        assert len(full_data_after["dependents"]) == len(full_data["dependents"])
        assert len(full_data_after["documents"]) == len(full_data["documents"])
    
    def test_partial_update_employee_empty_request(self, client: TestClient, auth_headers: dict):
        """Test partial update with empty request body."""
        # First create an employee
        data = EmployeeDataFactory.valid_employee_data("partial.empty@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Update with empty body
        update_data = {}
        response = client.patch(f"/api/v1/employee/{employee_id}/full", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        # All fields should remain unchanged
        assert response_data["first_name"] == "John"
        assert response_data["last_name"] == "Doe"
        assert response_data["email"] == "partial.empty@example.com"
    
    def test_partial_update_employee_join_date(self, client: TestClient, auth_headers: dict):
        """Test partial update with join date change."""
        # First create an employee
        data = EmployeeDataFactory.valid_employee_data("partial.date@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Update join date
        update_data = {"join_date": "2024-06-01"}
        response = client.patch(f"/api/v1/employee/{employee_id}/full", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["join_date"] == "2024-06-01"
        assert response_data["first_name"] == "John"  # Should remain unchanged


class TestEmployeeContractTimelineAPI:
    """Test contract timeline API endpoints."""
    
    def test_create_contract_timeline(self, client: TestClient, auth_headers: dict):
        """Test creating a contract timeline entry."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("contract.test@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create contract timeline entry
        contract_data = {
            "contract_number": "EMP-CT-001",
            "contract_name": "Software Engineer Contract",
            "contract_type": "FULL_TIME",
            "start_date": "2024-01-15",
            "end_date": None,
            "is_active": True
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/contract", json=contract_data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["contract_number"] == "EMP-CT-001"
        assert response_data["contract_name"] == "Software Engineer Contract"
        assert response_data["contract_type"] == "FULL_TIME"
        assert response_data["start_date"] == "2024-01-15"
        assert response_data["end_date"] is None
        assert response_data["is_active"] is True
        assert response_data["employee_id"] == employee_id
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    def test_get_contract_timeline(self, client: TestClient, auth_headers: dict):
        """Test getting contract timeline entries."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("contract.get@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create multiple contract timeline entries
        contracts = [
            {
                "contract_number": "EMP-CT-001",
                "contract_name": "Initial Contract",
                "contract_type": "FULL_TIME",
                "start_date": "2024-01-15",
                "end_date": "2024-12-31",
                "is_active": False
            },
            {
                "contract_number": "EMP-CT-002",
                "contract_name": "Renewed Contract",
                "contract_type": "FULL_TIME",
                "start_date": "2025-01-01",
                "end_date": None,
                "is_active": True
            }
        ]
        
        for contract_data in contracts:
            response = client.post(f"/api/v1/employee/{employee_id}/contract", json=contract_data, headers=auth_headers)
            assert response.status_code == 201
        
        # Get all contract timeline entries
        response = client.get(f"/api/v1/employee/{employee_id}/contract", headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        
        # Should be ordered by start_date desc (newest first)
        assert response_data[0]["contract_number"] == "EMP-CT-002"
        assert response_data[1]["contract_number"] == "EMP-CT-001"
    
    def test_update_contract_timeline(self, client: TestClient, auth_headers: dict):
        """Test updating a contract timeline entry."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("contract.update@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create contract timeline entry
        contract_data = {
            "contract_number": "EMP-CT-001",
            "contract_name": "Software Engineer Contract",
            "contract_type": "FULL_TIME",
            "start_date": "2024-01-15",
            "end_date": None,
            "is_active": True
        }
        
        create_response = client.post(f"/api/v1/employee/{employee_id}/contract", json=contract_data, headers=auth_headers)
        assert create_response.status_code == 201
        contract_id = create_response.json()["id"]
        
        # Update contract timeline entry
        update_data = {
            "contract_number": "EMP-CT-001-UPDATED",
            "contract_name": "Updated Software Engineer Contract",
            "contract_type": "PART_TIME",
            "start_date": "2024-02-01",
            "end_date": "2024-12-31",
            "is_active": False
        }
        
        response = client.put(f"/api/v1/employee/{employee_id}/contract/{contract_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["contract_number"] == "EMP-CT-001-UPDATED"
        assert response_data["contract_name"] == "Updated Software Engineer Contract"
        assert response_data["contract_type"] == "PART_TIME"
        assert response_data["start_date"] == "2024-02-01"
        assert response_data["end_date"] == "2024-12-31"
        assert response_data["is_active"] is False
        assert response_data["id"] == contract_id
    
    def test_delete_contract_timeline(self, client: TestClient, auth_headers: dict):
        """Test deleting a contract timeline entry."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("contract.delete@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create contract timeline entry
        contract_data = {
            "contract_number": "EMP-CT-001",
            "contract_name": "Software Engineer Contract",
            "contract_type": "FULL_TIME",
            "start_date": "2024-01-15",
            "end_date": None,
            "is_active": True
        }
        
        create_response = client.post(f"/api/v1/employee/{employee_id}/contract", json=contract_data, headers=auth_headers)
        assert create_response.status_code == 201
        contract_id = create_response.json()["id"]
        
        # Delete contract timeline entry
        response = client.delete(f"/api/v1/employee/{employee_id}/contract/{contract_id}", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/employee/{employee_id}/contract", headers=auth_headers)
        assert get_response.status_code == 200
        assert len(get_response.json()) == 0
    
    def test_contract_timeline_validation(self, client: TestClient, auth_headers: dict):
        """Test contract timeline validation."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("contract.validation@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Test invalid contract type
        invalid_data = {
            "contract_number": "EMP-CT-001",
            "contract_name": "Software Engineer Contract",
            "contract_type": "INVALID_TYPE",
            "start_date": "2024-01-15",
            "end_date": None,
            "is_active": True
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/contract", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422
        
        # Test missing required fields
        incomplete_data = {
            "contract_number": "EMP-CT-001",
            "contract_name": "Software Engineer Contract",
            # Missing contract_type, start_date
            "end_date": None,
            "is_active": True
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/contract", json=incomplete_data, headers=auth_headers)
        assert response.status_code == 422
    
    def test_contract_timeline_duplicate_number(self, client: TestClient, auth_headers: dict):
        """Test that contract numbers must be unique."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("contract.duplicate@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create first contract timeline entry
        contract_data = {
            "contract_number": "EMP-CT-001",
            "contract_name": "Software Engineer Contract",
            "contract_type": "FULL_TIME",
            "start_date": "2024-01-15",
            "end_date": None,
            "is_active": True
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/contract", json=contract_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Try to create another with same contract number
        response = client.post(f"/api/v1/employee/{employee_id}/contract", json=contract_data, headers=auth_headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_contract_timeline_in_full_employee_response(self, client: TestClient, auth_headers: dict):
        """Test that contract timeline is included in full employee response."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("contract.full@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create contract timeline entry
        contract_data = {
            "contract_number": "EMP-CT-001",
            "contract_name": "Software Engineer Contract",
            "contract_type": "FULL_TIME",
            "start_date": "2024-01-15",
            "end_date": None,
            "is_active": True
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/contract", json=contract_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Get full employee response
        response = client.get(f"/api/v1/employee/{employee_id}", headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert "contract_timeline" in response_data
        assert len(response_data["contract_timeline"]) == 1
        assert response_data["contract_timeline"][0]["contract_number"] == "EMP-CT-001"
    
    def test_patch_employee_with_contract_timeline(self, client: TestClient, auth_headers: dict):
        """Test PATCH /full endpoint with contract timeline."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("contract.patch@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Update employee with contract timeline using PATCH
        patch_data = {
            "contract_timeline": [
                {
                    "contract_number": "EMP-CT-001",
                    "contract_name": "Software Engineer Contract",
                    "contract_type": "FULL_TIME",
                    "start_date": "2024-01-15",
                    "end_date": None,
                    "is_active": True
                }
            ]
        }
        
        response = client.patch(f"/api/v1/employee/{employee_id}/full", json=patch_data, headers=auth_headers)
        
        assert response.status_code == 200
        response_data = response.json()
        assert "contract_timeline" in response_data
        assert len(response_data["contract_timeline"]) == 1
        assert response_data["contract_timeline"][0]["contract_number"] == "EMP-CT-001"
        
        # Verify it's also available via individual endpoint
        response = client.get(f"/api/v1/employee/{employee_id}/contract", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["contract_number"] == "EMP-CT-001"
    
    def test_contract_timeline_access_control(self, client: TestClient, auth_headers: dict, other_user_auth_headers: dict):
        """Test that users can only access their own contract timeline."""
        # Create employee with first user
        data = EmployeeDataFactory.valid_employee_data("contract.access@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create contract timeline entry
        contract_data = {
            "contract_number": "EMP-CT-001",
            "contract_name": "Software Engineer Contract",
            "contract_type": "FULL_TIME",
            "start_date": "2024-01-15",
            "end_date": None,
            "is_active": True
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/contract", json=contract_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Try to access with different user
        response = client.get(f"/api/v1/employee/{employee_id}/contract", headers=other_user_auth_headers)
        assert response.status_code == 404
        
        # Try to create contract timeline with different user
        response = client.post(f"/api/v1/employee/{employee_id}/contract", json=contract_data, headers=other_user_auth_headers)
        assert response.status_code == 404


class TestEmployeeWorkScheduleAPI:
    """Test work schedule API endpoints."""
    
    def test_create_work_schedule(self, client: TestClient, auth_headers: dict):
        """Test creating a work schedule entry."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("work.schedule.test@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create work schedule entry
        schedule_data = {
            "effective_from": "2024-01-15",
            "effective_to": None,
            "schedule_type": "duration-based",
            "standard_hours_per_day": 8.0,
            "total_hours_per_week": 40.0,
            "monday_hours": 8.0,
            "tuesday_hours": 8.0,
            "wednesday_hours": 8.0,
            "thursday_hours": 8.0,
            "friday_hours": 8.0,
            "saturday_hours": 0.0,
            "sunday_hours": 0.0,
            "is_current": True
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/work-schedule", json=schedule_data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["schedule_type"] == "duration-based"
        assert response_data["total_hours_per_week"] == 40.0
        assert response_data["monday_hours"] == 8.0
        assert response_data["is_current"] is True
        assert response_data["employee_id"] == employee_id
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    def test_get_work_schedule(self, client: TestClient, auth_headers: dict):
        """Test retrieving work schedule entries."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("work.schedule.get@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create multiple work schedule entries
        schedule_data1 = {
            "effective_from": "2024-01-01",
            "effective_to": "2024-06-30",
            "schedule_type": "duration-based",
            "total_hours_per_week": 40.0,
            "is_current": False
        }
        
        schedule_data2 = {
            "effective_from": "2024-07-01",
            "effective_to": None,
            "schedule_type": "flexible",
            "total_hours_per_week": 35.0,
            "is_current": True
        }
        
        # Create first schedule
        response1 = client.post(f"/api/v1/employee/{employee_id}/work-schedule", json=schedule_data1, headers=auth_headers)
        assert response1.status_code == 201
        
        # Create second schedule
        response2 = client.post(f"/api/v1/employee/{employee_id}/work-schedule", json=schedule_data2, headers=auth_headers)
        assert response2.status_code == 201
        
        # Get all work schedules
        response = client.get(f"/api/v1/employee/{employee_id}/work-schedule", headers=auth_headers)
        assert response.status_code == 200
        
        schedules = response.json()
        assert len(schedules) == 2
        
        # Should be ordered by effective_from descending (newest first)
        assert schedules[0]["schedule_type"] == "flexible"
        assert schedules[1]["schedule_type"] == "duration-based"
    
    def test_update_work_schedule(self, client: TestClient, auth_headers: dict):
        """Test updating a work schedule entry."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("work.schedule.update@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create work schedule entry
        schedule_data = {
            "effective_from": "2024-01-15",
            "effective_to": None,
            "schedule_type": "duration-based",
            "total_hours_per_week": 40.0,
            "is_current": True
        }
        
        create_response = client.post(f"/api/v1/employee/{employee_id}/work-schedule", json=schedule_data, headers=auth_headers)
        assert create_response.status_code == 201
        schedule_id = create_response.json()["id"]
        
        # Update work schedule
        update_data = {
            "effective_from": "2024-01-15",
            "effective_to": None,
            "schedule_type": "flexible",
            "total_hours_per_week": 35.0,
            "is_current": True
        }
        
        response = client.put(f"/api/v1/employee/{employee_id}/work-schedule/{schedule_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["schedule_type"] == "flexible"
        assert response_data["total_hours_per_week"] == 35.0
    
    def test_delete_work_schedule(self, client: TestClient, auth_headers: dict):
        """Test deleting a work schedule entry."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("work.schedule.delete@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create work schedule entry
        schedule_data = {
            "effective_from": "2024-01-15",
            "effective_to": None,
            "schedule_type": "duration-based",
            "total_hours_per_week": 40.0,
            "is_current": True
        }
        
        create_response = client.post(f"/api/v1/employee/{employee_id}/work-schedule", json=schedule_data, headers=auth_headers)
        assert create_response.status_code == 201
        schedule_id = create_response.json()["id"]
        
        # Delete work schedule
        response = client.delete(f"/api/v1/employee/{employee_id}/work-schedule/{schedule_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f"/api/v1/employee/{employee_id}/work-schedule", headers=auth_headers)
        assert response.status_code == 200
        schedules = response.json()
        assert len(schedules) == 0
    
    def test_work_schedule_validation(self, client: TestClient, auth_headers: dict):
        """Test work schedule validation rules."""
        # Create employee first
        data = EmployeeDataFactory.valid_employee_data("work.schedule.validation@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Test invalid schedule type
        invalid_data = {
            "effective_from": "2024-01-15",
            "effective_to": None,
            "schedule_type": "invalid-type",
            "total_hours_per_week": 40.0,
            "is_current": True
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/work-schedule", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422
        
        # Test invalid hours
        invalid_data2 = {
            "effective_from": "2024-01-15",
            "effective_to": None,
            "schedule_type": "duration-based",
            "total_hours_per_week": 200.0,  # Too many hours
            "is_current": True
        }
        
        response = client.post(f"/api/v1/employee/{employee_id}/work-schedule", json=invalid_data2, headers=auth_headers)
        assert response.status_code == 422
    
    def test_work_schedule_in_full_employee_response(self, client: TestClient, auth_headers: dict):
        """Test that work schedule is included in full employee response."""
        # Create employee with work schedule
        data = EmployeeDataFactory.valid_employee_data("work.schedule.full@example.com")
        create_response = client.post("/api/v1/employee", json=data, headers=auth_headers)
        assert create_response.status_code == 201
        employee_id = create_response.json()["id"]
        
        # Create work schedule entry
        schedule_data = {
            "effective_from": "2024-01-15",
            "effective_to": None,
            "schedule_type": "duration-based",
            "total_hours_per_week": 40.0,
            "is_current": True
        }
        
        schedule_response = client.post(f"/api/v1/employee/{employee_id}/work-schedule", json=schedule_data, headers=auth_headers)
        assert schedule_response.status_code == 201
        
        # Get full employee data
        response = client.get(f"/api/v1/employee/{employee_id}/full", headers=auth_headers)
        assert response.status_code == 200
        
        employee_data = response.json()
        assert "work_schedule" in employee_data
        assert len(employee_data["work_schedule"]) == 1
        assert employee_data["work_schedule"][0]["schedule_type"] == "duration-based"
        assert employee_data["work_schedule"][0]["total_hours_per_week"] == 40.0


class TestEmployeeListAPI:
    """Test employee listing functionality."""
    
    def test_list_employees_success(self, client: TestClient, auth_headers: dict):
        """Test successful employee listing."""
        # Create multiple employees
        for i in range(3):
            employee_data = EmployeeDataFactory.valid_employee_data(f"employee{i}@example.com")
            response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
            assert response.status_code == 201
        
        # List employees
        response = client.get("/api/v1/employee", headers=auth_headers)
        assert response.status_code == 200
        
        employees = response.json()
        assert len(employees) >= 3
        assert all("id" in emp for emp in employees)
        assert all("first_name" in emp for emp in employees)
        assert all("last_name" in emp for emp in employees)
    
    def test_list_employees_with_pagination(self, client: TestClient, auth_headers: dict):
        """Test employee listing with pagination."""
        # Create multiple employees
        for i in range(5):
            employee_data = EmployeeDataFactory.valid_employee_data(f"employee{i}@example.com")
            response = client.post("/api/v1/employee", json=employee_data, headers=auth_headers)
            assert response.status_code == 201
        
        # Test pagination
        response = client.get("/api/v1/employee?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        
        employees = response.json()
        assert len(employees) <= 2
    
    def test_list_employees_requires_auth(self, client: TestClient):
        """Test that employee listing requires authentication."""
        response = client.get("/api/v1/employee")
        assert response.status_code == 403



# Personal details and job timeline endpoints don't exist yet
# These tests will be added when the endpoints are implemented
