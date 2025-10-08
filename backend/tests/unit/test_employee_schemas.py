"""
Unit tests for employee Pydantic schemas.

Tests validation logic, field constraints, and data transformation
for all employee-related schemas. These tests ensure data integrity
and proper error handling at the schema level.

Following FastAPI testing patterns from:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import pytest
from pydantic import ValidationError
from datetime import date, datetime, timezone

from schemas.employee import (
    EmployeeRequest, EmployeeResponse, EmployeeFullRequest, EmployeeFullResponse,
    EmployeePersonalDetailsRequest, EmployeePersonalDetailsResponse,
    EmployeeJobTimelineRequest, EmployeeJobTimelineResponse,
    EmployeeBankInfoRequest, EmployeeBankInfoResponse,
    EmployeeDependentRequest, EmployeeDependentResponse,
    EmployeeDocumentRequest, EmployeeDocumentResponse
)


class TestEmployeeRequest:
    """Test EmployeeRequest schema validation and business rules."""
    
    def test_valid_employee_request(self):
        """Test creation with all valid data."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15"
        }
        
        request = EmployeeRequest(**data)
        
        # Verify all fields are set correctly
        assert request.first_name == "John"
        assert request.last_name == "Doe"
        assert request.email == "john.doe@example.com"
        assert request.phone == "(555) 123-4567"
        assert request.join_date == date(2024, 1, 15)
    
    def test_name_validation(self):
        """Test name field validation rules."""
        base_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15"
        }
        
        # Valid names
        valid_names = [
            "John",
            "Mary-Jane",
            "O'Connor",
            "Jean-Luc",
            "José",
            "A" * 50  # Maximum length
        ]
        
        for name in valid_names:
            data = {**base_data, "first_name": name}
            request = EmployeeRequest(**data)
            assert request.first_name == name.title()  # Should be title-cased
        
        # Invalid names
        invalid_names = [
            "",  # Empty
            "A" * 51,  # Too long
            "John123",  # Numbers not allowed
            "John@Doe",  # Special chars not allowed
            "John_Doe",  # Underscores not allowed
        ]
        
        for name in invalid_names:
            data = {**base_data, "first_name": name}
            with pytest.raises(ValidationError) as exc_info:
                EmployeeRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("first_name",) for error in errors)
    
    def test_phone_validation(self):
        """Test phone number validation and formatting."""
        base_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15"
        }
        
        # Valid phone numbers
        valid_phones = [
            "5551234567",  # 10 digits
            "(555) 123-4567",  # Formatted
            "555-123-4567",  # Dashes
            "555.123.4567",  # Dots
            "+1 555 123 4567",  # International
            "123456789012345",  # 15 digits max
        ]
        
        for phone in valid_phones:
            data = {**base_data, "phone": phone}
            request = EmployeeRequest(**data)
            # Should be formatted if 10 digits
            if len(phone.replace("(", "").replace(")", "").replace("-", "").replace(".", "").replace(" ", "").replace("+", "")) == 10:
                assert request.phone == "(555) 123-4567"  # Formatted
            else:
                assert request.phone == phone.strip()  # As-is
        
        # Invalid phone numbers
        invalid_phones = [
            "123",  # Too short
            "1234567890123456",  # Too long
            "abc-def-ghij",  # Letters
            "555-123",  # Too short
        ]
        
        for phone in invalid_phones:
            data = {**base_data, "phone": phone}
            with pytest.raises(ValidationError) as exc_info:
                EmployeeRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("phone",) for error in errors)
    
    def test_email_validation(self):
        """Test email validation."""
        base_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15"
        }
        
        # Valid emails
        valid_emails = [
            "john@example.com",
            "john.doe@company.co.uk",
            "user+tag@domain.org",
            "test123@subdomain.example.com"
        ]
        
        for email in valid_emails:
            data = {**base_data, "email": email}
            request = EmployeeRequest(**data)
            assert request.email == email
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "john@",
            "",
            "john@.com"
        ]
        
        for email in invalid_emails:
            data = {**base_data, "email": email}
            with pytest.raises(ValidationError) as exc_info:
                EmployeeRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("email",) for error in errors)
    
    def test_join_date_validation(self):
        """Test join date validation."""
        base_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15"
        }
        
        # Valid dates
        valid_dates = [
            "2024-01-15",
            "2023-12-31",
            "2024-02-29",  # Leap year
            "2020-01-01"
        ]
        
        for date_str in valid_dates:
            data = {**base_data, "join_date": date_str}
            request = EmployeeRequest(**data)
            assert request.join_date == date.fromisoformat(date_str)
        
        # Invalid dates
        invalid_dates = [
            "invalid-date",
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
            "2024-02-30",  # Invalid day for February
            "",
            "01/15/2024"  # Wrong format
        ]
        
        for date_str in invalid_dates:
            data = {**base_data, "join_date": date_str}
            with pytest.raises(ValidationError) as exc_info:
                EmployeeRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("join_date",) for error in errors)


