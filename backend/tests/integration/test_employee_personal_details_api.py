"""
Integration tests for Employee Personal Details API endpoints.

This module tests the complete personal details management functionality including:
- GET /api/v1/employee/{employee_id}/personal
- PUT /api/v1/employee/{employee_id}/personal  
- PATCH /api/v1/employee/{employee_id}/personal
- DELETE /api/v1/employee/{employee_id}/personal
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.employee import Employee, EmployeePersonalDetails
from models.user import User
from schemas.employee import EmployeePersonalDetailsRequest


class TestEmployeePersonalDetailsEndpoints:
    """Test class for personal details CRUD endpoints."""

    def test_get_personal_details_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that getting personal details requires authentication."""
        response = client.get(f"/api/v1/employee/{employee_id}/personal")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_personal_details_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test getting personal details for employee without personal details."""
        response = client.get(
            f"/api/v1/employee/{employee_id}/personal", headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Personal details not found" in response.json()["detail"]

    def test_get_personal_details_success(
        self, client: TestClient, auth_headers: dict, employee_with_personal_details: int
    ):
        """Test successfully getting personal details with data masking."""
        response = client.get(
            f"/api/v1/employee/{employee_with_personal_details}/personal", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["employee_id"] == employee_with_personal_details
        assert data["gender"] == "MALE"
        assert data["nationality"] == "American"
        
        # Verify sensitive data is masked
        assert data["personal_tax_id"] == "*******6789"
        assert data["social_insurance_number"] == "*****4321"
        assert data["primary_address"] == "*************Apt 4B"

    def test_get_personal_details_wrong_user(
        self, client: TestClient, auth_headers: dict, other_user_employee: int
    ):
        """Test getting personal details for employee belonging to different user."""
        response = client.get(
            f"/api/v1/employee/{other_user_employee}/personal", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_personal_details_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that updating personal details requires authentication."""
        personal_data = {
            "gender": "FEMALE",
            "date_of_birth": "1990-01-01",
            "nationality": "Canadian"
        }
        response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_personal_details_success(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test successfully updating personal details (full replacement)."""
        personal_data = {
            "gender": "FEMALE",
            "date_of_birth": "1990-01-01",
            "nationality": "Canadian",
            "health_care_provider": "Sun Life",
            "marital_status": "SINGLE",
            "personal_tax_id": "987-65-4321",
            "social_insurance_number": "123456789",
            "primary_address": "456 Oak Street",
            "city": "Toronto",
            "state": "ON",
            "country": "Canada",
            "postal_code": "M5V 3A8"
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["employee_id"] == employee_id
        assert data["gender"] == "FEMALE"
        assert data["nationality"] == "Canadian"
        assert data["city"] == "Toronto"
        
        # Verify sensitive data is masked
        assert data["personal_tax_id"] == "*******4321"
        assert data["social_insurance_number"] == "*****6789"
        assert data["primary_address"] == "********Street"

    def test_update_personal_details_creates_new_record(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that updating personal details creates new record if none exists."""
        personal_data = {
            "gender": "MALE",
            "date_of_birth": "1985-05-15",
            "nationality": "American",
            "health_care_provider": "Blue Cross",
            "marital_status": "MARRIED",
            "personal_tax_id": "111-22-3333",
            "social_insurance_number": "987654321",
            "primary_address": "789 Pine Avenue",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10001"
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["employee_id"] == employee_id
        assert data["gender"] == "MALE"
        assert data["city"] == "New York"

    def test_update_personal_details_validation_errors(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test validation errors when updating personal details."""
        invalid_data = {
            "gender": "INVALID_GENDER",
            "marital_status": "INVALID_STATUS",
            "personal_tax_id": "invalid-format"
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_personal_details_employee_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating personal details for non-existent employee."""
        personal_data = {
            "gender": "FEMALE",
            "nationality": "Canadian"
        }
        
        response = client.put(
            "/api/v1/employee/99999/personal",
            json=personal_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Employee not found" in response.json()["detail"]

    def test_partial_update_personal_details_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that partial updating personal details requires authentication."""
        personal_data = {"city": "Boston"}
        response = client.patch(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_partial_update_personal_details_success(
        self, client: TestClient, auth_headers: dict, employee_with_personal_details: int
    ):
        """Test successfully partially updating personal details."""
        partial_data = {
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94102"
        }
        
        response = client.patch(
            f"/api/v1/employee/{employee_with_personal_details}/personal",
            json=partial_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["city"] == "San Francisco"
        assert data["state"] == "CA"
        assert data["postal_code"] == "94102"
        
        # Verify other fields remain unchanged
        assert data["gender"] == "MALE"
        assert data["nationality"] == "American"

    def test_partial_update_personal_details_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test partial updating personal details when none exist."""
        partial_data = {"city": "Boston"}
        
        response = client.patch(
            f"/api/v1/employee/{employee_id}/personal",
            json=partial_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Personal details not found" in response.json()["detail"]

    def test_delete_personal_details_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that deleting personal details requires authentication."""
        response = client.delete(f"/api/v1/employee/{employee_id}/personal")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_personal_details_success(
        self, client: TestClient, auth_headers: dict, employee_with_personal_details: int
    ):
        """Test successfully deleting personal details."""
        response = client.delete(
            f"/api/v1/employee/{employee_with_personal_details}/personal",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify personal details are deleted
        get_response = client.get(
            f"/api/v1/employee/{employee_with_personal_details}/personal",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_personal_details_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test deleting personal details when none exist."""
        response = client.delete(
            f"/api/v1/employee/{employee_id}/personal",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Personal details not found" in response.json()["detail"]

    def test_delete_personal_details_wrong_user(
        self, client: TestClient, auth_headers: dict, other_user_employee: int
    ):
        """Test deleting personal details for employee belonging to different user."""
        response = client.delete(
            f"/api/v1/employee/{other_user_employee}/personal",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_personal_details_data_masking(
        self, client: TestClient, auth_headers: dict, employee_with_personal_details: int
    ):
        """Test that sensitive data is properly masked in responses."""
        response = client.get(
            f"/api/v1/employee/{employee_with_personal_details}/personal",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Verify masking patterns
        assert data["personal_tax_id"].startswith("*******")
        assert data["social_insurance_number"].startswith("*****")
        assert data["primary_address"].startswith("*************")
        
        # Verify last few characters are visible
        assert data["personal_tax_id"].endswith("6789")
        assert data["social_insurance_number"].endswith("4321")
        assert data["primary_address"].endswith("Apt 4B")

    def test_personal_details_empty_string_handling(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that empty strings are converted to None for optional fields."""
        personal_data = {
            "gender": "",
            "marital_status": "",
            "nationality": "American"
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["gender"] is None
        assert data["marital_status"] is None
        assert data["nationality"] == "American"

    def test_personal_details_complete_workflow(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test complete personal details workflow: create, get, update, partial update, delete."""
        # 1. Create personal details
        personal_data = {
            "gender": "MALE",
            "date_of_birth": "1985-05-15",
            "nationality": "American",
            "health_care_provider": "Blue Cross",
            "marital_status": "SINGLE",
            "personal_tax_id": "123-45-6789",
            "social_insurance_number": "987654321",
            "primary_address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10001"
        }
        
        create_response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_200_OK
        
        # 2. Get personal details
        get_response = client.get(
            f"/api/v1/employee/{employee_id}/personal",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["gender"] == "MALE"
        assert data["city"] == "New York"
        
        # 3. Full update
        updated_data = personal_data.copy()
        updated_data["marital_status"] = "MARRIED"
        updated_data["city"] = "Boston"
        
        update_response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=updated_data,
            headers=auth_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        # 4. Partial update
        partial_data = {"state": "MA", "postal_code": "02101"}
        patch_response = client.patch(
            f"/api/v1/employee/{employee_id}/personal",
            json=partial_data,
            headers=auth_headers
        )
        assert patch_response.status_code == status.HTTP_200_OK
        
        # 5. Verify changes
        final_response = client.get(
            f"/api/v1/employee/{employee_id}/personal",
            headers=auth_headers
        )
        assert final_response.status_code == status.HTTP_200_OK
        final_data = final_response.json()
        assert final_data["marital_status"] == "MARRIED"
        assert final_data["city"] == "Boston"
        assert final_data["state"] == "MA"
        assert final_data["postal_code"] == "02101"
        
        # 6. Delete personal details
        delete_response = client.delete(
            f"/api/v1/employee/{employee_id}/personal",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 7. Verify deletion
        get_after_delete = client.get(
            f"/api/v1/employee/{employee_id}/personal",
            headers=auth_headers
        )
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND