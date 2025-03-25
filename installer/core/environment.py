"""
Environment management for the Handyman KPI System Installer.

This module provides classes and functions for managing the application environment,
including Python environment, dependencies, and system configuration.
"""

import os
import sys
import platform
import subprocess
import importlib
from typing import Dict, List, Optional, Tuple, Any


class Environment:
    """Platform-agnostic environment setup and validation."""
    
    @staticmethod
    def get_platform() -> str:
        """Get the current platform identifier.
        
        Returns:
            str: Platform identifier ('windows', 'linux', 'macos', or 'unknown')
        """
        system = platform.system().lower()
        if system == 'windows':
            return 'windows'
        elif system == 'linux':
            return 'linux'
        elif system == 'darwin':
            return 'macos'
        else:
            return 'unknown'
    
    @staticmethod
    def is_virtual_env() -> bool:
        """Check if running in a virtual environment.
        
        Returns:
            bool: True if running in a virtual environment, False otherwise
        """
        return hasattr(sys, 'real_prefix') or \
               (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    @staticmethod
    def get_python_info() -> Dict[str, str]:
        """Get information about the Python environment.
        
        Returns:
            Dict[str, str]: Python environment information
        """
        return {
            'version': platform.python_version(),
            'implementation': platform.python_implementation(),
            'executable': sys.executable,
            'is_virtual_env': str(Environment.is_virtual_env()),
            'path': str(sys.path)
        }
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Get information about the system.
        
        Returns:
            Dict[str, str]: System information
        """
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'node': platform.node()
        }
    
    @staticmethod
    def check_dependencies(required_packages: List[str]) -> Tuple[bool, List[str]]:
        """Check if required Python packages are installed.
        
        Args:
            required_packages: List of required package names
            
        Returns:
            Tuple containing:
                - Boolean indicating if all dependencies are met
                - List of missing packages
        """
        missing = []
        
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                missing.append(package)
        
        return len(missing) == 0, missing
    
    @staticmethod
    def install_dependencies(packages: List[str]) -> bool:
        """Install Python dependencies.
        
        Args:
            packages: List of package names to install
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not packages:
            return True
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def get_app_directory() -> str:
        """Get the application directory.
        
        Returns:
            str: Application directory
            
        Note:
            This method should be overridden by platform-specific implementations.
        """
        # Base implementation - will be overridden by platform-specific classes
        # This returns the parent directory of the 'installer' package
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    @staticmethod
    def get_data_directory() -> str:
        """Get the data directory.
        
        Returns:
            str: Data directory
            
        Note:
            This method should be overridden by platform-specific implementations.
        """
        # Base implementation - will be overridden by platform-specific classes
        app_dir = Environment.get_app_directory()
        return os.path.join(app_dir, 'data')
    
    @staticmethod
    def get_config_directory() -> str:
        """Get the configuration directory.
        
        Returns:
            str: Configuration directory
            
        Note:
            This method should be overridden by platform-specific implementations.
        """
        # Base implementation - will be overridden by platform-specific classes
        app_dir = Environment.get_app_directory()
        return os.path.join(app_dir, 'config')
    
    @staticmethod
    def get_log_directory() -> str:
        """Get the log directory.
        
        Returns:
            str: Log directory
            
        Note:
            This method should be overridden by platform-specific implementations.
        """
        # Base implementation - will be overridden by platform-specific classes
        app_dir = Environment.get_app_directory()
        return os.path.join(app_dir, 'logs')
    
    @staticmethod
    def setup_environment() -> bool:
        """Set up the environment for the application.
        
        Returns:
            bool: True if successful, False otherwise
            
        Note:
            This method should be overridden by platform-specific implementations.
        """
        # Base implementation - will be overridden by platform-specific classes
        try:
            # Create necessary directories
            for directory in [
                Environment.get_data_directory(),
                Environment.get_config_directory(),
                Environment.get_log_directory()
            ]:
                os.makedirs(directory, exist_ok=True)
            
            return True
        except OSError:
            return False
    
    @staticmethod
    def is_admin() -> bool:
        """Check if the current user has administrator privileges.
        
        Returns:
            bool: True if the user has administrator privileges, False otherwise
            
        Note:
            This method should be overridden by platform-specific implementations.
        """
        # Base implementation - will be overridden by platform-specific classes
        # This implementation always returns False to be conservative
        return False
    
    @staticmethod
    def get_environment_variables() -> Dict[str, str]:
        """Get relevant environment variables.
        
        Returns:
            Dict[str, str]: Environment variables
        """
        # Return a subset of environment variables that are relevant
        relevant_vars = [
            'PATH', 'PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE',
            'TEMP', 'TMP', 'HOME', 'USERPROFILE', 'USERNAME'
        ]
        
        return {var: os.environ.get(var, '') for var in relevant_vars if var in os.environ}
    
    @staticmethod
    def get_port_availability(port: int) -> bool:
        """Check if a port is available.
        
        Args:
            port: Port number to check
            
        Returns:
            bool: True if port is available, False otherwise
        """
        import socket
        
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                s.listen(1)
                return True
        except OSError:
            return False
    
    @classmethod
    def get_free_port(cls, start_port: int = 5000, max_attempts: int = 100) -> Optional[int]:
        """Find a free port.
        
        Args:
            start_port: Port to start checking from
            max_attempts: Maximum number of ports to check
            
        Returns:
            Optional[int]: First available port, or None if no ports are available
        """
        for port in range(start_port, start_port + max_attempts):
            if cls.get_port_availability(port):
                return port
        
        return None