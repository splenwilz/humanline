"""
User model for authentication and user management.

This module defines the User SQLAlchemy model with security considerations:
- Email uniqueness enforced at database level
- Password stored as hash only (never plain text)
- Timestamps for audit trail
- Soft delete capability for data retention
"""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class User(Base):
    """
    User model for authentication and profile management.
    
    Security features:
    - Email uniqueness constraint prevents duplicate accounts
    - Password field stores bcrypt hash only
    - is_active allows for account deactivation without deletion
    - Timestamps provide audit trail
    """
    
    __tablename__ = "users"
    
    # Primary key with auto-increment
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Email as unique identifier
    # index=True for fast lookups during authentication
    # unique=True enforced at database level for data integrity
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="User email address - unique identifier"
    )
    
    # Hashed password storage
    # Never store plain text passwords for security
    # Text type allows for longer hash strings if algorithm changes
    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Bcrypt hashed password"
    )
    
    # Optional profile fields
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="User's first name"
    )
    
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="User's last name"
    )
    
    # Account status flags
    # is_active allows for soft account deactivation
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether the user account is active"
    )
    
    # Email verification status
    # Important for security - prevents unauthorized account creation
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user's email has been verified"
    )
    
    # Role-based access control
    role: Mapped[str] = mapped_column(
        String(50),
        default="user",
        nullable=False,
        comment="User role for RBAC (admin, manager, user)"
    )
    
    # Email verification code (6-digit)
    # User-friendly verification code for email confirmation
    # Nullable because verified users don't need codes
    # Unique constraint prevents account takeover via code collisions
    email_verification_code: Mapped[str] = mapped_column(
        String(6),
        nullable=True,
        unique=True,  # Ensure uniqueness to prevent collision attacks
        index=True,   # Index for fast code lookups during verification
        comment="6-digit verification code for email confirmation"
    )
    
    # Email verification code expiration
    # Codes expire for security - prevents indefinite validity
    email_verification_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Email verification code expiration timestamp"
    )
    
    # Audit timestamps
    # timezone.utc ensures consistent timezone handling
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Account creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Last account update timestamp"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email.split("@")[0]  # Fallback to email username
