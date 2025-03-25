"""
Configuration management for the Handyman KPI System Installer.

This module provides classes and functions for managing configuration across
different installation methods, including reading and writing configuration files,
validating configuration, and generating configuration templates.
"""

import os
import sys
import configparser
import secrets
from typing import Any, Dict, Optional


class InstallerConfig:
    """Platform-agnostic configuration management for the installer."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file, or None to use default location
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration path based on platform."""
        # Get the base path of the package
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Platform-agnostic default location (will be overridden by platform-specific classes)
        return os.path.join(base_dir, 'shared', 'config_templates', 'default_config.ini')
    
    def _load_config(self) -> configparser.ConfigParser:
        """Load configuration from file."""
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_path):
            try:
                config.read(self.config_path)
            except (configparser.Error, IOError) as e:
                print(f"Error loading configuration: {e}", file=sys.stderr)
                # Create a new configuration with defaults
                config = self._create_default_config()
        else:
            # Create a new configuration with defaults
            config = self._create_default_config()
        
        return config
    
    def _create_default_config(self) -> configparser.ConfigParser:
        """Create a default configuration."""
        config = configparser.ConfigParser()
        
        # Database section
        config.add_section('database')
        config.set('database', 'type', 'sqlite')
        config.set('database', 'path', 'data/database.db')
        
        # Server section
        config.add_section('server')
        config.set('server', 'host', '127.0.0.1')
        config.set('server', 'port', '5000')
        config.set('server', 'debug', 'false')
        
        # App section
        config.add_section('app')
        config.set('app', 'secret_key', self._generate_secret_key())
        config.set('app', 'log_level', 'INFO')
        
        # Dependencies section
        config.add_section('dependencies')
        config.set('dependencies', 'flask', 'flask')
        config.set('dependencies', 'sqlalchemy', 'sqlalchemy')
        config.set('dependencies', 'jinja2', 'jinja2')
        config.set('dependencies', 'waitress', 'waitress')
        
        return config
    
    def _generate_secret_key(self, length: int = 32) -> str:
        """Generate a secure random secret key.
        
        Args:
            length: Length of the secret key in bytes
            
        Returns:
            str: Hex-encoded secure random secret key
        """
        return secrets.token_hex(length)
    
    def save(self) -> bool:
        """Save configuration to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Write configuration
            with open(self.config_path, 'w') as f:
                self.config.write(f)
            
            return True
        except (IOError, OSError) as e:
            print(f"Error saving configuration: {e}", file=sys.stderr)
            return False
    
    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            section: Configuration section
            option: Configuration option
            fallback: Fallback value if not found
            
        Returns:
            Any: Configuration value or fallback
        """
        return self.config.get(section, option, fallback=fallback)
    
    def get_int(self, section: str, option: str, fallback: Optional[int] = None) -> Optional[int]:
        """Get an integer configuration value.
        
        Args:
            section: Configuration section
            option: Configuration option
            fallback: Fallback value if not found
            
        Returns:
            Optional[int]: Integer configuration value or fallback
        """
        try:
            return self.config.getint(section, option, fallback=fallback)
        except (configparser.Error, ValueError):
            return fallback
    
    def get_boolean(self, section: str, option: str, fallback: Optional[bool] = None) -> Optional[bool]:
        """Get a boolean configuration value.
        
        Args:
            section: Configuration section
            option: Configuration option
            fallback: Fallback value if not found
            
        Returns:
            Optional[bool]: Boolean configuration value or fallback
        """
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except (configparser.Error, ValueError):
            return fallback
    
    def set(self, section: str, option: str, value: str) -> None:
        """Set a configuration value.
        
        Args:
            section: Configuration section
            option: Configuration option
            value: Configuration value
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, option, value)
    
    def has_section(self, section: str) -> bool:
        """Check if a section exists.
        
        Args:
            section: Configuration section
            
        Returns:
            bool: True if the section exists, False otherwise
        """
        return self.config.has_section(section)
    
    def has_option(self, section: str, option: str) -> bool:
        """Check if an option exists.
        
        Args:
            section: Configuration section
            option: Configuration option
            
        Returns:
            bool: True if the option exists, False otherwise
        """
        return self.config.has_option(section, option)
    
    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration as a dictionary.
        
        Returns:
            Dict[str, str]: Database configuration
        """
        if not self.config.has_section('database'):
            return {}
        
        return dict(self.config['database'])
    
    def set_database_config(self, db_config: Dict[str, str]) -> None:
        """Set database configuration from a dictionary.
        
        Args:
            db_config: Database configuration
        """
        if not self.config.has_section('database'):
            self.config.add_section('database')
        
        for key, value in db_config.items():
            self.config.set('database', key, value)
    
    def get_server_config(self) -> Dict[str, str]:
        """Get server configuration as a dictionary.
        
        Returns:
            Dict[str, str]: Server configuration
        """
        if not self.config.has_section('server'):
            return {}
        
        return dict(self.config['server'])
    
    def set_server_config(self, server_config: Dict[str, str]) -> None:
        """Set server configuration from a dictionary.
        
        Args:
            server_config: Server configuration
        """
        if not self.config.has_section('server'):
            self.config.add_section('server')
        
        for key, value in server_config.items():
            self.config.set('server', key, value)
    
    def get_app_config(self) -> Dict[str, str]:
        """Get application configuration as a dictionary.
        
        Returns:
            Dict[str, str]: Application configuration
        """
        if not self.config.has_section('app'):
            return {}
        
        return dict(self.config['app'])
    
    def set_app_config(self, app_config: Dict[str, str]) -> None:
        """Set application configuration from a dictionary.
        
        Args:
            app_config: Application configuration
        """
        if not self.config.has_section('app'):
            self.config.add_section('app')
        
        for key, value in app_config.items():
            self.config.set('app', key, value)
