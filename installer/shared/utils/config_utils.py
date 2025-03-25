"""
Configuration Utilities for the KPI System Installer

This module provides utilities for validating and managing configuration settings
across different components of the installer system.
"""

import os
from pathlib import Path
import re
import ipaddress
import urllib.parse

from .logging_utils import get_logger
from .error_utils import InstallerError, ValidationError, ErrorSeverity

logger = get_logger(__name__)


def validate_installation_path(path_str):
    """
    Validate a proposed installation path.
    
    Args:
        path_str (str): Path to validate
        
    Returns:
        bool: True if the path is valid, False otherwise
        
    Raises:
        ValidationError: If the path has severe problems
    """
    try:
        if not path_str:
            return False
            
        path = Path(path_str)
        
        # Check if path is absolute
        if not path.is_absolute():
            logger.warning(f"Path is not absolute: {path}")
            return False
            
        # Check for invalid characters or syntax
        try:
            # Just checking if it's properly formatted
            path.resolve()
        except (ValueError, OSError) as e:
            logger.warning(f"Path has invalid syntax: {path}")
            return False
            
        # Check for required installation conditions
        parent = path.parent
        
        # Parent directory should exist
        if not parent.exists():
            logger.warning(f"Parent directory does not exist: {parent}")
            return False
            
        # Parent directory should be writable
        if not os.access(parent, os.W_OK):
            logger.warning(f"Parent directory is not writable: {parent}")
            return False
            
        # Path should not be a file
        if path.exists() and path.is_file():
            logger.warning(f"Path exists and is a file: {path}")
            return False
            
        # If path is a directory, it should be writable
        if path.exists() and path.is_dir() and not os.access(path, os.W_OK):
            logger.warning(f"Directory exists but is not writable: {path}")
            return False
            
        # Additional checks for Windows
        if os.name == 'nt':
            # Check for reserved names
            if path.drive.upper() in ('CON:', 'PRN:', 'AUX:', 'NUL:', 'COM1:', 'COM2:', 'COM3:', 'COM4:', 
                                    'LPT1:', 'LPT2:', 'LPT3:'):
                logger.warning(f"Path contains a reserved Windows device name: {path}")
                return False
                
            # Check for reserved characters
            reserved_chars = '<>:"|?*\\'
            if any(c in path_str for c in reserved_chars):
                logger.warning(f"Path contains reserved Windows characters: {path}")
                return False
        
        return True
        
    except Exception as e:
        # Log but don't raise; return False instead
        logger.error(f"Error validating installation path: {e}")
        return False


def validate_database_connection(db_type, connection_params):
    """
    Validate database connection parameters.
    
    Args:
        db_type (str): Database type ('sqlite', 'mysql', 'postgresql')
        connection_params (dict): Connection parameters for the database
        
    Returns:
        bool: True if the connection parameters are valid, False otherwise
    """
    try:
        if db_type.lower() == 'sqlite':
            # SQLite requires a valid file path
            path_str = connection_params.get('database')
            if not path_str:
                logger.warning("SQLite database path is missing")
                return False
                
            path = Path(path_str)
            
            # If the file exists, it should be a file and readable
            if path.exists() and (not path.is_file() or not os.access(path, os.R_OK)):
                logger.warning(f"SQLite database exists but is not a readable file: {path}")
                return False
                
            # If the file doesn't exist, its parent directory should exist and be writable
            if not path.exists():
                parent = path.parent
                if not parent.exists() or not os.access(parent, os.W_OK):
                    logger.warning(f"Parent directory for SQLite database does not exist or is not writable: {parent}")
                    return False
                    
            return True
            
        elif db_type.lower() in ('mysql', 'postgresql'):
            # Required parameters
            required_params = ['host', 'port', 'user', 'database']
            
            # Check if all required parameters are present
            for param in required_params:
                if param not in connection_params:
                    logger.warning(f"Required parameter '{param}' missing for {db_type} connection")
                    return False
                    
            # Validate port
            port = connection_params.get('port')
            try:
                port_num = int(port)
                if port_num < 1 or port_num > 65535:
                    logger.warning(f"Invalid port number: {port}")
                    return False
            except (ValueError, TypeError):
                logger.warning(f"Port is not a valid number: {port}")
                return False
                
            # Validate host (basic check)
            host = connection_params.get('host')
            if not host:
                logger.warning("Host is empty")
                return False
                
            # Validate database name (basic check)
            database = connection_params.get('database')
            if not database:
                logger.warning("Database name is empty")
                return False
                
            # Validate username (basic check)
            user = connection_params.get('user')
            if not user:
                logger.warning("Username is empty")
                return False
                
            return True
            
        else:
            # Unsupported database type
            logger.warning(f"Unsupported database type: {db_type}")
            return False
            
    except Exception as e:
        # Log but don't raise; return False instead
        logger.error(f"Error validating database connection: {e}")
        return False


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


def validate_config_file(config_dict, required_sections, required_keys=None):
    """
    Validate a configuration dictionary against required sections and keys.
    
    Args:
        config_dict (dict): Configuration dictionary to validate
        required_sections (list): List of section names that must be present
        required_keys (dict, optional): Dictionary mapping section names to lists of required keys
        
    Returns:
        tuple: (is_valid, errors) where errors is a list of validation errors
    """
    errors = []
    
    try:
        # Check required sections
        for section in required_sections:
            if section not in config_dict:
                errors.append(f"Missing required section: {section}")
                
        # Check required keys in each section
        if required_keys:
            for section, keys in required_keys.items():
                if section in config_dict:
                    for key in keys:
                        if key not in config_dict[section]:
                            errors.append(f"Missing required key '{key}' in section '{section}'")
        
        # Return validation result
        is_valid = len(errors) == 0
        return is_valid, errors
        
    except Exception as e:
        # Log but don't raise; return False with errors
        logger.error(f"Error validating configuration: {e}")
        errors.append("Internal validation error")
        return False, errors


def get_with_default(config_dict, section, key, default=None):
    """
    Get a configuration value with a default if not found.
    
    Args:
        config_dict (dict): Configuration dictionary
        section (str): Section name
        key (str): Key name
        default: Default value to return if not found
        
    Returns:
        The configuration value or the default
    """
    try:
        return config_dict.get(section, {}).get(key, default)
    except Exception:
        return default
