"""
Integration tests for Employee Bank Information API endpoints.

This module tests the complete bank information management functionality including:
- GET /api/v1/employee/{employee_id}/bank
- PUT /api/v1/employee/{employee_id}/bank  
- PATCH /api/v1/employee/{employee_id}/bank
- DELETE /api/v1/employee/{employee_id}/bank
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.employee import Employee, EmployeeBankInfo
from models.user import User
from schemas.employee import EmployeeBankInfoRequest


class TestEmployeeBankInfoEndpoints:
    """Test class for bank information CRUD endpoints."""

    def test_get_bank_info_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that getting bank info requires authentication."""
        response = client.get(f"/api/v1/employee/{employee_id}/bank")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_bank_info_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test getting bank info for employee without bank info."""
        response = client.get(
            f"/api/v1/employee/{employee_id}/bank", headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Bank information not found" in response.json()["detail"]

    def test_get_bank_info_success(
        self, client: TestClient, auth_headers: dict, employee_with_bank_info: int
    ):
        """Test successfully getting bank info with data masking."""
        response = client.get(
            f"/api/v1/employee/{employee_with_bank_info}/bank", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["employee_id"] == employee_with_bank_info
        assert data["bank_name"] == "Chase Bank"
        assert data["account_type"] == "CHECKING"
        assert data["is_primary"] is True
        
        # Verify sensitive data is masked
        assert data["account_number"] == "******7890"
        assert data["routing_number"] == "*****0021"

    def test_update_bank_info_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that updating bank info requires authentication."""
        bank_data = {
            "bank_name": "Wells Fargo",
            "account_number": "1234567890",
            "routing_number": "021000021",
            "account_type": "CHECKING",
            "account_holder_name": "John Doe",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": True,
            "is_active": True
        }
        response = client.put(
            f"/api/v1/employee/{employee_id}/bank",
            json=bank_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_bank_info_success(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test successfully updating bank info (full replacement)."""
        bank_data = {
            "bank_name": "Wells Fargo",
            "account_number": "9876543210",
            "routing_number": "121000248",
            "account_type": "SAVINGS",
            "account_holder_name": "John Smith",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": True,
            "is_active": True
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/bank",
            json=bank_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["employee_id"] == employee_id
        assert data["bank_name"] == "Wells Fargo"
        assert data["account_type"] == "SAVINGS"
        assert data["is_primary"] is True
        
        # Verify sensitive data is masked
        assert data["account_number"] == "******3210"
        assert data["routing_number"] == "*****0248"

    def test_update_bank_info_creates_new_record(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that updating bank info creates new record if none exists."""
        bank_data = {
            "bank_name": "Bank of America",
            "account_number": "5555666677",
            "routing_number": "026009593",
            "account_type": "CHECKING",
            "account_holder_name": "Jane Doe",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": False,
            "is_active": True
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/bank",
            json=bank_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["employee_id"] == employee_id
        assert data["bank_name"] == "Bank of America"
        assert data["is_primary"] is False

    def test_update_bank_info_validation_errors(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test validation errors when updating bank info."""
        invalid_data = {
            "bank_name": "",  # Empty string
            "account_type": "INVALID_TYPE",
            "account_holder_type": "INVALID_TYPE"
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/bank",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_bank_info_employee_not_found(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating bank info for non-existent employee."""
        bank_data = {
            "bank_name": "Test Bank",
            "account_number": "1234567890",
            "routing_number": "021000021",
            "account_type": "CHECKING",
            "account_holder_name": "Test User",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": True,
            "is_active": True
        }
        
        response = client.put(
            "/api/v1/employee/99999/bank",
            json=bank_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Employee not found" in response.json()["detail"]

    def test_partial_update_bank_info_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that partial updating bank info requires authentication."""
        bank_data = {"account_type": "SAVINGS"}
        response = client.patch(
            f"/api/v1/employee/{employee_id}/bank",
            json=bank_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_partial_update_bank_info_success(
        self, client: TestClient, auth_headers: dict, employee_with_bank_info: int
    ):
        """Test successfully partially updating bank info."""
        partial_data = {
            "account_type": "SAVINGS",
            "is_primary": False,
            "is_active": False
        }
        
        response = client.patch(
            f"/api/v1/employee/{employee_with_bank_info}/bank",
            json=partial_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["account_type"] == "SAVINGS"
        assert data["is_primary"] is False
        assert data["is_active"] is False
        
        # Verify other fields remain unchanged
        assert data["bank_name"] == "Chase Bank"
        assert data["account_holder_name"] == "John Smith"

    def test_partial_update_bank_info_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test partial updating bank info when none exist."""
        partial_data = {"account_type": "SAVINGS"}
        
        response = client.patch(
            f"/api/v1/employee/{employee_id}/bank",
            json=partial_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Bank information not found" in response.json()["detail"]

    def test_delete_bank_info_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that deleting bank info requires authentication."""
        response = client.delete(f"/api/v1/employee/{employee_id}/bank")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_bank_info_success(
        self, client: TestClient, auth_headers: dict, employee_with_bank_info: int
    ):
        """Test successfully deleting bank info."""
        response = client.delete(
            f"/api/v1/employee/{employee_with_bank_info}/bank",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify bank info is deleted
        get_response = client.get(
            f"/api/v1/employee/{employee_with_bank_info}/bank",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_bank_info_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test deleting bank info when none exist."""
        response = client.delete(
            f"/api/v1/employee/{employee_id}/bank",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Bank information not found" in response.json()["detail"]

    def test_bank_info_data_masking(
        self, client: TestClient, auth_headers: dict, employee_with_bank_info: int
    ):
        """Test that sensitive data is properly masked in responses."""
        response = client.get(
            f"/api/v1/employee/{employee_with_bank_info}/bank",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Verify masking patterns
        assert data["account_number"].startswith("******")
        assert data["routing_number"].startswith("*****")
        
        # Verify last few characters are visible
        assert data["account_number"].endswith("7890")
        assert data["routing_number"].endswith("0021")

    def test_bank_info_boolean_fields(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that boolean fields are handled correctly."""
        bank_data = {
            "bank_name": "Test Bank",
            "account_number": "1234567890",
            "routing_number": "021000021",
            "account_type": "CHECKING",
            "account_holder_name": "Test User",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": False,
            "is_active": False
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/bank",
            json=bank_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["is_primary"] is False
        assert data["is_active"] is False

    def test_bank_info_complete_workflow(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test complete bank info workflow: create, get, update, partial update, delete."""
        # 1. Create bank info
        bank_data = {
            "bank_name": "Chase Bank",
            "account_number": "1234567890",
            "routing_number": "021000021",
            "account_type": "CHECKING",
            "account_holder_name": "John Smith",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": True,
            "is_active": True
        }
        
        create_response = client.put(
            f"/api/v1/employee/{employee_id}/bank",
            json=bank_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_200_OK
        
        # 2. Get bank info
        get_response = client.get(
            f"/api/v1/employee/{employee_id}/bank",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["bank_name"] == "Chase Bank"
        assert data["account_type"] == "CHECKING"
        
        # 3. Full update
        updated_data = bank_data.copy()
        updated_data["bank_name"] = "Wells Fargo"
        updated_data["account_type"] = "SAVINGS"
        
        update_response = client.put(
            f"/api/v1/employee/{employee_id}/bank",
            json=updated_data,
            headers=auth_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        # 4. Partial update
        partial_data = {"is_primary": False, "is_active": False}
        patch_response = client.patch(
            f"/api/v1/employee/{employee_id}/bank",
            json=partial_data,
            headers=auth_headers
        )
        assert patch_response.status_code == status.HTTP_200_OK
        
        # 5. Verify changes
        final_response = client.get(
            f"/api/v1/employee/{employee_id}/bank",
            headers=auth_headers
        )
        assert final_response.status_code == status.HTTP_200_OK
        final_data = final_response.json()
        assert final_data["bank_name"] == "Wells Fargo"
        assert final_data["account_type"] == "SAVINGS"
        assert final_data["is_primary"] is False
        assert final_data["is_active"] is False
        
        # 6. Delete bank info
        delete_response = client.delete(
            f"/api/v1/employee/{employee_id}/bank",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 7. Verify deletion
        get_after_delete = client.get(
            f"/api/v1/employee/{employee_id}/bank",
            headers=auth_headers
        )
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND