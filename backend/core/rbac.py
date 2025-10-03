r"""
Role-Based Access Control (RBAC) system.

This module defines roles and their associated permissions for the application.
"""

from typing import List, Dict
from enum import Enum


class Role(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class Permission(str, Enum):
    """System permissions."""
    # Employee permissions
    EMPLOYEES_READ = "employees.read"
    EMPLOYEES_WRITE = "employees.write"
    EMPLOYEES_DELETE = "employees.delete"
    
    # User management permissions
    USERS_READ = "users.read"
    USERS_WRITE = "users.write"
    USERS_DELETE = "users.delete"
    
    # Payroll permissions
    PAYROLL_READ = "payroll.read"
    PAYROLL_WRITE = "payroll.write"
    
    # Reports permissions
    REPORTS_READ = "reports.read"
    REPORTS_WRITE = "reports.write"
    
    # Settings permissions
    SETTINGS_READ = "settings.read"
    SETTINGS_WRITE = "settings.write"


# Role-Permission mapping
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    Role.ADMIN: [
        # Full access to everything
        Permission.EMPLOYEES_READ,
        Permission.EMPLOYEES_WRITE,
        Permission.EMPLOYEES_DELETE,
        Permission.USERS_READ,
        Permission.USERS_WRITE,
        Permission.USERS_DELETE,
        Permission.PAYROLL_READ,
        Permission.PAYROLL_WRITE,
        Permission.REPORTS_READ,
        Permission.REPORTS_WRITE,
        Permission.SETTINGS_READ,
        Permission.SETTINGS_WRITE,
    ],
    Role.MANAGER: [
        # Employee management and reporting
        Permission.EMPLOYEES_READ,
        Permission.EMPLOYEES_WRITE,
        Permission.PAYROLL_READ,
        Permission.REPORTS_READ,
        Permission.REPORTS_WRITE,
        Permission.SETTINGS_READ,
    ],
    Role.USER: [
        # Read-only access to basic features
        Permission.EMPLOYEES_READ,
        Permission.REPORTS_READ,
    ],
}


def get_permissions_for_role(role: str) -> List[str]:
    """
    Get permissions for a given role.
    
    Args:
        role: User role string
        
    Returns:
        List of permission strings for the role
    """
    try:
        role_enum = Role(role.lower())
        permissions = ROLE_PERMISSIONS.get(role_enum, ROLE_PERMISSIONS[Role.USER])
        return [perm.value for perm in permissions]
    except ValueError:
        # Invalid role, return user permissions as default
        return [perm.value for perm in ROLE_PERMISSIONS[Role.USER]]


def has_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if a user role has a specific permission.
    
    Args:
        user_role: User's role
        required_permission: Permission to check
        
    Returns:
        True if user has permission, False otherwise
    """
    user_permissions = get_permissions_for_role(user_role)
    return required_permission in user_permissions


def validate_role(role: str) -> bool:
    """
    Validate if a role is valid.
    
    Args:
        role: Role string to validate
        
    Returns:
        True if role is valid, False otherwise
    """
    try:
        Role(role.lower())
        return True
    except ValueError:
        return False
