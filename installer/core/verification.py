"""
Installation verification for the Handyman KPI System Installer.

This module provides classes and functions for verifying the installation,
including file checks, port availability, database connection, and dependencies.
"""

import os
import sys
import socket
from typing import Dict, List, Optional, Tuple, Any

from .environment import Environment
from .config import InstallerConfig
from .database import DatabaseInitializer


class InstallationVerifier:
    """Platform-agnostic installation verification."""
    
    def __init__(self, config: Optional[InstallerConfig] = None):
        """Initialize installation verifier.
        
        Args:
            config: Configuration object, or None to create a new one
        """
        self.config = config or InstallerConfig()
        self.environment = Environment()
        self.database = DatabaseInitializer(self.config)
    
    def verify_files(self, required_files: List[str] = None) -> Tuple[bool, List[str]]:
        """Verify that required files exist.
        
        Args:
            required_files: List of required file paths (relative to app directory),
                            or None to get from configuration
            
        Returns:
            Tuple containing:
                - Boolean indicating if all files exist
                - List of missing files
        """
        if required_files is None:
            required_files = []
            
            # Get required files from configuration
            if self.config.has_section('required_files'):
                for option, value in self.config.config.items('required_files'):
                    required_files.append(value)
        
        app_dir = self.environment.get_app_directory()
        missing = []
        
        for file_path in required_files:
            full_path = os.path.join(app_dir, file_path)
            if not os.path.exists(full_path):
                missing.append(file_path)
        
        return len(missing) == 0, missing
    
    def verify_directories(self, required_dirs: List[str] = None) -> Tuple[bool, List[str]]:
        """Verify that required directories exist.
        
        Args:
            required_dirs: List of required directory paths (relative to app directory),
                           or None to get from configuration
            
        Returns:
            Tuple containing:
                - Boolean indicating if all directories exist
                - List of missing directories
        """
        if required_dirs is None:
            required_dirs = []
            
            # Get required directories from configuration
            if self.config.has_section('required_directories'):
                for option, value in self.config.config.items('required_directories'):
                    required_dirs.append(value)
        
        app_dir = self.environment.get_app_directory()
        missing = []
        
        for dir_path in required_dirs:
            full_path = os.path.join(app_dir, dir_path)
            if not os.path.isdir(full_path):
                missing.append(dir_path)
        
        return len(missing) == 0, missing
    
    def verify_port_available(self, port: Optional[int] = None) -> bool:
        """Verify that the specified port is available.
        
        Args:
            port: Port number to check, or None to get from configuration
            
        Returns:
            bool: True if port is available, False otherwise
        """
        if port is None:
            port = self.config.get_int('server', 'port', fallback=5000)
        
        return self.environment.get_port_availability(port)
    
    def verify_database_connection(self) -> Tuple[bool, str]:
        """Verify database connection.
        
        Returns:
            Tuple containing:
                - Boolean indicating if database connection works
                - Error message if connection fails, empty string otherwise
        """
        return self.database.test_database_connection()
    
    def verify_dependencies(self) -> Tuple[bool, List[str]]:
        """Verify that required Python packages are installed.
        
        Returns:
            Tuple containing:
                - Boolean indicating if all dependencies are met
                - List of missing packages
        """
        dependencies = []
        
        # Get Python dependencies from configuration
        if self.config.has_section('dependencies'):
            for option, value in self.config.config.items('dependencies'):
                dependencies.append(value)
        
        return self.environment.check_dependencies(dependencies)
    
    def verify_permissions(self) -> Tuple[bool, List[str]]:
        """Verify that the application has necessary permissions.
        
        Returns:
            Tuple containing:
                - Boolean indicating if all permissions are available
                - List of permission issues
        """
        issues = []
        app_dir = self.environment.get_app_directory()
        
        # Check if we can write to the application directory
        if not os.access(app_dir, os.W_OK):
            issues.append(f"Cannot write to application directory: {app_dir}")
        
        # Check if we can write to the data directory
        data_dir = self.environment.get_data_directory()
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
            except OSError:
                issues.append(f"Cannot create data directory: {data_dir}")
        elif not os.access(data_dir, os.W_OK):
            issues.append(f"Cannot write to data directory: {data_dir}")
        
        # Check if we can write to the config directory
        config_dir = self.environment.get_config_directory()
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir, exist_ok=True)
            except OSError:
                issues.append(f"Cannot create config directory: {config_dir}")
        elif not os.access(config_dir, os.W_OK):
            issues.append(f"Cannot write to config directory: {config_dir}")
        
        # Check if we can write to the log directory
        log_dir = self.environment.get_log_directory()
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError:
                issues.append(f"Cannot create log directory: {log_dir}")
        elif not os.access(log_dir, os.W_OK):
            issues.append(f"Cannot write to log directory: {log_dir}")
        
        return len(issues) == 0, issues
    
    def run_full_verification(self) -> Dict[str, Any]:
        """Run full verification of the installation.
        
        Returns:
            Dict containing verification results for each aspect
        """
        # Verify files
        files_ok, missing_files = self.verify_files()
        
        # Verify directories
        dirs_ok, missing_dirs = self.verify_directories()
        
        # Verify port
        port = self.config.get_int('server', 'port', fallback=5000)
        port_ok = self.verify_port_available(port)
        
        # Verify database
        db_ok, db_error = self.verify_database_connection()
        
        # Verify dependencies
        deps_ok, missing_deps = self.verify_dependencies()
        
        # Verify permissions
        perms_ok, perm_issues = self.verify_permissions()
        
        return {
            'files': {
                'status': files_ok,
                'missing': missing_files
            },
            'directories': {
                'status': dirs_ok,
                'missing': missing_dirs
            },
            'port': {
                'status': port_ok,
                'port': port
            },
            'database': {
                'status': db_ok,
                'error': db_error
            },
            'dependencies': {
                'status': deps_ok,
                'missing': missing_deps
            },
            'permissions': {
                'status': perms_ok,
                'issues': perm_issues
            },
            'overall': files_ok and dirs_ok and port_ok and db_ok and deps_ok and perms_ok
        }
    
    def get_verification_summary(self) -> str:
        """Get a summary of the verification results.
        
        Returns:
            str: Summary of verification results
        """
        results = self.run_full_verification()
        
        summary = []
        summary.append("Installation Verification Summary")
        summary.append("===============================")
        summary.append("")
        
        # Files
        summary.append(f"Files: {'OK' if results['files']['status'] else 'FAILED'}")
        if not results['files']['status']:
            summary.append("  Missing files:")
            for file in results['files']['missing']:
                summary.append(f"  - {file}")
            summary.append("")
        
        # Directories
        summary.append(f"Directories: {'OK' if results['directories']['status'] else 'FAILED'}")
        if not results['directories']['status']:
            summary.append("  Missing directories:")
            for directory in results['directories']['missing']:
                summary.append(f"  - {directory}")
            summary.append("")
        
        # Port
        summary.append(f"Port {results['port']['port']}: {'AVAILABLE' if results['port']['status'] else 'IN USE'}")
        if not results['port']['status']:
            summary.append("  The port is already in use by another application.")
            summary.append(f"  Please change the port in the configuration file or stop the other application.")
            summary.append("")
        
        # Database
        summary.append(f"Database: {'OK' if results['database']['status'] else 'FAILED'}")
        if not results['database']['status']:
            summary.append(f"  Error: {results['database']['error']}")
            summary.append("")
        
        # Dependencies
        summary.append(f"Dependencies: {'OK' if results['dependencies']['status'] else 'FAILED'}")
        if not results['dependencies']['status']:
            summary.append("  Missing dependencies:")
            for dep in results['dependencies']['missing']:
                summary.append(f"  - {dep}")
            summary.append("")
        
        # Permissions
        summary.append(f"Permissions: {'OK' if results['permissions']['status'] else 'FAILED'}")
        if not results['permissions']['status']:
            summary.append("  Permission issues:")
            for issue in results['permissions']['issues']:
                summary.append(f"  - {issue}")
            summary.append("")
        
        # Overall
        summary.append("")
        summary.append(f"Overall: {'OK' if results['overall'] else 'FAILED'}")
        
        return "\n".join(summary)
