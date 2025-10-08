"""
Integration tests for Employee Documents API endpoints.

This module tests the complete document management functionality including:
- GET /api/v1/employee/{employee_id}/documents
- GET /api/v1/employee/{employee_id}/documents/{document_id}
- PUT /api/v1/employee/{employee_id}/documents/{document_id}
- PATCH /api/v1/employee/{employee_id}/documents/{document_id}
- DELETE /api/v1/employee/{employee_id}/documents/{document_id}
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from models.employee import Employee, EmployeeDocument
from models.user import User
from schemas.employee import EmployeeDocumentRequest


class TestEmployeeDocumentsEndpoints:
    """Test class for document CRUD endpoints."""

    def test_get_documents_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that getting documents requires authentication."""
        response = client.get(f"/api/v1/employee/{employee_id}/documents")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_documents_empty_list(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test getting documents for employee with no documents."""
        response = client.get(
            f"/api/v1/employee/{employee_id}/documents", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_documents_success(
        self, client: TestClient, auth_headers: dict, employee_with_documents: int
    ):
        """Test successfully getting documents with data masking."""
        response = client.get(
            f"/api/v1/employee/{employee_with_documents}/documents", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 2  # Should have 2 documents
        
        # Verify first document
        doc1 = data[0]
        assert doc1["employee_id"] == employee_with_documents
        assert doc1["document_type"] == "CONTRACT"
        assert doc1["file_name"] == "employment_contract.pdf"
        assert doc1["mime_type"] == "application/pdf"
        assert doc1["is_active"] is True
        
        # Verify sensitive data is masked
        assert doc1["file_path"].startswith("*****")
        assert doc1["file_path"].endswith(".pdf")

    def test_get_specific_document_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that getting specific document requires authentication."""
        response = client.get(f"/api/v1/employee/{employee_id}/documents/99999")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_specific_document_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test getting non-existent document."""
        response = client.get(
            f"/api/v1/employee/{employee_id}/documents/99999", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Document not found" in response.json()["detail"]

    def test_get_specific_document_success(
        self, client: TestClient, auth_headers: dict, employee_with_documents: int
    ):
        """Test successfully getting specific document with data masking."""
        response = client.get(
            f"/api/v1/employee/{employee_with_documents}/documents/1", 
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["employee_id"] == employee_with_documents
        assert data["document_type"] == "CONTRACT"
        assert data["file_name"] == "employment_contract.pdf"
        
        # Verify sensitive data is masked
        assert data["file_path"].startswith("*****")
        assert data["file_path"].endswith(".pdf")

    def test_update_document_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that updating document requires authentication."""
        document_data = {
            "document_type": "CERTIFICATE",
            "file_name": "cert.pdf",
            "file_path": "/uploads/cert.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf",
            "is_active": True
        }
        response = client.put(
            f"/api/v1/employee/{employee_id}/documents/99999",
            json=document_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_document_success(
        self, client: TestClient, auth_headers: dict, employee_with_documents: int
    ):
        """Test successfully updating document (full replacement)."""
        document_data = {
            "document_type": "CERTIFICATE",
            "file_name": "professional_cert.pdf",
            "file_path": "/uploads/certs/professional_cert.pdf",
            "file_size": 2048000,
            "mime_type": "application/pdf",
            "is_active": False
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_with_documents}/documents/1",
            json=document_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["document_type"] == "CERTIFICATE"
        assert data["file_name"] == "professional_cert.pdf"
        assert data["file_size"] == 2048000
        assert data["is_active"] is False
        
        # Verify sensitive data is masked
        assert data["file_path"].startswith("*****")
        assert data["file_path"].endswith(".pdf")

    def test_update_document_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test updating non-existent document."""
        document_data = {
            "document_type": "CERTIFICATE",
            "file_name": "cert.pdf",
            "file_path": "/uploads/cert.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf",
            "is_active": True
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/documents/99999",
            json=document_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Document not found" in response.json()["detail"]

    def test_update_document_validation_errors(
        self, client: TestClient, auth_headers: dict, employee_with_documents: int
    ):
        """Test validation errors when updating document."""
        invalid_data = {
            "document_type": "",  # Empty string
            "file_name": "x" * 300,  # Too long
            "file_size": -1,  # Negative size
            "mime_type": "invalid/mime"
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_with_documents}/documents/1",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_partial_update_document_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that partial updating document requires authentication."""
        document_data = {"is_active": False}
        response = client.patch(
            f"/api/v1/employee/{employee_id}/documents/99999",
            json=document_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_partial_update_document_success(
        self, client: TestClient, auth_headers: dict, employee_with_documents: int
    ):
        """Test successfully partially updating document."""
        partial_data = {
            "document_type": "ID",
            "is_active": False
        }
        
        response = client.patch(
            f"/api/v1/employee/{employee_with_documents}/documents/1",
            json=partial_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["document_type"] == "ID"
        assert data["is_active"] is False
        
        # Verify other fields remain unchanged
        assert data["file_name"] == "employment_contract.pdf"
        assert data["mime_type"] == "application/pdf"

    def test_partial_update_document_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test partial updating non-existent document."""
        partial_data = {"is_active": False}
        
        response = client.patch(
            f"/api/v1/employee/{employee_id}/documents/99999",
            json=partial_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Document not found" in response.json()["detail"]

    def test_delete_document_requires_authentication(
        self, client: TestClient, employee_id: int
    ):
        """Test that deleting document requires authentication."""
        response = client.delete(f"/api/v1/employee/{employee_id}/documents/99999")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_document_success(
        self, client: TestClient, auth_headers: dict, employee_with_documents: int
    ):
        """Test successfully deleting document."""
        response = client.delete(
            f"/api/v1/employee/{employee_with_documents}/documents/1",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify document is deleted
        get_response = client.get(
            f"/api/v1/employee/{employee_with_documents}/documents/1",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_document_not_found(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test deleting non-existent document."""
        response = client.delete(
            f"/api/v1/employee/{employee_id}/documents/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Document not found" in response.json()["detail"]

    def test_documents_data_masking(
        self, client: TestClient, auth_headers: dict, employee_with_documents: int
    ):
        """Test that sensitive data is properly masked in responses."""
        response = client.get(
            f"/api/v1/employee/{employee_with_documents}/documents",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) > 0
        
        for document in data:
            # Verify file path is masked
            assert document["file_path"].startswith("*****")
            # Verify last part of path is visible
            assert len(document["file_path"]) > 5

    def test_documents_file_size_handling(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test that file size is handled correctly."""
        # First create a document
        create_data = {
            "document_type": "CONTRACT",
            "file_name": "contract.pdf",
            "file_path": "/uploads/contract.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf",
            "is_active": True
        }
        
        create_response = client.post(
            f"/api/v1/employee/{employee_id}/documents",
            json=create_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        document_id = create_response.json()["id"]
        
        # Now update with large file size
        update_data = {
            "document_type": "LARGE_FILE",
            "file_name": "large_document.pdf",
            "file_path": "/uploads/large_document.pdf",
            "file_size": 1073741824,  # 1GB
            "mime_type": "application/pdf",
            "is_active": True
        }
        
        response = client.put(
            f"/api/v1/employee/{employee_id}/documents/{document_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["file_size"] == 1073741824

    def test_documents_complete_workflow(
        self, client: TestClient, auth_headers: dict, employee_id: int
    ):
        """Test complete document workflow: create, get, update, partial update, delete."""
        # 1. Create document using POST
        document_data = {
            "document_type": "CONTRACT",
            "file_name": "employment_contract.pdf",
            "file_path": "/uploads/contracts/emp_contract.pdf",
            "file_size": 2048576,
            "mime_type": "application/pdf",
            "is_active": True
        }
        
        create_response = client.post(
            f"/api/v1/employee/{employee_id}/documents",
            json=document_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        document_id = create_response.json()["id"]
        
        # 2. Get all documents
        get_all_response = client.get(
            f"/api/v1/employee/{employee_id}/documents",
            headers=auth_headers
        )
        assert get_all_response.status_code == status.HTTP_200_OK
        documents = get_all_response.json()
        assert len(documents) == 1
        
        # 3. Get specific document
        get_specific_response = client.get(
            f"/api/v1/employee/{employee_id}/documents/{document_id}",
            headers=auth_headers
        )
        assert get_specific_response.status_code == status.HTTP_200_OK
        data = get_specific_response.json()
        assert data["document_type"] == "CONTRACT"
        
        # 4. Full update
        updated_data = document_data.copy()
        updated_data["document_type"] = "CERTIFICATE"
        updated_data["file_name"] = "professional_cert.pdf"
        
        update_response = client.put(
            f"/api/v1/employee/{employee_id}/documents/{document_id}",
            json=updated_data,
            headers=auth_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        # 5. Partial update
        partial_data = {"is_active": False}
        patch_response = client.patch(
            f"/api/v1/employee/{employee_id}/documents/{document_id}",
            json=partial_data,
            headers=auth_headers
        )
        assert patch_response.status_code == status.HTTP_200_OK
        
        # 6. Verify changes
        final_response = client.get(
            f"/api/v1/employee/{employee_id}/documents/{document_id}",
            headers=auth_headers
        )
        assert final_response.status_code == status.HTTP_200_OK
        final_data = final_response.json()
        assert final_data["document_type"] == "CERTIFICATE"
        assert final_data["file_name"] == "professional_cert.pdf"
        assert final_data["is_active"] is False
        
        # 7. Delete document
        delete_response = client.delete(
            f"/api/v1/employee/{employee_id}/documents/{document_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 8. Verify deletion
        get_after_delete = client.get(
            f"/api/v1/employee/{employee_id}/documents/{document_id}",
            headers=auth_headers
        )
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND