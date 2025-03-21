"""Database initialization utility for the Handyman KPI System Installer.

This module provides a utility class for initializing databases, creating admin users,
and testing database connections using different database adapters.
"""

import os
import logging
from typing import Dict, Tuple, Optional, Any

from .adapters import get_adapter


class DatabaseInitializer:
    """Database initialization utility."""
    
    def __init__(self, schema_dir: Optional[str] = None):
        """Initialize database initializer.
        
        Args:
            schema_dir: Directory containing schema files (default: shared/database)
        """
        self.schema_dir = schema_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..'
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_schema_path(self, db_type: str) -> str:
        """Get schema file path for the specified database type.
        
        Args:
            db_type: Database type ('sqlite', 'mysql', or 'postgresql')
            
        Returns:
            str: Path to schema file
        """
        schema_filename = f"schema_{db_type}.sql"
        return os.path.join(self.schema_dir, schema_filename)
    
    def _read_schema(self, db_type: str) -> str:
        """Read schema file for the specified database type.
        
        Args:
            db_type: Database type ('sqlite', 'mysql', or 'postgresql')
            
        Returns:
            str: Schema SQL
            
        Raises:
            FileNotFoundError: If schema file is not found
        """
        schema_path = self._get_schema_path(db_type)
        
        if not os.path.exists(schema_path):
            # Fall back to sqlite schema if specific one doesn't exist
            fallback_path = self._get_schema_path('sqlite')
            if db_type != 'sqlite' and os.path.exists(fallback_path):
                self.logger.warning(
                    f"Schema file for {db_type} not found. Using SQLite schema as fallback."
                )
                schema_path = fallback_path
            else:
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def test_database_connection(self, db_config: Dict[str, str]) -> Tuple[bool, str]:
        """Test database connection.
        
        Args:
            db_config: Database configuration
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        db_type = db_config.get('type', 'sqlite')
        
        try:
            # Get appropriate adapter
            adapter = get_adapter(db_type, db_config)
            
            # Test connection
            if adapter.test_connection():
                return True, ""
            else:
                return False, "Connection test failed"
        
        except Exception as e:
            self.logger.exception(f"Error testing database connection: {str(e)}")
            return False, str(e)
    
    def initialize_database(self, db_config: Dict[str, str]) -> bool:
        """Initialize database with schema.
        
        Args:
            db_config: Database configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        db_type = db_config.get('type', 'sqlite')
        
        try:
            # Get appropriate adapter
            adapter = get_adapter(db_type, db_config)
            
            # Read schema
            schema_sql = self._read_schema(db_type)
            
            # Initialize database
            return adapter.initialize(schema_sql)
        
        except Exception as e:
            self.logger.exception(f"Error initializing database: {str(e)}")
            return False
    
    def create_admin_user(self, username: str, password: str, email: str, db_config: Dict[str, str]) -> bool:
        """Create admin user in the database.
        
        Args:
            username: Admin username
            password: Admin password
            email: Admin email
            db_config: Database configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        db_type = db_config.get('type', 'sqlite')
        
        try:
            # Get appropriate adapter
            adapter = get_adapter(db_type, db_config)
            
            # Create admin user
            return adapter.create_admin_user(username, password, email)
        
        except Exception as e:
            self.logger.exception(f"Error creating admin user: {str(e)}")
            return False
    
    def get_database_info(self, db_config: Dict[str, str]) -> Dict[str, Any]:
        """Get information about the database.
        
        Args:
            db_config: Database configuration
            
        Returns:
            Dict[str, Any]: Database information
        """
        db_type = db_config.get('type', 'sqlite')
        
        try:
            # Get appropriate adapter
            adapter = get_adapter(db_type, db_config)
            
            # Get database info
            return adapter.get_database_info()
        
        except Exception as e:
            self.logger.exception(f"Error getting database information: {str(e)}")
            return {
                'type': db_type,
                'error': str(e)
            }