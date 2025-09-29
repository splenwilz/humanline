"""
User service for user management operations.

This service handles user CRUD operations and business logic,
providing a clean interface between API endpoints and database models.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import time
import logging

from models.user import User
from schemas.user import UserCreate, UserUpdate
from core.security import get_password_hash
from middleware.profiler import time_operation

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user management operations."""
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID to search for
            
        Returns:
            User model if found, None otherwise
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: Email address to search for
            
        Returns:
            User model if found, None otherwise
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Create a new user account.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user model
            
        Raises:
            ValueError: If email already exists
        """
        start_time = time.perf_counter()
        logger.info(f"🔄 Starting user creation for: {user_data.email}")
        
        # Check if email already exists (optimized query)
        email_start = time.perf_counter()
        email_check = await db.execute(
            select(User.id).where(User.email == user_data.email).limit(1)
        )
        email_time = time.perf_counter() - email_start
        logger.info(f"📧 Email check completed in: {email_time:.3f}s")
        
        if email_check.scalar_one_or_none():
            raise ValueError("Email already registered")
        
        # Hash password before storing
        hash_start = time.perf_counter()
        hashed_password = get_password_hash(user_data.password)
        hash_time = time.perf_counter() - hash_start
        logger.info(f"🔐 Password hashing completed in: {hash_time:.3f}s")
        
        # Create new user with immediate return of ID
        create_start = time.perf_counter()
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        
        db.add(db_user)
        create_time = time.perf_counter() - create_start
        logger.info(f"👤 User object creation in: {create_time:.3f}s")
        
        # Commit to database
        commit_start = time.perf_counter()
        await db.commit()
        commit_time = time.perf_counter() - commit_start
        logger.info(f"💾 Database commit completed in: {commit_time:.3f}s")
        
        total_time = time.perf_counter() - start_time
        logger.info(f"✅ Total user creation time: {total_time:.3f}s")
        
        return db_user
    
    @staticmethod
    async def update_user(
        db: AsyncSession, 
        user_id: int, 
        user_data: UserUpdate
    ) -> Optional[User]:
        """
        Update user information.
        
        Args:
            db: Database session
            user_id: ID of user to update
            user_data: Updated user data
            
        Returns:
            Updated user model if found, None otherwise
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
        """
        Deactivate user account (soft delete).
        
        Args:
            db: Database session
            user_id: ID of user to deactivate
            
        Returns:
            True if user was deactivated, False if not found
        """
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        await db.commit()
        
        return True