class TestEmployeePersonalDetailsRequest:
    """Test EmployeePersonalDetailsRequest schema validation."""
    
    def test_valid_personal_details(self):
        """Test creation with all valid data."""
        data = {
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
        
        request = EmployeePersonalDetailsRequest(**data)
        
        assert request.gender == "MALE"
        assert request.date_of_birth == date(1990, 1, 15)
        assert request.nationality == "American"
        assert request.marital_status == "SINGLE"
    
    def test_gender_validation(self):
        """Test gender field validation."""
        base_data = {
            "gender": "MALE",
            "date_of_birth": "1990-01-15",
            "nationality": "American"
        }
        
        # Valid genders
        valid_genders = ["MALE", "FEMALE", "OTHER", "PREFER_NOT_TO_SAY"]
        
        for gender in valid_genders:
            data = {**base_data, "gender": gender}
            request = EmployeePersonalDetailsRequest(**data)
            assert request.gender == gender
        
        # Invalid genders (empty string should be converted to None, not raise error)
        invalid_genders = ["male", "female", "Male", "INVALID"]
        
        for gender in invalid_genders:
            data = {**base_data, "gender": gender}
            with pytest.raises(ValidationError) as exc_info:
                EmployeePersonalDetailsRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("gender",) for error in errors)
        
        # Test empty string is converted to None
        data = {**base_data, "gender": ""}
        request = EmployeePersonalDetailsRequest(**data)
        assert request.gender is None
    
    def test_marital_status_validation(self):
        """Test marital status field validation."""
        base_data = {
            "gender": "MALE",
            "date_of_birth": "1990-01-15",
            "marital_status": "SINGLE"
        }
        
        # Valid marital statuses
        valid_statuses = ["SINGLE", "MARRIED", "DIVORCED", "WIDOWED", "SEPARATED"]
        
        for status in valid_statuses:
            data = {**base_data, "marital_status": status}
            request = EmployeePersonalDetailsRequest(**data)
            assert request.marital_status == status
        
        # Invalid marital statuses (empty string should be converted to None, not raise error)
        invalid_statuses = ["single", "Single", "INVALID"]
        
        for status in invalid_statuses:
            data = {**base_data, "marital_status": status}
            with pytest.raises(ValidationError) as exc_info:
                EmployeePersonalDetailsRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("marital_status",) for error in errors)
        
        # Test empty string is converted to None
        data = {**base_data, "marital_status": ""}
        request = EmployeePersonalDetailsRequest(**data)
        assert request.marital_status is None


class TestEmployeeJobTimelineRequest:
    """Test EmployeeJobTimelineRequest schema validation."""
    
    def test_valid_job_timeline(self):
        """Test creation with all valid data."""
        data = {
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
        
        request = EmployeeJobTimelineRequest(**data)
        
        assert request.effective_date == date(2024, 1, 15)
        assert request.end_date == date(2024, 12, 31)
        assert request.job_title == "Software Engineer"
        assert request.employment_type == "FULL_TIME"
        assert request.is_current is True
    
    def test_employment_type_validation(self):
        """Test employment type field validation."""
        base_data = {
            "effective_date": "2024-01-15",
            "job_title": "Software Engineer",
            "employment_type": "FULL_TIME",
            "department": "Engineering",
            "office": "New York"
        }
        
        # Valid employment types
        valid_types = ["FULL_TIME", "PART_TIME", "CONTRACT", "INTERNSHIP", "TEMPORARY"]
        
        for emp_type in valid_types:
            data = {**base_data, "employment_type": emp_type}
            request = EmployeeJobTimelineRequest(**data)
            assert request.employment_type == emp_type
        
        # Invalid employment types
        invalid_types = ["full_time", "Full Time", "INVALID", ""]
        
        for emp_type in invalid_types:
            data = {**base_data, "employment_type": emp_type}
            with pytest.raises(ValidationError) as exc_info:
                EmployeeJobTimelineRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("employment_type",) for error in errors)


class TestEmployeeBankInfoRequest:
    """Test EmployeeBankInfoRequest schema validation."""
    
    def test_valid_bank_info(self):
        """Test creation with all valid data."""
        data = {
            "bank_name": "Chase Bank",
            "account_number": "1234567890",
            "routing_number": "021000021",
            "account_type": "CHECKING",
            "account_holder_name": "John Doe",
            "account_holder_type": "INDIVIDUAL",
            "is_primary": True,
            "is_active": True
        }
        
        request = EmployeeBankInfoRequest(**data)
        
        assert request.bank_name == "Chase Bank"
        assert request.account_number == "1234567890"
        assert request.routing_number == "021000021"
        assert request.is_primary is True
        assert request.is_active is True


