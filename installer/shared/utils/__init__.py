"""
Shared utilities for the KPI System Installer.

This package provides common utilities used across different
components of the installer.
"""

# Import and re-export utility modules for easier importing
from .logging_utils import get_logger
from .error_utils import (
    InstallerError, ErrorSeverity, ConfigurationError, 
    DatabaseError, EnvironmentError, GUIError, 
    BuildError, ValidationError, handle_exception
)

# Import the separate files and then merge them into a single module
from .file_utils import (
    ensure_directory, safe_copy_file, safe_move_file, calculate_file_hash
)

from .file_utils_part2 import (
    read_text_file, write_text_file, read_json_file, write_json_file
)

from .file_utils_part3 import (
    read_ini_file, write_ini_file, create_temp_directory,
    extract_archive, create_archive, find_files
)

from .config_utils import (
    validate_installation_path, validate_database_connection,
    validate_url, validate_email, validate_ip_address,
    validate_port, validate_username, validate_password,
    validate_config_file, get_with_default
)

from .version_utils import (
    get_python_version, check_python_version, get_os_info,
    is_windows, is_macos, is_linux, is_64bit
)

from .version_utils_part2 import (
    check_admin_privileges, format_version, parse_version_string,
    compare_versions, check_dependency_installed, get_dependency_version
)

from .version_utils_part3 import (
    check_windows_registry, get_application_version, get_installer_version
)

from .version_utils_part4 import (
    check_environment_compatibility, get_compatibility_report
)

# Define package exports
__all__ = [
    # Logging utilities
    'get_logger',
    
    # Error utilities
    'InstallerError', 'ErrorSeverity', 'ConfigurationError',
    'DatabaseError', 'EnvironmentError', 'GUIError',
    'BuildError', 'ValidationError', 'handle_exception',
    
    # File utilities
    'ensure_directory', 'safe_copy_file', 'safe_move_file',
    'calculate_file_hash', 'read_text_file', 'write_text_file',
    'read_json_file', 'write_json_file', 'read_ini_file',
    'write_ini_file', 'create_temp_directory', 'extract_archive',
    'create_archive', 'find_files',
    
    # Configuration utilities
    'validate_installation_path', 'validate_database_connection',
    'validate_url', 'validate_email', 'validate_ip_address',
    'validate_port', 'validate_username', 'validate_password',
    'validate_config_file', 'get_with_default',
    
    # Version and platform utilities
    'get_python_version', 'check_python_version', 'get_os_info',
    'is_windows', 'is_macos', 'is_linux', 'is_64bit',
    'check_admin_privileges', 'format_version', 'parse_version_string',
    'compare_versions', 'check_dependency_installed', 'get_dependency_version',
    'check_windows_registry', 'get_application_version', 'get_installer_version',
    'check_environment_compatibility', 'get_compatibility_report'
]
