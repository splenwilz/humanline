"""
Authentication service for login, registration, and token management.

This service handles authentication business logic, including password
verification, token creation, user registration with email confirmation,
and secure account activation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest
from schemas.user import UserCreate
from core.security import verify_password, create_access_token, create_refresh_token, verify_token
from core.rbac import get_permissions_for_role
from core.config import settings
from services.user_service import UserService
from services.email_service import email_service


class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            email: User's email address
            password: Plain text password
            
        Returns:
            User model if authentication successful, None otherwise
        """
        # Get user by email
        user = await UserService.get_user_by_email(db, email)
        if not user:
            return None
        
        # Check if account is active
        if not user.is_active:
            return None
            
        # Check if email confirmation is required and user is verified
        # This prevents login with unverified accounts when confirmation is enabled
        if settings.require_email_confirmation and not user.is_verified:
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    async def login(db: AsyncSession, login_data: LoginRequest) -> Optional[TokenResponse]:
        """
        Handle user login and return JWT token.
        
        Args:
            db: Database session
            login_data: Login credentials
            
        Returns:
            TokenResponse with JWT token if successful, None otherwise
        """
        # Authenticate user
        user = await AuthService.authenticate_user(
            db, login_data.email, login_data.password
        )
        if not user:
            return None
        
        # Create access token with real user role
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={
                "sub": str(user.id), 
                "email": user.email, 
                "role": user.role,
                "is_verified": user.is_verified,
                "needs_onboarding": AuthService._determine_needs_onboarding(user)
            },
            expires_delta=access_token_expires
        )
        
        # Create refresh token with real user role
        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id), 
                "email": user.email, 
                "role": user.role,
                "is_verified": user.is_verified,
                "needs_onboarding": AuthService._determine_needs_onboarding(user)
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,  # Convert to seconds
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": f"{user.first_name} {user.last_name}".strip(),
                "role": user.role,
                "email_confirmed_at": user.updated_at.isoformat() if user.is_verified else None,
                "created_at": user.created_at.isoformat(),
                "permissions": get_permissions_for_role(user.role),
                "needs_onboarding": AuthService._determine_needs_onboarding(user)
            }
        )
    
    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Optional[TokenResponse]:
        """
        Generate new access token using valid refresh token.
        
        Args:
            db: Database session
            refresh_token: Valid refresh token
            
        Returns:
            TokenResponse with new access token if successful, None otherwise
        """
        # Verify refresh token
        token_data = verify_token(refresh_token, "refresh_token")
        if not token_data:
            return None
        
        # Get user from token
        user_id = token_data.get("sub")
        if not user_id:
            return None
        
        # Verify user still exists and is active
        user = await UserService.get_user_by_id(db, int(user_id))
        if not user or not user.is_active:
            return None
        
        # Create new access token with real user role
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={
                "sub": str(user.id), 
                "email": user.email, 
                "role": user.role,
                "is_verified": user.is_verified,
                "needs_onboarding": AuthService._determine_needs_onboarding(user)
            },
            expires_delta=access_token_expires
        )
        
        # Create new refresh token with real user role
        new_refresh_token = create_refresh_token(
            data={
                "sub": str(user.id), 
                "email": user.email, 
                "role": user.role,
                "is_verified": user.is_verified
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": f"{user.first_name} {user.last_name}".strip(),
                "role": user.role,
                "email_confirmed_at": user.updated_at.isoformat() if user.is_verified else None,
                "created_at": user.created_at.isoformat(),
                "permissions": get_permissions_for_role(user.role),
                "needs_onboarding": AuthService._determine_needs_onboarding(user)
            }
        )
    
    @staticmethod
    async def register(db: AsyncSession, register_data: RegisterRequest) -> Dict[str, Any]:
        """
        Handle user registration with optional email confirmation.
        
        This method implements a flexible registration flow:
        - If email confirmation is disabled: Creates active user and returns JWT token
        - If email confirmation is enabled: Creates inactive user and sends confirmation email
        
        Args:
            db: Database session
            register_data: Registration data
            
        Returns:
            Dict containing either:
            - TokenResponse (if confirmation disabled)
            - Confirmation message (if confirmation enabled)
            
        Raises:
            ValueError: If email already exists or validation fails
        """
        # Create user data object with registration information
        # This standardizes the data format for user creation
        user_data = UserCreate(
            email=register_data.email,
            password=register_data.password,
            first_name=register_data.first_name,
            last_name=register_data.last_name
        )
        
        # Check if email confirmation is required by configuration
        # This allows the feature to be toggled on/off as requested
        if settings.require_email_confirmation:
            # EMAIL CONFIRMATION FLOW
            # Create user account in inactive state pending email verification
            
            # Generate unique 6-digit verification code for email confirmation
            # Ensure uniqueness to prevent account takeover attacks
            verification_code = await AuthService._generate_unique_verification_code(db)
            code_expiration = email_service.calculate_code_expiration()
            
            # Create or update user account with email verification fields
            # UserService handles both new registrations and re-registration for unverified accounts
            user = await UserService.create_user_with_verification(
                db=db,
                user_data=user_data,
                verification_code=verification_code,
                code_expiration=code_expiration,
                is_active=False,   # Account inactive until email confirmed
                is_verified=False, # Email not verified yet
                needs_onboarding=True  # New users need onboarding
            )
            
            # Send confirmation email asynchronously
            # Email delivery failure doesn't prevent account creation
            user_display_name = f"{user.first_name} {user.last_name}".strip() or user.email
            email_sent = await email_service.send_confirmation_email(
                user_email=user.email,
                user_name=user_display_name,
                verification_code=verification_code
            )
            
            # Return confirmation message instead of JWT token
            # User must confirm email before they can login
            return {
                "type": "email_confirmation_required",
                "message": "Registration successful! Please check your email for a confirmation link.",
                "email": user.email,
                "email_sent": email_sent,
                "expires_in_hours": settings.email_confirmation_expire_hours,
                "next_step": "check_email_for_confirmation_link"
            }
            
        else:
            # IMMEDIATE ACTIVATION FLOW (original behavior)
            # Create active user account and return JWT token for immediate login
            
            # Create user account with immediate activation
            # This maintains backward compatibility when confirmation is disabled
            user = await UserService.create_user_with_verification(
                db=db,
                user_data=user_data,
                verification_code=None,  # No code needed for immediate activation
                code_expiration=None,    # No expiration needed
                is_active=True,           # Account active immediately
                is_verified=True,         # Email considered verified
                needs_onboarding=True     # New users need onboarding
            )
            
            # Create access token for immediate login with real user role
            # This provides the same experience as before when confirmation is disabled
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={
                    "sub": str(user.id), 
                    "email": user.email, 
                    "role": user.role,
                    "is_verified": user.is_verified,
                    "needs_onboarding": AuthService._determine_needs_onboarding(user)
                },
                expires_delta=access_token_expires
            )
            
            # Create refresh token with real user role
            refresh_token = create_refresh_token(
                data={
                    "sub": str(user.id), 
                    "email": user.email, 
                    "role": user.role,
                    "is_verified": user.is_verified
                }
            )
            
            # Return JWT token for immediate authentication
            # This allows seamless login after registration
            return {
                "type": "immediate_login",
                "token_response": TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=settings.access_token_expire_minutes * 60,
                    user={
                        "id": str(user.id),
                        "email": user.email,
                        "full_name": f"{user.first_name} {user.last_name}".strip(),
                        "role": user.role,
                        "email_confirmed_at": user.updated_at.isoformat() if user.is_verified else None,
                        "created_at": user.created_at.isoformat(),
                        "permissions": get_permissions_for_role(user.role),
                        "needs_onboarding": AuthService._determine_needs_onboarding(user)
                    }
                )
            }
    
    @staticmethod
    async def confirm_email(db: AsyncSession, verification_code: str) -> Dict[str, Any]:
        """
        Confirm user email address using 6-digit verification code.

        This method handles the email confirmation process:
        1. Validates the verification code exists and hasn't expired
        2. Activates the user account
        3. Marks email as verified
        4. Clears the verification code for security

        Args:
            db: Database session
            verification_code: 6-digit verification code from confirmation email

        Returns:
            Dict containing success status and user information

        Raises:
            ValueError: If code is invalid, expired, or user not found
        """
        # Find user by verification code
        # Use database query for secure code lookup with expiration check
        query = select(User).where(
            User.email_verification_code == verification_code
        )
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        # Validate code exists and user found
        # Invalid codes should not reveal whether they ever existed
        if not user:
            return {
                "success": False,
                "error": "This verification code is invalid or has already been used. If you need a new confirmation code, please sign up again."
            }

        # Check if code has expired for security
        # Expired codes must be rejected to prevent indefinite validity
        current_time = datetime.now(timezone.utc)
        if user.email_verification_expires_at and current_time > user.email_verification_expires_at:
            return {
                "success": False,
                "error": "Verification code has expired. Please request a new confirmation code."
            }
        
        # Check if user is already verified
        # This prevents unnecessary processing and provides clear feedback
        if user.is_verified:
            return {
                "success": False,
                "error": "Email address is already verified. You can login to your account."
            }
        
        # Activate user account and mark email as verified
        # This completes the registration process
        user.is_active = True
        user.is_verified = True
        
        # Clear verification code for security
        # Codes should not be reusable after successful verification
        user.email_verification_code = None
        user.email_verification_expires_at = None
        
        # Update the user's last modified timestamp
        # This provides audit trail for account activation
        user.updated_at = current_time
        
        # Commit changes to database
        # Ensure all updates are persisted atomically
        await db.commit()
        await db.refresh(user)
        
        # Return success response with user information
        # This provides confirmation details for the frontend
        return {
            "success": True,
            "user_email": user.email,
            "confirmed_at": current_time.isoformat(),
            "message": "Email confirmed successfully! Your account is now active."
        }

    @staticmethod
    async def resend_confirmation(db: AsyncSession, email: str) -> Dict[str, Any]:
        """
        Resend email confirmation code to an unverified user.

        This method handles resending verification codes:
        1. Finds the unverified user by email
        2. Generates a new unique 6-digit verification code
        3. Updates the user's verification code and expiration
        4. Sends a new confirmation email
        5. Implements basic rate limiting by checking last update time

        Args:
            db: Database session
            email: Email address to resend confirmation to

        Returns:
            Dict containing success status and message

        Raises:
            ValueError: If user not found, already verified, or rate limited
        """
        # Find user by email
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        # Validate user exists
        if not user:
            return {
                "success": False,
                "error": "No account found with this email address. Please sign up first."
            }

        # Check if user is already verified
        if user.is_verified:
            return {
                "success": False,
                "error": "This email address is already verified. You can sign in to your account."
            }

        # Basic rate limiting: prevent resend within 1 minute of last update
        # This prevents abuse while allowing legitimate resend requests
        current_time = datetime.now(timezone.utc)
        if user.updated_at:
            time_since_last_update = current_time - user.updated_at
            if time_since_last_update.total_seconds() < 60:  # 1 minute cooldown
                remaining_seconds = 60 - int(time_since_last_update.total_seconds())
                return {
                    "success": False,
                    "error": f"Please wait {remaining_seconds} seconds before requesting another confirmation code."
                }

        # Generate new unique verification code
        verification_code = await AuthService._generate_unique_verification_code(db)
        code_expiration = email_service.calculate_code_expiration()

        # Update user with new verification code and expiration
        user.email_verification_code = verification_code
        user.email_verification_expires_at = code_expiration
        user.updated_at = current_time

        # Commit the code update to database
        await db.commit()
        await db.refresh(user)

        # Send new confirmation email
        user_display_name = f"{user.first_name} {user.last_name}".strip() or user.email
        email_sent = await email_service.send_confirmation_email(
            user_email=user.email,
            user_name=user_display_name,
            verification_code=verification_code
        )

        if email_sent:
            return {
                "success": True,
                "message": "A new confirmation code has been sent to your email address.",
                "email": user.email,
                "expires_in_hours": settings.email_confirmation_expire_hours
            }
        else:
            return {
                "success": False,
                "error": "Failed to send confirmation email. Please try again later."
            }

    @staticmethod
    async def _generate_unique_verification_code(db: AsyncSession) -> str:
        """
        Generate a unique 6-digit verification code that doesn't exist in the database.
        
        This prevents account takeover attacks due to code collisions by ensuring
        each active verification code is unique across all pending registrations.
        
        Args:
            db: Database session
            
        Returns:
            str: Unique 6-digit verification code
            
        Raises:
            RuntimeError: If unable to generate unique code after max attempts
        """
        max_attempts = 10  # Prevent infinite loops
        
        for attempt in range(max_attempts):
            # Generate a candidate verification code
            candidate_code = email_service.generate_verification_code()
            
            # Check if this code is already in use by any pending verification
            existing_query = select(User).where(
                User.email_verification_code == candidate_code
            )
            existing_result = await db.execute(existing_query)
            existing_user = existing_result.scalar_one_or_none()
            
            # If no collision found, use this code
            if not existing_user:
                return candidate_code
                
            # Log collision for monitoring (in production, you might want metrics)
            print(f"Verification code collision detected on attempt {attempt + 1}: {candidate_code}")
        
        # If we couldn't generate a unique code after max attempts, this indicates
        # either a very high collision rate or a potential issue with randomness
        raise RuntimeError(
            f"Unable to generate unique verification code after {max_attempts} attempts. "
            "This may indicate high system load or insufficient entropy."
        )

    @staticmethod
    def _determine_needs_onboarding(user: User) -> bool:
        """
        Determine if a user needs to complete onboarding.
        
        This method handles the logic for both new and existing users:
        - New users: Use the needs_onboarding field if set
        - Existing users: Check if they have completed onboarding
        
        Args:
            user: User model instance
            
        Returns:
            bool: True if user needs onboarding, False otherwise
        """
        # For new users with the field set, use that value
        if user.needs_onboarding is not None:
            return user.needs_onboarding
        
        # For existing users (field is None), check if they have completed onboarding
        # This handles backward compatibility with users created before this field existed
        if hasattr(user, 'onboarding') and user.onboarding:
            return not user.onboarding.onboarding_completed
        
        # Default: existing users without onboarding record need onboarding
        return True

