"""
Version and Platform Utilities for the KPI System Installer (Part 3)

Windows-specific and application version utilities.
"""

from pathlib import Path

from .logging_utils import get_logger
from .error_utils import InstallerError, ErrorSeverity

logger = get_logger(__name__)


def check_windows_registry(key, value_name=None):
    """
    Check a Windows registry key/value.
    
    Args:
        key (str): Registry key path
        value_name (str, optional): Name of the value to retrieve
        
    Returns:
        object or None: Value if found, None otherwise
    """
    try:
        from .version_utils import is_windows
        
        if not is_windows():
            logger.warning("Windows registry check attempted on non-Windows system")
            return None
            
        try:
            import winreg
            
            # Split the key path into the root key and subkey
            root_key_str, subkey = key.split('\\', 1)
            
            # Map the root key string to the actual key
            root_key_map = {
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
            }
            
            root_key = root_key_map.get(root_key_str)
            if root_key is None:
                logger.warning(f"Invalid registry root key: {root_key_str}")
                return None
                
            # Open the registry key
            with winreg.OpenKey(root_key, subkey) as reg_key:
                # If value_name is None, just check if the key exists
                if value_name is None:
                    return True
                    
                # Otherwise, get the specified value
                value, value_type = winreg.QueryValueEx(reg_key, value_name)
                return value
        except (ImportError, WindowsError) as e:
            logger.warning(f"Error accessing Windows registry: {e}")
            return None
    except Exception as e:
        logger.warning(f"Error in check_windows_registry: {e}")
        return None


def get_application_version():
    """
    Get the version of the KPI System application.
    
    Returns:
        str: Application version
    """
    # Check for version in package metadata
    try:
        from importlib.metadata import version as get_pkg_version
        try:
            return get_pkg_version('handyman-kpi-system')
        except:
            pass
    except ImportError:
        pass
        
    # Check for version file
    try:
        version_file = Path(__file__).parent.parent.parent / 'VERSION'
        if version_file.exists():
            with open(version_file, 'r') as f:
                return f.read().strip()
    except:
        pass
        
    # Default version
    return "0.1.0"


def get_installer_version():
    """
    Get the version of the installer.
    
    Returns:
        str: Installer version
    """
    # Check for version in package metadata
    try:
        from importlib.metadata import version as get_pkg_version
        try:
            return get_pkg_version('handyman-kpi-installer')
        except:
            pass
    except ImportError:
        pass
        
    # Check for version file
    try:
        version_file = Path(__file__).parent.parent / 'VERSION'
        if version_file.exists():
            with open(version_file, 'r') as f:
                return f.read().strip()
    except:
        pass
        
    # Default version
    return "0.1.0"
