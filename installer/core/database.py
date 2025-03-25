"""
Database initialization and management for the Handyman KPI System Installer.

This module provides classes and functions for initializing and managing databases,
including support for SQLite, MySQL, and PostgreSQL.
"""

import os
import sys
import importlib
from typing import Dict, Any, Optional, Tuple, List

from .config import InstallerConfig


class DatabaseInitializer:
    """Platform-agnostic database initialization."""
    
    def __init__(self, config: Optional[InstallerConfig] = None):
        """Initialize database initializer.
        
        Args:
            config: Configuration object, or None to create a new one
        """
        self.config = config or InstallerConfig()
    
    def get_schema_path(self, db_type: str) -> str:
        """Get the path to the database schema file based on database type.
        
        Args:
            db_type: Database type ('sqlite', 'mysql', or 'postgresql')
            
        Returns:
            str: Path to the schema file
            
        Raises:
            ValueError: If the database type is unsupported
        """
        # Get the base path of the package
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        schema_files = {
            'sqlite': 'schema_sqlite.sql',
            'mysql': 'schema_mysql.sql',
            'postgresql': 'schema_postgresql.sql'
        }
        
        if db_type not in schema_files:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        return os.path.join(base_dir, 'shared', 'database', schema_files[db_type])
    
    def import_database_adapter(self, db_type: str):
        """Import the appropriate database adapter dynamically.
        
        Args:
            db_type: Database type ('sqlite', 'mysql', or 'postgresql')
            
        Returns:
            module: Imported database adapter module
            
        Raises:
            ImportError: If the database adapter cannot be imported
            ValueError: If the database type is unsupported
        """
        if db_type not in ['sqlite', 'mysql', 'postgresql']:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        try:
            return importlib.import_module(f'.adapters.{db_type}', 
                                           package='installer.shared.database')
        except ImportError as e:
            print(f"Error importing database adapter: {e}", file=sys.stderr)
            raise ImportError(f"Database adapter for {db_type} not found") from e
    
    def initialize_database(self, db_config: Optional[Dict[str, str]] = None) -> bool:
        """Initialize the database with schema and initial data.
        
        Args:
            db_config: Database configuration, or None to use config from file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if db_config is None:
            db_config = self.config.get_database_config()
        
        db_type = db_config.get('type', 'sqlite')
        
        try:
            # Import the appropriate database module dynamically
            db_module = self.import_database_adapter(db_type)
            
            # Get the schema
            schema_path = self.get_schema_path(db_type)
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            # Initialize the database
            adapter = db_module.DatabaseAdapter(db_config)
            success = adapter.initialize(schema_sql)
            
            # Save configuration if successful
            if success and db_config is not None:
                self.config.set_database_config(db_config)
                self.config.save()
            
            return success
        
        except (ImportError, ValueError, IOError, Exception) as e:
            print(f"Error initializing database: {e}", file=sys.stderr)
            return False
    
    def test_database_connection(self, db_config: Optional[Dict[str, str]] = None) -> Tuple[bool, str]:
        """Test database connection.
        
        Args:
            db_config: Database configuration, or None to use config from file
            
        Returns:
            Tuple containing:
                - Boolean indicating if connection works
                - Error message if connection fails, empty string otherwise
        """
        if db_config is None:
            db_config = self.config.get_database_config()
        
        db_type = db_config.get('type', 'sqlite')
        
        try:
            # Import the appropriate database module dynamically
            db_module = self.import_database_adapter(db_type)
            
            # Test connection
            adapter = db_module.DatabaseAdapter(db_config)
            success = adapter.test_connection()
            
            return success, "" if success else "Failed to connect to database"
        
        except Exception as e:
            return False, f"Error testing database connection: {str(e)}"
    
    def create_admin_user(self, username: str, password: str, email: str) -> bool:
        """Create admin user in the database.
        
        Args:
            username: Admin username
            password: Admin password
            email: Admin email
            
        Returns:
            bool: True if successful, False otherwise
        """
        db_config = self.config.get_database_config()
        db_type = db_config.get('type', 'sqlite')
        
        try:
            # Import the appropriate database module dynamically
            db_module = self.import_database_adapter(db_type)
            
            # Create admin user
            adapter = db_module.DatabaseAdapter(db_config)
            return adapter.create_admin_user(username, password, email)
        
        except Exception as e:
            print(f"Error creating admin user: {e}", file=sys.stderr)
            return False
    
    def get_supported_database_types(self) -> List[str]:
        """Get list of supported database types.
        
        Returns:
            List[str]: List of supported database types
        """
        return ['sqlite', 'mysql', 'postgresql']
    
    def get_database_type_description(self, db_type: str) -> str:
        """Get description of a database type.
        
        Args:
            db_type: Database type
            
        Returns:
            str: Description of the database type
        """
        descriptions = {
            'sqlite': "SQLite - Embedded database, ideal for single-user deployments",
            'mysql': "MySQL - Popular open-source database, good for multi-user deployments",
            'postgresql': "PostgreSQL - Advanced open-source database with extensive features"
        }
        
        return descriptions.get(db_type, "Unknown database type")
