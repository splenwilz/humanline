"""
Unit tests for Onboarding model.

Tests model behavior, properties, and relationships without database operations.
Focuses on model-specific logic and computed properties.
"""

import pytest
from datetime import datetime, timezone

from models.onboarding import Onboarding


class TestOnboardingModel:
    """Test Onboarding model behavior and properties."""
    
    def test_onboarding_creation(self):
        """Test creating onboarding instance with all fields."""
        now = datetime.now(timezone.utc)
        
        onboarding = Onboarding(
            user_id=123,
            company_name="Test Company",
            company_domain="testcompany",
            company_size="1-10",
            company_industry="fintech",
            company_roles="ceo-founder-owner",
            your_needs="onboarding-new-employees",
            onboarding_completed=True,
            workspace_created=False,
            created_at=now,
            updated_at=now
        )
        
        # Verify all fields are set correctly
        assert onboarding.user_id == 123
        assert onboarding.company_name == "Test Company"
        assert onboarding.company_domain == "testcompany"
        assert onboarding.company_size == "1-10"
        assert onboarding.company_industry == "fintech"
        assert onboarding.company_roles == "ceo-founder-owner"
        assert onboarding.your_needs == "onboarding-new-employees"
        assert onboarding.onboarding_completed is True
        assert onboarding.workspace_created is False
        assert onboarding.created_at == now
        assert onboarding.updated_at == now
    
    def test_full_domain_property(self):
        """Test full_domain computed property."""
        onboarding = Onboarding(
            user_id=123,
            company_name="Test Company",
            company_domain="testcompany",
            company_size="1-10",
            company_industry="fintech",
            company_roles="ceo-founder-owner",
            your_needs="onboarding-new-employees"
        )
        
        assert onboarding.full_domain == "testcompany.hrline.com"
    
    def test_full_domain_property_with_different_domains(self):
        """Test full_domain property with various domain formats."""
        test_cases = [
            ("simple", "simple.hrline.com"),
            ("with-hyphens", "with-hyphens.hrline.com"),
            ("with123numbers", "with123numbers.hrline.com"),
            ("a", "a.hrline.com"),
            ("verylongdomainname", "verylongdomainname.hrline.com")
        ]
        
        for domain, expected_full_domain in test_cases:
            onboarding = Onboarding(
                user_id=123,
                company_name="Test Company",
                company_domain=domain,
                company_size="1-10",
                company_industry="fintech",
                company_roles="ceo-founder-owner",
                your_needs="onboarding-new-employees"
            )
            
            assert onboarding.full_domain == expected_full_domain
    
    def test_repr_method(self):
        """Test string representation of onboarding."""
        onboarding = Onboarding(
            id=456,
            user_id=123,
            company_name="Test Company",
            company_domain="testcompany",
            company_size="1-10",
            company_industry="fintech",
            company_roles="ceo-founder-owner",
            your_needs="onboarding-new-employees"
        )
        
        repr_str = repr(onboarding)
        
        assert "Onboarding" in repr_str
        assert "id=456" in repr_str
        assert "user_id=123" in repr_str
        assert "domain='testcompany'" in repr_str
    
    def test_default_values(self):
        """Test default values for boolean fields."""
        onboarding = Onboarding(
            user_id=123,
            company_name="Test Company",
            company_domain="testcompany",
            company_size="1-10",
            company_industry="fintech",
            company_roles="ceo-founder-owner",
            your_needs="onboarding-new-employees"
        )
        
        # Test default values (SQLAlchemy sets these when not explicitly provided)
        # When not set, they should be None initially, but the column defaults will apply in DB
        assert onboarding.onboarding_completed is None or onboarding.onboarding_completed is False
        assert onboarding.workspace_created is None or onboarding.workspace_created is False
    
    def test_tablename(self):
        """Test that table name is set correctly."""
        assert Onboarding.__tablename__ == "onboarding"
