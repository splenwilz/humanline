"""
Unit tests for onboarding Pydantic schemas.

Tests validation logic, field constraints, and data transformation
for all onboarding-related schemas. These tests ensure data integrity
and proper error handling at the schema level.

Following FastAPI testing patterns from:
https://fastapi.tiangolo.com/tutorial/testing/
"""

import pytest
from pydantic import ValidationError

from schemas.onboarding import (
    OnboardingRequest,
    OnboardingResponse, 
    OnboardingDetail,
    OnboardingStatus
)


class TestOnboardingRequest:
    """Test OnboardingRequest schema validation and business rules."""
    
    def test_valid_onboarding_request(self):
        """Test creation with all valid data."""
        data = {
            "company_name": "Test Company Inc",
            "company_domain": "testcompany",
            "company_size": "1-10",
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
        
        request = OnboardingRequest(**data)
        
        # Verify all fields are set correctly
        assert request.company_name == "Test Company Inc"
        assert request.company_domain == "testcompany"
        assert request.company_size == "1-10"
        assert request.company_industry == "fintech"
        assert request.company_roles == "ceo-founder-owner"
        assert request.your_needs == "onboarding-new-employees"
    
    def test_company_name_validation(self):
        """Test company name field validation rules."""
        base_data = {
            "company_name": "Valid Company",
            "company_domain": "validcompany",
            "company_size": "1-10",
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
        
        # Valid names
        valid_names = [
            "A",  # Minimum length (2 chars, but edge case)
            "AB",  # Exactly minimum length
            "Test Company Inc.",
            "Company with Numbers 123",
            "Company-with-Hyphens",
            "Company with Special Chars & Co.",
            "A" * 255  # Maximum length
        ]
        
        for name in valid_names:
            data = {**base_data, "company_name": name}
            if len(name) >= 2:  # Only test names that meet minimum requirement
                request = OnboardingRequest(**data)
                assert request.company_name == name
        
        # Invalid names
        invalid_names = [
            "",  # Empty
            "A",  # Too short (less than 2 chars)
            "A" * 256  # Too long (more than 255 chars)
        ]
        
        for name in invalid_names:
            data = {**base_data, "company_name": name}
            with pytest.raises(ValidationError) as exc_info:
                OnboardingRequest(**data)
            
            # Verify error is about company_name field
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("company_name",) for error in errors)
    
    def test_company_domain_validation(self):
        """Test company domain validation with comprehensive rules."""
        base_data = {
            "company_name": "Test Company",
            "company_domain": "valid",
            "company_size": "1-10", 
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
        
        # Valid domains
        valid_domains = [
            "abc",  # Minimum valid length
            "test",
            "testcompany",
            "test-company",  # Hyphens allowed
            "company123",  # Numbers allowed
            "a1b2c3",  # Mixed alphanumeric
            "test-company-123",  # Multiple hyphens
            "a" * 50  # Maximum length
        ]
        
        for domain in valid_domains:
            data = {**base_data, "company_domain": domain}
            request = OnboardingRequest(**data)
            # Domain should be normalized to lowercase
            assert request.company_domain == domain.lower()
        
        # Test case normalization
        mixed_case_domains = [
            ("TestCompany", "testcompany"),
            ("TEST-COMPANY", "test-company"),
            ("MixedCase123", "mixedcase123")
        ]
        
        for input_domain, expected_domain in mixed_case_domains:
            data = {**base_data, "company_domain": input_domain}
            request = OnboardingRequest(**data)
            assert request.company_domain == expected_domain
        
        # Invalid domains
        invalid_domains = [
            "",  # Empty
            "ab",  # Too short (less than 3 chars)
            "a" * 51,  # Too long (more than 50 chars)
            "-invalid",  # Starts with hyphen
            "invalid-",  # Ends with hyphen
            "invalid--domain",  # Consecutive hyphens
            "invalid.domain",  # Dots not allowed
            "invalid_domain",  # Underscores not allowed
            "invalid domain",  # Spaces not allowed
            "invalid@domain",  # Special chars not allowed
            "invalid!domain",  # Exclamation not allowed
        ]
        
        for domain in invalid_domains:
            data = {**base_data, "company_domain": domain}
            with pytest.raises(ValidationError) as exc_info:
                OnboardingRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("company_domain",) for error in errors)
    
    def test_reserved_domain_validation(self):
        """Test that reserved domains are rejected."""
        base_data = {
            "company_name": "Test Company",
            "company_domain": "www",  # Reserved
            "company_size": "1-10",
            "company_industry": "fintech", 
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
        
        reserved_domains = ["www", "api", "admin", "app", "mail", "ftp", "blog"]
        
        for domain in reserved_domains:
            data = {**base_data, "company_domain": domain}
            with pytest.raises(ValidationError) as exc_info:
                OnboardingRequest(**data)
            
            errors = exc_info.value.errors()
            error_messages = [error["msg"] for error in errors]
            assert any("reserved" in msg.lower() for msg in error_messages)
    
    def test_company_size_validation(self):
        """Test company size enum validation."""
        base_data = {
            "company_name": "Test Company",
            "company_domain": "testcompany",
            "company_size": "1-10",
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner", 
            "your_needs": "onboarding-new-employees"
        }
        
        # Valid sizes
        valid_sizes = ["1-10", "11-50", "51-100", "101-200", "201-500", "500+"]
        
        for size in valid_sizes:
            data = {**base_data, "company_size": size}
            request = OnboardingRequest(**data)
            assert request.company_size == size
        
        # Invalid sizes
        invalid_sizes = ["", "1-5", "small", "large", "0-10", "501+"]
        
        for size in invalid_sizes:
            data = {**base_data, "company_size": size}
            with pytest.raises(ValidationError) as exc_info:
                OnboardingRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("company_size",) for error in errors)
    
    def test_company_industry_validation(self):
        """Test company industry enum validation."""
        base_data = {
            "company_name": "Test Company",
            "company_domain": "testcompany", 
            "company_size": "1-10",
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
        
        # Valid industries (predefined and custom)
        valid_industries = [
            "crypto", "ecommerce", "fintech", 
            "health-tech", "software-outsourcing", "Custom Industry Type", "AI/ML"
        ]
        
        for industry in valid_industries:
            data = {**base_data, "company_industry": industry}
            request = OnboardingRequest(**data)
            assert request.company_industry == industry
        
        # Invalid industries (only empty strings are invalid now)
        invalid_industries = ["", "   ", "\t\n"]
        
        for industry in invalid_industries:
            data = {**base_data, "company_industry": industry}
            with pytest.raises(ValidationError) as exc_info:
                OnboardingRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("company_industry",) for error in errors)
    
    def test_company_roles_validation(self):
        """Test company roles enum validation."""
        base_data = {
            "company_name": "Test Company",
            "company_domain": "testcompany",
            "company_size": "1-10",
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
        
        # Valid roles (predefined and custom)
        valid_roles = [
            "ceo-founder-owner", "hr-manager", "hr-staff",
            "it-tech-manager", "it-tech-staff", "Custom Role Title", "Product Manager"
        ]
        
        for role in valid_roles:
            data = {**base_data, "company_roles": role}
            request = OnboardingRequest(**data)
            assert request.company_roles == role
        
        # Invalid roles (only empty strings are invalid now)
        invalid_roles = ["", "   ", "\t\n"]
        
        for role in invalid_roles:
            data = {**base_data, "company_roles": role}
            with pytest.raises(ValidationError) as exc_info:
                OnboardingRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("company_roles",) for error in errors)
    
    def test_your_needs_validation(self):
        """Test your needs enum validation."""
        base_data = {
            "company_name": "Test Company",
            "company_domain": "testcompany",
            "company_size": "1-10", 
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
        
        # Valid needs (predefined and custom)
        valid_needs = [
            "onboarding-new-employees", "online-time-tracking",
            "performance-management", "employee-engagement", "recruitment", 
            "Custom HR Need", "Compliance Management"
        ]
        
        for need in valid_needs:
            data = {**base_data, "your_needs": need}
            request = OnboardingRequest(**data)
            assert request.your_needs == need
        
        # Invalid needs (only empty strings are invalid now)
        invalid_needs = ["", "   ", "\t\n"]
        
        for need in invalid_needs:
            data = {**base_data, "your_needs": need}
            with pytest.raises(ValidationError) as exc_info:
                OnboardingRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("your_needs",) for error in errors)
    
    def test_custom_industry_validation(self):
        """Test that custom industry strings are accepted directly."""
        base_data = {
            "company_name": "Test Company",
            "company_domain": "testcompany",
            "company_size": "1-10",
            "company_industry": "Custom Industry Type",
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
        
        # Valid: Custom industry string
        request = OnboardingRequest(**base_data)
        assert request.company_industry == "Custom Industry Type"
        
        # Valid: Predefined industry
        predefined_data = {**base_data, "company_industry": "fintech"}
        request = OnboardingRequest(**predefined_data)
        assert request.company_industry == "fintech"
        
        # Invalid: Empty industry
        with pytest.raises(ValidationError) as exc_info:
            OnboardingRequest(**{**base_data, "company_industry": ""})
        assert "Company industry cannot be empty" in str(exc_info.value)
    
    def test_custom_role_validation(self):
        """Test that custom role strings are accepted directly."""
        base_data = {
            "company_name": "Test Company",
            "company_domain": "testcompany",
            "company_size": "1-10",
            "company_industry": "fintech",
            "company_roles": "Custom Role Title",
            "your_needs": "onboarding-new-employees"
        }
        
        # Valid: Custom role string
        request = OnboardingRequest(**base_data)
        assert request.company_roles == "Custom Role Title"
        
        # Valid: Predefined role
        predefined_data = {**base_data, "company_roles": "ceo-founder-owner"}
        request = OnboardingRequest(**predefined_data)
        assert request.company_roles == "ceo-founder-owner"
        
        # Invalid: Empty role
        with pytest.raises(ValidationError) as exc_info:
            OnboardingRequest(**{**base_data, "company_roles": ""})
        assert "Company role cannot be empty" in str(exc_info.value)
    
    def test_custom_needs_validation(self):
        """Test that custom needs strings are accepted directly."""
        base_data = {
            "company_name": "Test Company",
            "company_domain": "testcompany",
            "company_size": "1-10",
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner",
            "your_needs": "Custom HR Need"
        }
        
        # Valid: Custom needs string
        request = OnboardingRequest(**base_data)
        assert request.your_needs == "Custom HR Need"
        
        # Valid: Predefined needs
        predefined_data = {**base_data, "your_needs": "onboarding-new-employees"}
        request = OnboardingRequest(**predefined_data)
        assert request.your_needs == "onboarding-new-employees"
        
        # Invalid: Empty needs
        with pytest.raises(ValidationError) as exc_info:
            OnboardingRequest(**{**base_data, "your_needs": ""})
        assert "Your needs cannot be empty" in str(exc_info.value)
    
    def test_multiple_custom_fields(self):
        """Test validation when multiple custom strings are used."""
        data = {
            "company_name": "Test Company",
            "company_domain": "testcompany",
            "company_size": "1-10",
            "company_industry": "AI/Machine Learning",
            "company_roles": "Chief AI Officer",
            "your_needs": "AI Model Training & Deployment"
        }
        
        request = OnboardingRequest(**data)
        assert request.company_industry == "AI/Machine Learning"
        assert request.company_roles == "Chief AI Officer"
        assert request.your_needs == "AI Model Training & Deployment"
    
    def test_missing_required_fields(self):
        """Test that all fields are required."""
        required_fields = [
            "company_name", "company_domain", "company_size",
            "company_industry", "company_roles", "your_needs"
        ]
        
        base_data = {
            "company_name": "Test Company",
            "company_domain": "testcompany",
            "company_size": "1-10",
            "company_industry": "fintech", 
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees"
        }
        
        # Test each field is required
        for field in required_fields:
            data = base_data.copy()
            del data[field]  # Remove required field
            
            with pytest.raises(ValidationError) as exc_info:
                OnboardingRequest(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == (field,) for error in errors)
            assert any(error["type"] == "missing" for error in errors)


class TestOnboardingResponse:
    """Test OnboardingResponse schema structure and defaults."""
    
    def test_valid_response_creation(self):
        """Test creating valid response with all fields."""
        data = {
            "success": True,
            "message": "Onboarding completed successfully!",
            "onboarding_id": 123,
            "workspace_created": False,
            "company_domain": "testcompany",
            "full_domain": "testcompany.hrline.com"
        }
        
        response = OnboardingResponse(**data)
        
        assert response.success is True
        assert response.message == "Onboarding completed successfully!"
        assert response.onboarding_id == 123
        assert response.workspace_created is False
        assert response.company_domain == "testcompany"
        assert response.full_domain == "testcompany.hrline.com"
    
    def test_default_values(self):
        """Test default values for optional fields."""
        minimal_data = {
            "message": "Success",
            "onboarding_id": 1,
            "company_domain": "test",
            "full_domain": "test.hrline.com"
        }
        
        response = OnboardingResponse(**minimal_data)
        
        # Test defaults
        assert response.success is True  # Default value
        assert response.workspace_created is False  # Default value


class TestOnboardingDetail:
    """Test OnboardingDetail schema for GET responses."""
    
    def test_complete_detail_creation(self):
        """Test creating complete onboarding detail."""
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        
        data = {
            "onboarding_id": 1,
            "user_id": 123,
            "company_name": "Test Company",
            "company_domain": "testcompany", 
            "company_size": "1-10",
            "company_industry": "fintech",
            "company_roles": "ceo-founder-owner",
            "your_needs": "onboarding-new-employees",
            "onboarding_completed": True,
            "workspace_created": False,
            "full_domain": "testcompany.hrline.com",
            "created_at": now,
            "updated_at": now
        }
        
        detail = OnboardingDetail(**data)
        
        # Verify all fields
        assert detail.onboarding_id == 1
        assert detail.user_id == 123
        assert detail.company_name == "Test Company"
        assert detail.company_domain == "testcompany"
        assert detail.full_domain == "testcompany.hrline.com"
        assert detail.created_at == now
        assert detail.updated_at == now


class TestOnboardingStatus:
    """Test OnboardingStatus schema for lightweight status checks."""
    
    def test_status_with_onboarding(self):
        """Test status when user has onboarding."""
        data = {
            "has_onboarding": True,
            "onboarding_completed": True,
            "workspace_created": False,
            "company_domain": "testcompany"
        }
        
        status = OnboardingStatus(**data)
        
        assert status.has_onboarding is True
        assert status.onboarding_completed is True
        assert status.workspace_created is False
        assert status.company_domain == "testcompany"
    
    def test_status_without_onboarding(self):
        """Test status when user has no onboarding."""
        data = {
            "has_onboarding": False
        }
        
        status = OnboardingStatus(**data)
        
        assert status.has_onboarding is False
        assert status.onboarding_completed is False  # Default
        assert status.workspace_created is False  # Default
        assert status.company_domain is None  # Default
    
    def test_default_values(self):
        """Test default values for optional fields."""
        minimal_data = {"has_onboarding": True}
        
        status = OnboardingStatus(**minimal_data)
        
        assert status.onboarding_completed is False
        assert status.workspace_created is False
        assert status.company_domain is None
