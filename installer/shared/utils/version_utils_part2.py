"""
Version and Platform Utilities for the KPI System Installer (Part 2)

Additional version and platform utilities.
"""

import os
import sys
import platform
import re
import subprocess
from pathlib import Path

from .logging_utils import get_logger
from .error_utils import InstallerError, ErrorSeverity

logger = get_logger(__name__)


def check_admin_privileges():
    """
    Check if the current process has administrator/root privileges.
    
    Returns:
        bool: True if the process has admin privileges, False otherwise
    """
    try:
        from .version_utils import is_windows
        
        if is_windows():
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # Unix-like systems
            return os.geteuid() == 0
    except (AttributeError, ImportError):
        # If geteuid is not available or import fails, try a different approach
        try:
            return os.access('/root', os.W_OK)
        except:
            logger.warning("Could not determine admin privileges")
            return False


def format_version(version_tuple):
    """
    Format a version tuple as a string.
    
    Args:
        version_tuple (tuple): Version numbers (major, minor, micro)
        
    Returns:
        str: Formatted version string
    """
    if len(version_tuple) >= 3:
        return f"{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}"
    elif len(version_tuple) == 2:
        return f"{version_tuple[0]}.{version_tuple[1]}"
    elif len(version_tuple) == 1:
        return str(version_tuple[0])
    else:
        return "Unknown"


def parse_version_string(version_str):
    """
    Parse a version string into a comparable version object.
    
    Args:
        version_str (str): Version string to parse
        
    Returns:
        version.Version: Parsed version object
        
    Raises:
        InstallerError: If the version string is invalid
    """
    try:
        from packaging import version
        return version.parse(version_str)
    except:
        raise InstallerError(
            f"Invalid version format: {version_str}",
            details="The version string could not be parsed",
            recovery_hint="Make sure the version follows the format: X.Y.Z"
        )


def compare_versions(version1, version2):
    """
    Compare two version strings.
    
    Args:
        version1 (str): First version string
        version2 (str): Second version string
        
    Returns:
        int: -1 if version1 < version2, 0 if version1 == version2, 1 if version1 > version2
        
    Raises:
        InstallerError: If either version string is invalid
    """
    try:
        v1 = parse_version_string(version1)
        v2 = parse_version_string(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to compare versions: {version1} and {version2}",
            details=str(e)
        ) from e


def check_dependency_installed(executable_name):
    """
    Check if a dependency is installed by looking for its executable.
    
    Args:
        executable_name (str): Name of the executable to check
        
    Returns:
        bool: True if the executable is found, False otherwise
    """
    try:
        from .version_utils import is_windows
        
        # Use subprocess to check if the executable exists
        if is_windows():
            # On Windows, use where command
            result = subprocess.run(['where', executable_name], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   check=False)
        else:
            # On Unix-like systems, use which command
            result = subprocess.run(['which', executable_name], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   check=False)
        
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"Error checking for {executable_name}: {e}")
        return False


def get_dependency_version(executable_name, version_arg='--version', regex=r'(\d+\.\d+(\.\d+)?)'):
    """
    Get the version of an installed dependency.
    
    Args:
        executable_name (str): Name of the executable
        version_arg (str): Command-line argument to get version info
        regex (str): Regular expression to extract version number
        
    Returns:
        str or None: Version string if found, None otherwise
    """
    try:
        # Run the command to get version info
        result = subprocess.run([executable_name, version_arg], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True,
                               check=False)
        
        # Check if the command succeeded
        if result.returncode != 0:
            logger.warning(f"Failed to get version for {executable_name}")
            return None
            
        # Extract version using regex
        output = result.stdout if result.stdout else result.stderr
        match = re.search(regex, output)
        
        if match:
            return match.group(1)
        else:
            logger.warning(f"Version pattern not found for {executable_name}")
            return None
    except Exception as e:
        logger.warning(f"Error getting version for {executable_name}: {e}")
        return None
