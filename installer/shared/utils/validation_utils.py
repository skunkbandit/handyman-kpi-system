"""Validation Utilities for the KPI System Installer

This module provides utilities for validating various inputs like URLs, emails, etc.
"""

import re
import ipaddress
import urllib.parse

from .logging_utils import get_logger

logger = get_logger(__name__)


def validate_url(url):
    """
    Validate a URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    try:
        if not url:
            return False
            
        # Parse the URL
        parsed = urllib.parse.urlparse(url)
        
        # Check for scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            logger.warning(f"URL is missing scheme or network location: {url}")
            return False
            
        # Check for supported schemes
        if parsed.scheme not in ('http', 'https'):
            logger.warning(f"URL has unsupported scheme: {parsed.scheme}")
            return False
            
        return True
        
    except Exception as e:
        # Log but don't raise; return False instead
        logger.error(f"Error validating URL: {e}")
        return False


def validate_email(email):
    """
    Validate an email address.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if the email is valid, False otherwise
    """
    try:
        if not email:
            return False
            
        # Basic email pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Check if the email matches the pattern
        if not re.match(pattern, email):
            logger.warning(f"Email does not match expected pattern: {email}")
            return False
            
        return True
        
    except Exception as e:
        # Log but don't raise; return False instead
        logger.error(f"Error validating email: {e}")
        return False


def validate_ip_address(ip):
    """
    Validate an IP address (IPv4 or IPv6).
    
    Args:
        ip (str): IP address to validate
        
    Returns:
        bool: True if the IP address is valid, False otherwise
    """
    try:
        if not ip:
            return False
            
        # Try to create an IP address object
        ipaddress.ip_address(ip)
        return True
        
    except ValueError:
        logger.warning(f"Invalid IP address: {ip}")
        return False
    except Exception as e:
        # Log but don't raise; return False instead
        logger.error(f"Error validating IP address: {e}")
        return False


def validate_port(port):
    """
    Validate a port number.
    
    Args:
        port (str or int): Port number to validate
        
    Returns:
        bool: True if the port is valid, False otherwise
    """
    try:
        # Convert to int if it's a string
        if isinstance(port, str):
            port = int(port)
            
        # Check if the port is in the valid range
        if port < 1 or port > 65535:
            logger.warning(f"Port number out of range (1-65535): {port}")
            return False
            
        return True
        
    except (ValueError, TypeError):
        logger.warning(f"Port is not a valid number: {port}")
        return False
    except Exception as e:
        # Log but don't raise; return False instead
        logger.error(f"Error validating port: {e}")
        return False


def validate_username(username):
    """
    Validate a username.
    
    Args:
        username (str): Username to validate
        
    Returns:
        bool: True if the username is valid, False otherwise
    """
    try:
        if not username:
            return False
            
        # Username should be at least 3 characters
        if len(username) < 3:
            logger.warning(f"Username too short (minimum 3 characters): {username}")
            return False
            
        # Username should contain only alphanumeric characters, underscore, and hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            logger.warning(f"Username contains invalid characters: {username}")
            return False
            
        return True
        
    except Exception as e:
        # Log but don't raise; return False instead
        logger.error(f"Error validating username: {e}")
        return False


def validate_password(password, min_length=8, require_upper=True, require_lower=True, 
                     require_digit=True, require_special=True):
    """
    Validate a password against security requirements.
    
    Args:
        password (str): Password to validate
        min_length (int): Minimum password length
        require_upper (bool): Whether to require uppercase letters
        require_lower (bool): Whether to require lowercase letters
        require_digit (bool): Whether to require digits
        require_special (bool): Whether to require special characters
        
    Returns:
        tuple: (is_valid, reasons) where reasons is a list of validation failures
    """
    try:
        reasons = []
        
        if not password:
            reasons.append("Password is empty")
            return False, reasons
            
        # Check minimum length
        if len(password) < min_length:
            reasons.append(f"Password is too short (minimum {min_length} characters)")
            
        # Check for uppercase letters
        if require_upper and not any(c.isupper() for c in password):
            reasons.append("Password must contain at least one uppercase letter")
            
        # Check for lowercase letters
        if require_lower and not any(c.islower() for c in password):
            reasons.append("Password must contain at least one lowercase letter")
            
        # Check for digits
        if require_digit and not any(c.isdigit() for c in password):
            reasons.append("Password must contain at least one digit")
            
        # Check for special characters
        if require_special and not any(not c.isalnum() for c in password):
            reasons.append("Password must contain at least one special character")
            
        # Return validation result
        is_valid = len(reasons) == 0
        return is_valid, reasons
        
    except Exception as e:
        # Log but don't raise; return False instead
        logger.error(f"Error validating password: {e}")
        return False, ["Internal validation error"]