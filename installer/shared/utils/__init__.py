# Shared utilities for the KPI System Installer.

# Import and re-export utility modules for easier importing
from .logging_utils import get_logger
from .error_utils import (
    InstallerError, ErrorSeverity, ConfigurationError, 
    DatabaseError, EnvironmentError, GUIError, 
    BuildError, ValidationError, handle_exception
)

# File utilities
from .file_utils import (
    ensure_directory, safe_copy_file, safe_move_file, calculate_file_hash,
    read_text_file, write_text_file, read_json_file, write_json_file,
    read_ini_file, write_ini_file, create_temp_directory, extract_archive,
    create_archive, find_files
)

# Configuration utilities
from .config_utils import (
    validate_installation_path, validate_database_connection,
    validate_url, validate_email, validate_ip_address,
    validate_port, validate_username, validate_password,
    validate_config_file, get_with_default
)

# Version and platform utilities
from .version_utils import (
    get_python_version, check_python_version, get_os_info,
    is_windows, is_macos, is_linux, is_64bit,
    check_admin_privileges, format_version, parse_version_string,
    compare_versions, check_dependency_installed, get_dependency_version,
    check_windows_registry, get_application_version, get_installer_version,
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