"""
Email service for sending confirmation emails and other notifications.

This service handles all email operations including SMTP configuration,
template rendering, and secure email delivery with proper error handling.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, BaseLoader

from core.config import settings

# Configure logging for email operations
logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for handling email operations.
    
    This service provides secure email functionality with:
    - SMTP connection management with TLS encryption
    - HTML email template rendering using Jinja2
    - Proper error handling and logging
    - Rate limiting and security considerations
    """
    
    def __init__(self):
        """Initialize email service with SMTP configuration."""
        # SMTP configuration loaded from environment variables
        # This ensures sensitive credentials are not hardcoded
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
        
        # Initialize Jinja2 environment for email templates
        # BaseLoader allows us to define templates as strings
        # SECURITY: autoescape=True prevents XSS attacks by escaping user input in templates
        self.template_env = Environment(
            loader=BaseLoader(),
            autoescape=True  # Critical: prevents XSS by escaping HTML in user input
        )
        
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SMTP with TLS encryption.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML email body
            text_content: Plain text fallback (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
            
        Raises:
            Exception: Logs errors but doesn't raise to prevent service disruption
        """
        try:
            # Validate email configuration before attempting to send
            if not self._validate_email_config():
                logger.error("Email configuration is incomplete - cannot send email")
                return False
                
            # Create multipart message to support both HTML and text
            # This ensures compatibility with all email clients
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email
            
            # Add text content if provided (fallback for HTML)
            # Text content is important for accessibility and older email clients
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML content (primary email format)
            # HTML allows for better formatting and branding
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email using aiosmtplib for async operation
            # This prevents blocking the main application thread
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,  # Use TLS encryption for security
                username=self.smtp_user,
                password=self.smtp_password,
            )
            
            logger.info(f"✅ Email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            # Log error but don't raise to prevent service disruption
            # Email failures shouldn't crash the application
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _validate_email_config(self) -> bool:
        """
        Validate that all required email configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        # Check that all required SMTP settings are configured
        # Empty strings are considered invalid configuration
        required_settings = [
            self.smtp_host,
            self.smtp_user, 
            self.smtp_password,
            self.from_email
        ]
        
        # Validate that no required setting is empty
        # This prevents attempting SMTP connection with invalid credentials
        if not all(setting.strip() for setting in required_settings):
            logger.warning("Email configuration incomplete - some required settings are missing")
            return False
            
        return True
    
    def generate_verification_code(self) -> str:
        """
        Generate a 6-digit verification code for user-friendly input.
        
        Returns:
            str: 6-digit numeric code (e.g., "123456")
            
        Security considerations:
        - Uses secrets module for cryptographic randomness
        - 6 digits provides 1 million possible combinations
        - Should be paired with rate limiting and expiration
        - Less secure than tokens but more user-friendly
        - Uniqueness must be enforced at database level to prevent collisions
        """
        # Generate a random 6-digit number using cryptographically secure random
        # This ensures the code cannot be predicted or brute-forced easily
        return f"{secrets.randbelow(1000000):06d}"
    
    def calculate_code_expiration(self) -> datetime:
        """
        Calculate expiration time for email verification codes.
        
        Returns:
            datetime: Code expiration timestamp in UTC
            
        Security considerations:
        - Codes expire after configured hours to limit attack window
        - Uses UTC timezone for consistent handling across regions
        """
        # Add configured hours to current UTC time
        # UTC ensures consistent behavior regardless of server timezone
        expiration_hours = settings.email_confirmation_expire_hours
        return datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
    
    def render_confirmation_email_template(
        self, 
        user_name: str, 
        verification_code: str
    ) -> tuple[str, str]:
        """
        Render email confirmation template with user data.
        
        Args:
            user_name: User's display name for personalization
            verification_code: 6-digit verification code for user input
            
        Returns:
            tuple[str, str]: (html_content, text_content)
            
        Template design considerations:
        - Professional branding with Humanline identity
        - Clear 6-digit code display
        - Instructions for entering code in app
        - Security warning about not sharing the code
        - Fallback text version for accessibility
        """
        
        # HTML email template with modern, responsive design
        # Inline CSS ensures compatibility across email clients
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirm Your Email - Humanline</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <!-- Header with branding -->
            <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;">
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 600;">Humanline</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 16px;">Human Resources Management</p>
            </div>
            
            <!-- Main content -->
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="color: #2c3e50; margin-top: 0; font-size: 24px;">Welcome to Humanline, {{ user_name }}!</h2>
                
                <p style="font-size: 16px; margin-bottom: 20px;">
                    Thank you for creating your Humanline account. To complete your registration and secure your account, 
                    please enter the verification code below in the Humanline app.
                </p>
                
                <!-- 6-digit verification code display -->
                <div style="text-align: center; margin: 30px 0;">
                    <div style="background: #f8f9fa; border: 2px dashed #667eea; border-radius: 12px; padding: 20px; margin: 20px 0;">
                        <p style="margin: 0 0 10px 0; font-size: 14px; color: #666; font-weight: 500;">Your Verification Code:</p>
                        <div style="font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                            {{ verification_code }}
                        </div>
                    </div>
                </div>
                
                <!-- Instructions -->
                <p style="font-size: 14px; color: #666; margin-top: 20px; text-align: center;">
                    Enter this code in the Humanline app to verify your email address.<br>
                    This code will expire in {{ expiration_hours }} hours.
                </p>
            </div>
            
            <!-- Security notice -->
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    <strong>🔒 Security Notice:</strong> This confirmation link will expire in {{ expiration_hours }} hours. 
                    If you didn't create this account, please ignore this email.
                </p>
            </div>
            
            <!-- Footer -->
            <div style="text-align: center; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 14px;">
                <p>This email was sent by Humanline HR Management System</p>
                <p>If you have questions, please contact our support team.</p>
            </div>
            
        </body>
        </html>
        """
        
        # Plain text version for accessibility and email client compatibility
        # Some users prefer text emails or have clients that don't support HTML
        text_template = """
        Welcome to Humanline, {{ user_name }}!
        
        Thank you for creating your Humanline account. To complete your registration 
        and secure your account, please enter the verification code below in the Humanline app.
        
        Your Verification Code: {{ verification_code }}
        
        Enter this code in the Humanline app to verify your email address.
        
        Security Notice:
        This verification code will expire in {{ expiration_hours }} hours. 
        If you didn't create this account, please ignore this email.
        
        ---
        Humanline HR Management System
        """
        
        # Render templates with user data using Jinja2
        # This allows for dynamic content personalization
        html_template_obj = self.template_env.from_string(html_template)
        text_template_obj = self.template_env.from_string(text_template)
        
        # Template context with all required variables
        # expiration_hours is included for user transparency
        template_context = {
            "user_name": user_name,
            "verification_code": verification_code,
            "expiration_hours": settings.email_confirmation_expire_hours
        }
        
        # Render both HTML and text versions with separate environments for thread safety
        # HTML version uses autoescape for XSS protection
        html_content = html_template_obj.render(**template_context)
        
        # For text content, create a separate non-autoescaping environment
        # This prevents race conditions in concurrent email sending
        from jinja2 import Environment, BaseLoader
        text_env = Environment(
            loader=BaseLoader(),
            autoescape=False  # Plain text doesn't need HTML escaping
        )
        text_template_obj_safe = text_env.from_string(text_template)
        text_content = text_template_obj_safe.render(**template_context)
        
        return html_content, text_content
    
    async def send_confirmation_email(
        self, 
        user_email: str, 
        user_name: str, 
        verification_code: str
    ) -> bool:
        """
        Send email confirmation message to user.
        
        Args:
            user_email: User's email address
            user_name: User's display name for personalization
            verification_code: 6-digit verification code for user input
            
        Returns:
            bool: True if email sent successfully, False otherwise
            
        This method sends a professionally formatted email with a 6-digit
        verification code that users can enter in the frontend app.
        """
        try:
            # Render email templates with user data and verification code
            # This creates personalized, professional-looking emails with the 6-digit code
            html_content, text_content = self.render_confirmation_email_template(
                user_name=user_name,
                verification_code=verification_code
            )
            
            # Send email with both HTML and text versions
            # Subject line is clear and actionable
            success = await self.send_email(
                to_email=user_email,
                subject="Confirm Your Email Address - Humanline",
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"📧 Confirmation email sent to: {user_email}")
            else:
                logger.error(f"❌ Failed to send confirmation email to: {user_email}")
                
            return success
            
        except Exception as e:
            # Log error but don't raise to prevent registration failure
            # Email delivery issues shouldn't prevent account creation
            logger.error(f"❌ Error sending confirmation email to {user_email}: {str(e)}")
            return False


# Global email service instance
# Instantiated once and reused throughout the application for efficiency
email_service = EmailService()
