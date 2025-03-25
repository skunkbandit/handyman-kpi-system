"""
Version and Platform Utilities for the KPI System Installer

This module provides utilities for version checking, comparison, and
platform detection to ensure compatibility across different environments.
"""

import os
import sys
import platform
import re
from packaging import version
import subprocess
from pathlib import Path

from .logging_utils import get_logger
from .error_utils import InstallerError, ErrorSeverity

logger = get_logger(__name__)


def get_python_version():
    """
    Get the current Python version.
    
    Returns:
        tuple: (major, minor, micro) version numbers
    """
    return sys.version_info[:3]


def check_python_version(min_version=(3, 8), max_version=None):
    """
    Check if the current Python version is within the acceptable range.
    
    Args:
        min_version (tuple): Minimum acceptable version (major, minor)
        max_version (tuple, optional): Maximum acceptable version (major, minor)
        
    Returns:
        bool: True if the Python version is acceptable, False otherwise
    """
    current = get_python_version()
    current_tuple = current[:2]  # Major, minor
    
    # Check minimum version
    if current_tuple < min_version:
        logger.warning(f"Python version {current[0]}.{current[1]}.{current[2]} is below minimum {min_version[0]}.{min_version[1]}")
        return False
        
    # Check maximum version if specified
    if max_version and current_tuple > max_version:
        logger.warning(f"Python version {current[0]}.{current[1]}.{current[2]} is above maximum {max_version[0]}.{max_version[1]}")
        return False
        
    return True


def get_os_info():
    """
    Get detailed information about the operating system.
    
    Returns:
        dict: Operating system information
    """
    os_info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'node': platform.node()
    }
    
    # Add Windows-specific information
    if os_info['system'] == 'Windows':
        os_info['edition'] = platform.win32_edition() if hasattr(platform, 'win32_edition') else 'Unknown'
        os_info['is_64bit'] = platform.machine().endswith('64')
        
    # Add Unix-specific information
    elif os_info['system'] in ('Linux', 'Darwin'):
        try:
            os_info['distribution'] = ' '.join(platform.dist()) if hasattr(platform, 'dist') else 'Unknown'
        except:
            os_info['distribution'] = 'Unknown'
            
        try:
            if os_info['system'] == 'Linux':
                # Try to get Linux distribution information
                import distro
                os_info['distribution'] = distro.name(True)
                os_info['distribution_version'] = distro.version(True)
        except ImportError:
            logger.debug("Distro package not available for Linux distribution detection")
            
    return os_info


def is_windows():
    """
    Check if the current platform is Windows.
    
    Returns:
        bool: True if Windows, False otherwise
    """
    return platform.system() == 'Windows'


def is_macos():
    """
    Check if the current platform is macOS.
    
    Returns:
        bool: True if macOS, False otherwise
    """
    return platform.system() == 'Darwin'


def is_linux():
    """
    Check if the current platform is Linux.
    
    Returns:
        bool: True if Linux, False otherwise
    """
    return platform.system() == 'Linux'


def is_64bit():
    """
    Check if the current platform is 64-bit.
    
    Returns:
        bool: True if 64-bit, False otherwise
    """
    return platform.machine().endswith('64')
