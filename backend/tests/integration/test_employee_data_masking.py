"""
Integration tests for Employee Data Masking functionality.

This module tests that sensitive data is properly masked in API responses
across all employee-related endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.employee import Employee, EmployeePersonalDetails, EmployeeBankInfo, EmployeeDocument
from models.user import User
from schemas.employee import EmployeePersonalDetailsRequest, EmployeeBankInfoRequest, EmployeeDocumentRequest


class TestEmployeeDataMasking:
    """Test class for data masking functionality."""

    def test_personal_details_tax_id_masking(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that personal tax ID is properly masked."""
        personal_data = {
            "gender": "MALE",
            "nationality": "American",
            "personal_tax_id": "123-45-6789",
            "social_insurance_number": "987654321",
            "primary_address": "123 Main Street, Apt 4B"
        }
        
        # Create personal details
        create_response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_200_OK
        
        # Get personal details and verify masking
        get_response = client.get(
            f"/api/v1/employee/{employee_id}/personal",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        
        data = get_response.json()
        assert data["personal_tax_id"] == "*******6789"
        assert data["social_insurance_number"] == "*****4321"
        assert data["primary_address"] == "*****************Apt 4B"

    def test_personal_details_different_tax_id_formats(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test masking with different tax ID formats."""
        test_cases = [
            ("123456789", "*****6789"),  # 9 digits
            ("123-45-6789", "*******6789"),  # SSN format
            ("12-3456789", "******6789"),  # Mixed format
            ("123456789012", "********9012"),  # 12 digits
        ]
        
        for tax_id, expected_masked in test_cases:
            personal_data = {
                "gender": "MALE",
                "nationality": "American",
                "personal_tax_id": tax_id,
                "social_insurance_number": "987654321",
                "primary_address": "123 Main Street"
            }
            
            # Create personal details
            create_response = client.put(
                f"/api/v1/employee/{employee_id}/personal",
                json=personal_data,
                headers=auth_headers
            )
            assert create_response.status_code == status.HTTP_200_OK
            
            # Get and verify masking
            get_response = client.get(
                f"/api/v1/employee/{employee_id}/personal",
                headers=auth_headers
            )
            assert get_response.status_code == status.HTTP_200_OK
            
            data = get_response.json()
            assert data["personal_tax_id"] == expected_masked

    def test_personal_details_short_strings_not_masked(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that short strings are not masked."""
        personal_data = {
            "gender": "MALE",
            "nationality": "American",
            "personal_tax_id": "123",  # Short string
            "social_insurance_number": "12",  # Short string
            "primary_address": "123"  # Short string
        }
        
        # Create personal details
        create_response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_200_OK
        
        # Get and verify no masking for short strings
        get_response = client.get(
            f"/api/v1/employee/{employee_id}/personal",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        
        data = get_response.json()
        assert data["personal_tax_id"] == "***"
        assert data["social_insurance_number"] == "**"
        assert data["primary_address"] == "***"

    def test_personal_details_none_values_handled(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that None values are handled correctly."""
        personal_data = {
            "gender": "MALE",
            "nationality": "American",
            "personal_tax_id": None,
            "social_insurance_number": None,
            "primary_address": None
        }
        
        # Create personal details
        create_response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_200_OK
        
        # Get and verify None values
        get_response = client.get(
            f"/api/v1/employee/{employee_id}/personal",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        
        data = get_response.json()
        assert data["personal_tax_id"] is None
        assert data["social_insurance_number"] is None
        assert data["primary_address"] is None

    def test_bank_info_account_number_masking(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that bank account numbers are properly masked."""
        bank_data = {
            "bank_name": "Test Bank",
            "account_number": "1234567890",
            "routing_number": "021000021",
            "account_type": "CHECKING",
            "account_holder_name": "John Doe",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": True,
            "is_active": True
        }
        
        # Create bank info
        create_response = client.put(
            f"/api/v1/employee/{employee_id}/bank",
            json=bank_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_200_OK
        
        # Get bank info and verify masking
        get_response = client.get(
            f"/api/v1/employee/{employee_id}/bank",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        
        data = get_response.json()
        assert data["account_number"] == "******7890"
        assert data["routing_number"] == "*****0021"

    def test_bank_info_different_account_number_formats(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test masking with different account number formats."""
        test_cases = [
            ("1234567890", "******7890"),  # 10 digits: 6 asterisks + 4 digits
            ("1234567890123456", "************3456"),  # 16 digits: 12 asterisks + 4 digits
            ("1234-5678-9012-3456", "***************3456"),  # Credit card format: 19 chars, 15 asterisks + 4 digits
            ("123456789", "*****6789"),  # 9 digits: 5 asterisks + 4 digits
        ]
        
        for account_number, expected_masked in test_cases:
            bank_data = {
                "bank_name": "Test Bank",
                "account_number": account_number,
                "routing_number": "021000021",
                "account_type": "CHECKING",
                "account_holder_name": "John Doe",
                "account_holder_type": "INDIVIDUAL",
                "is_primary": True,
                "is_active": True
            }
            
            # Create bank info
            create_response = client.put(
                f"/api/v1/employee/{employee_id}/bank",
                json=bank_data,
                headers=auth_headers
            )
            assert create_response.status_code == status.HTTP_200_OK
            
            # Get and verify masking
            get_response = client.get(
                f"/api/v1/employee/{employee_id}/bank",
                headers=auth_headers
            )
            assert get_response.status_code == status.HTTP_200_OK
            
            data = get_response.json()
            assert data["account_number"] == expected_masked

    def test_document_file_path_masking(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that document file paths are properly masked."""
        document_data = {
            "document_type": "CONTRACT",
            "file_name": "employment_contract.pdf",
            "file_path": "/uploads/contracts/employment_contract_2024.pdf",
            "file_size": 2048576,
            "mime_type": "application/pdf",
            "is_active": True
        }
        
        # Create document
        create_response = client.post(
            f"/api/v1/employee/{employee_id}/documents",
            json=document_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Get the created document ID
        created_doc = create_response.json()
        document_id = created_doc["id"]
        
        # Get document and verify masking
        get_response = client.get(
            f"/api/v1/employee/{employee_id}/documents/{document_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        
        data = get_response.json()
        assert data["file_path"].startswith("*****")
        assert data["file_path"].endswith(".pdf")

    def test_document_different_file_path_formats(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test masking with different file path formats."""
        test_cases = [
            ("/uploads/doc.pdf", "************.pdf"),  # 16 chars: 12 asterisks + 4 chars (.pdf)
            ("/very/long/path/to/document.pdf", "***************************.pdf"),  # 32 chars: 27 asterisks + 4 chars (.pdf)
            ("s3://bucket/folder/file.pdf", "***********************.pdf"),  # 25 chars: 21 asterisks + 4 chars (.pdf)
            ("https://example.com/files/doc.pdf", "*****************************.pdf"),  # 32 chars: 28 asterisks + 4 chars (.pdf)
        ]
        
        for file_path, expected_masked in test_cases:
            document_data = {
                "document_type": "CONTRACT",
                "file_name": "test.pdf",
                "file_path": file_path,
                "file_size": 1024,
                "mime_type": "application/pdf",
                "is_active": True
            }
            
            # Create document
            create_response = client.post(
                f"/api/v1/employee/{employee_id}/documents",
                json=document_data,
                headers=auth_headers
            )
            assert create_response.status_code == status.HTTP_201_CREATED
            
            # Get the created document ID
            created_doc = create_response.json()
            document_id = created_doc["id"]
            
            # Get and verify masking
            get_response = client.get(
                f"/api/v1/employee/{employee_id}/documents/{document_id}",
                headers=auth_headers
            )
            assert get_response.status_code == status.HTTP_200_OK
            
            data = get_response.json()
            assert data["file_path"] == expected_masked

    def test_full_employee_response_masking(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that full employee response properly masks sensitive data."""
        # Create personal details
        personal_data = {
            "gender": "MALE",
            "nationality": "American",
            "personal_tax_id": "123-45-6789",
            "social_insurance_number": "987654321",
            "primary_address": "123 Main Street, Apt 4B"
        }
        
        client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data,
            headers=auth_headers
        )
        
        # Create bank info
        bank_data = {
            "bank_name": "Test Bank",
            "account_number": "1234567890",
            "routing_number": "021000021",
            "account_type": "CHECKING",
            "account_holder_name": "John Doe",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": True,
            "is_active": True
        }
        
        client.put(
            f"/api/v1/employee/{employee_id}/bank",
            json=bank_data,
            headers=auth_headers
        )
        
        # Create document
        document_data = {
            "document_type": "CONTRACT",
            "file_name": "contract.pdf",
            "file_path": "/uploads/contract.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf",
            "is_active": True
        }
        
        create_response = client.post(
            f"/api/v1/employee/{employee_id}/documents",
            json=document_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Get full employee response
        full_response = client.get(
            f"/api/v1/employee/{employee_id}/full",
            headers=auth_headers
        )
        assert full_response.status_code == status.HTTP_200_OK
        
        data = full_response.json()
        
        # Verify personal details masking
        assert data["personal_details"]["personal_tax_id"] == "*******6789"
        assert data["personal_details"]["social_insurance_number"] == "*****4321"
        assert data["personal_details"]["primary_address"] == "*****************Apt 4B"
        
        # Verify bank info masking
        assert data["bank_info"]["account_number"] == "******7890"
        assert data["bank_info"]["routing_number"] == "*****0021"
        
        # Verify document masking
        assert len(data["documents"]) == 1
        assert data["documents"][0]["file_path"] == "*****************.pdf"

    def test_masking_consistency_across_endpoints(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that masking is consistent across different endpoints."""
        # Create data
        personal_data = {
            "gender": "MALE",
            "nationality": "American",
            "personal_tax_id": "123-45-6789",
            "social_insurance_number": "987654321",
            "primary_address": "123 Main Street, Apt 4B"
        }
        
        bank_data = {
            "bank_name": "Test Bank",
            "account_number": "1234567890",
            "routing_number": "021000021",
            "account_type": "CHECKING",
            "account_holder_name": "John Doe",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": True,
            "is_active": True
        }
        
        # Create data
        client.put(f"/api/v1/employee/{employee_id}/personal", json=personal_data, headers=auth_headers)
        client.put(f"/api/v1/employee/{employee_id}/bank", json=bank_data, headers=auth_headers)
        
        # Get data from individual endpoints
        personal_response = client.get(f"/api/v1/employee/{employee_id}/personal", headers=auth_headers)
        bank_response = client.get(f"/api/v1/employee/{employee_id}/bank", headers=auth_headers)
        full_response = client.get(f"/api/v1/employee/{employee_id}/full", headers=auth_headers)
        
        personal_data = personal_response.json()
        bank_data = bank_response.json()
        full_data = full_response.json()
        
        # Verify consistent masking - both should be masked
        assert personal_data["personal_tax_id"] == full_data["personal_details"]["personal_tax_id"]
        assert personal_data["social_insurance_number"] == full_data["personal_details"]["social_insurance_number"]
        assert personal_data["primary_address"] == full_data["personal_details"]["primary_address"]
        
        assert bank_data["account_number"] == full_data["bank_info"]["account_number"]
        assert bank_data["routing_number"] == full_data["bank_info"]["routing_number"]

    def test_masking_with_special_characters(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test masking with special characters in sensitive data."""
        personal_data = {
            "gender": "MALE",
            "nationality": "American",
            "personal_tax_id": "123-45-6789",
            "social_insurance_number": "987-65-4321",
            "primary_address": "123 Main St., Apt #4B, Floor 2"
        }
        
        # Create personal details
        create_response = client.put(
            f"/api/v1/employee/{employee_id}/personal",
            json=personal_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_200_OK
        
        # Get and verify masking
        get_response = client.get(
            f"/api/v1/employee/{employee_id}/personal",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        
        data = get_response.json()
        assert data["personal_tax_id"] == "*******6789"
        assert data["social_insurance_number"] == "*******4321"
        assert data["primary_address"] == "************************loor 2"