class TestEmployeeDependentRequest:
    """Test EmployeeDependentRequest schema validation."""
    
    def test_valid_dependent(self):
        """Test creation with all valid data."""
        data = {
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
        
        request = EmployeeDependentRequest(**data)
        
        assert request.name == "Jane Doe"
        assert request.relationship_type == "SPOUSE"
        assert request.date_of_birth == date(1992, 5, 20)
        assert request.is_active is True
    
    def test_relationship_type_validation(self):
        """Test relationship type field validation."""
        base_data = {
            "name": "Jane Doe",
            "relationship_type": "SPOUSE"
        }
        
        # Valid relationship types
        valid_types = ["SPOUSE", "CHILD", "PARENT", "SIBLING", "OTHER"]
        
        for rel_type in valid_types:
            data = {**base_data, "relationship_type": rel_type}
            request = EmployeeDependentRequest(**data)
            assert request.relationship_type == rel_type
        
        # Invalid relationship types
        invalid_types = ["spouse", "Spouse", "INVALID", ""]
        
        for rel_type in invalid_types:
            data = {**base_data, "relationship_type": rel_type}
            with pytest.raises(ValidationError) as exc_info:
                EmployeeDependentRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("relationship_type",) for error in errors)


class TestEmployeeDocumentRequest:
    """Test EmployeeDocumentRequest schema validation."""
    
    def test_valid_document(self):
        """Test creation with all valid data."""
        data = {
            "document_type": "PASSPORT",
            "file_name": "passport.pdf",
            "file_path": "/uploads/passport_123.pdf",
            "file_size": 1024000,
            "mime_type": "application/pdf",
            "is_active": True
        }
        
        request = EmployeeDocumentRequest(**data)
        
        assert request.document_type == "PASSPORT"
        assert request.file_name == "passport.pdf"
        assert request.file_size == 1024000
        assert request.is_active is True


class TestEmployeeFullRequest:
    """Test EmployeeFullRequest schema validation."""
    
    def test_valid_full_request(self):
        """Test creation with all valid data."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15",
            "personal_details": {
                "gender": "MALE",
                "date_of_birth": "1990-01-15",
                "nationality": "American",
                "marital_status": "SINGLE"
            },
            "bank_info": {
                "bank_name": "Chase Bank",
                "account_number": "1234567890",
                "routing_number": "021000021",
                "account_type": "CHECKING",
                "account_holder_name": "John Doe",
                "account_holder_type": "INDIVIDUAL"
            },
            "job_timeline": [
                {
                    "effective_date": "2024-01-15",
                    "job_title": "Software Engineer",
                    "employment_type": "FULL_TIME",
                    "department": "Engineering",
                    "office": "New York",
                    "is_current": True
                }
            ],
            "dependents": [
                {
                    "name": "Jane Doe",
                    "relationship_type": "SPOUSE",
                    "date_of_birth": "1992-05-20"
                }
            ],
            "documents": [
                {
                    "document_type": "PASSPORT",
                    "file_name": "passport.pdf",
                    "file_path": "/uploads/passport_123.pdf",
                    "file_size": 1024000,
                    "mime_type": "application/pdf"
                }
            ]
        }
        
        request = EmployeeFullRequest(**data)
        
        assert request.first_name == "John"
        assert request.last_name == "Doe"
        assert request.personal_details is not None
        assert request.bank_info is not None
        assert len(request.job_timeline) == 1
        assert len(request.dependents) == 1
        assert len(request.documents) == 1
    
    def test_minimal_full_request(self):
        """Test creation with only required fields."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "join_date": "2024-01-15"
        }
        
        request = EmployeeFullRequest(**data)
        
        assert request.first_name == "John"
        assert request.personal_details is None
        assert request.bank_info is None
        assert request.job_timeline == []
        assert request.dependents == []
        assert request.documents == []


class TestEmployeeResponse:
    """Test EmployeeResponse schema structure."""
    
    def test_valid_response_creation(self):
        """Test creating valid response with all fields."""
        now = datetime.now(timezone.utc)
        
        data = {
            "id": 123,
            "user_id": 456,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "join_date": date(2024, 1, 15),
            "created_at": now,
            "updated_at": now
        }
        
        response = EmployeeResponse(**data)
        
        assert response.id == 123
        assert response.user_id == 456
        assert response.first_name == "John"
        assert response.email == "john.doe@example.com"
        assert response.created_at == now


class TestEmployeeFullResponse:
    """Test EmployeeFullResponse schema structure."""
    
    def test_valid_full_response_creation(self):
        """Test creating valid full response with all fields."""
        now = datetime.now(timezone.utc)
        
        data = {
            "id": 123,
            "user_id": 456,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "join_date": date(2024, 1, 15),
            "created_at": now,
            "updated_at": now,
            "personal_details": {
                "id": 1,
                "employee_id": 123,
                "gender": "MALE",
                "date_of_birth": date(1990, 1, 15),
                "nationality": "American",
                "marital_status": "SINGLE",
                "created_at": now,
                "updated_at": now
            },
            "bank_info": {
                "id": 1,
                "employee_id": 123,
                "bank_name": "Chase Bank",
                "account_number": "1234567890",
                "routing_number": "021000021",
                "account_type": "CHECKING",
                "account_holder_name": "John Doe",
                "account_holder_type": "INDIVIDUAL",
                "is_primary": True,
                "is_active": True,
                "created_at": now,
                "updated_at": now
            },
            "job_timeline": [],
            "dependents": [],
            "documents": []
        }
        
        response = EmployeeFullResponse(**data)
        
        assert response.id == 123
        assert response.personal_details is not None
        assert response.bank_info is not None
        assert response.job_timeline == []
        assert response.dependents == []
        assert response.documents == []
