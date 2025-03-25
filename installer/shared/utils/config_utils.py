"""Configuration Utilities for the KPI System Installer

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