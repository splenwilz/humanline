"""
Onboarding model for company setup and user preferences.

This module defines the Onboarding SQLAlchemy model for capturing
company information during the user onboarding process:
- One-to-one relationship with User model
- Company domain uniqueness for multi-tenant architecture
- Status tracking for progressive onboarding flow
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Onboarding(Base):
    """
    Onboarding model for capturing company setup information.
    
    Design principles:
    - Single table approach for cohesive onboarding data
    - Domain uniqueness constraint for tenant isolation
    - Status fields for progressive onboarding flow
    - User association for personalized experience
    """
    
    __tablename__ = "onboarding"
    
    # Primary key with auto-increment
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # User association - one onboarding per user
    # Foreign key ensures referential integrity
    # unique=True enforces one-to-one relationship
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True,
        comment="Associated user ID - one onboarding per user"
    )
    
    # Company information fields
    # These directly map to frontend form structure
    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Company name as entered by user"
    )
    
    # Company domain with uniqueness constraint
    # Critical for multi-tenant architecture - prevents subdomain conflicts
    # Index for fast domain lookups during validation
    company_domain: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Company subdomain (unique across all tenants)"
    )
    
    # Company size selection from predefined options
    company_size: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Company size category (1-10, 11-50, etc.)"
    )
    
    # Industry selection for business context
    company_industry: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Company industry (predefined or custom)"
    )
    
    # User role within the company
    company_roles: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="User's role in the company (predefined or custom)"
    )
    
    # Primary use case for the HR system
    your_needs: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Primary HR system use case (predefined or custom)"
    )
    
    # Status tracking fields
    # Enables progressive onboarding and prevents duplicate submissions
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether onboarding process is completed"
    )
    
    # Workspace creation status for future extension
    # Placeholder for workspace setup functionality
    workspace_created: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether company workspace has been created"
    )
    
    # Audit timestamps for tracking
    # timezone.utc ensures consistent timezone handling
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Onboarding creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Last onboarding update timestamp"
    )
    
    # Relationship to User model
    # Enables easy access to user data from onboarding record
    user: Mapped["User"] = relationship("User", back_populates="onboarding")
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Onboarding(id={self.id}, user_id={self.user_id}, domain='{self.company_domain}')>"
    
    @property
    def full_domain(self) -> str:
        """Get the full domain with hrline.com suffix."""
        return f"{self.company_domain}.hrline.com"
