"""
Security utilities for handling sensitive data.
"""

import re
from typing import Optional


def mask_sensitive_string(value: Optional[str], visible_chars: int = 4) -> Optional[str]:
    """
    Mask a sensitive string, showing only the last few characters.
    
    Args:
        value: The string to mask
        visible_chars: Number of characters to show at the end (default: 4)
    
    Returns:
        Masked string or None if input is None/empty
    """
    if not value or not isinstance(value, str):
        return value
    
    if len(value) <= visible_chars:
        return "*" * len(value)
    
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]


def mask_tax_id(tax_id: Optional[str]) -> Optional[str]:
    """
    Mask a tax ID, showing only the last 4 characters.
    
    Args:
        tax_id: The tax ID to mask
    
    Returns:
        Masked tax ID or None if input is None/empty
    """
    return mask_sensitive_string(tax_id, visible_chars=4)


def mask_social_insurance(sin: Optional[str]) -> Optional[str]:
    """
    Mask a social insurance number, showing only the last 4 characters.
    
    Args:
        sin: The social insurance number to mask
    
    Returns:
        Masked social insurance number or None if input is None/empty
    """
    return mask_sensitive_string(sin, visible_chars=4)


def mask_address(address: Optional[str]) -> Optional[str]:
    """
    Mask a street address, showing only the last few characters.
    
    Args:
        address: The address to mask
    
    Returns:
        Masked address or None if input is None/empty
    """
    if not address or not isinstance(address, str):
        return address
    
    # For addresses, show only the last 6 characters (usually house number + partial street)
    return mask_sensitive_string(address, visible_chars=6)
