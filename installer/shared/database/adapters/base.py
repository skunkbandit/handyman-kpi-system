"""
Base database adapter for the Handyman KPI System Installer.

This module provides a base class for database adapters, defining
the interface that all database adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseDatabaseAdapter(ABC):
    """Base class for database adapters."""
    
    def __init__(self, config: Dict[str, str]):
        """Initialize database adapter.
        
        Args:
            config: Database configuration
        """
        self.config = config
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test database connection.
        
        Returns:
            bool: True if connection works, False otherwise
        """
        pass
    
    @abstractmethod
    def initialize(self, schema_sql: str) -> bool:
        """Initialize database with schema.
        
        Args:
            schema_sql: SQL schema to execute
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def create_admin_user(self, username: str, password: str, email: str) -> bool:
        """Create admin user in the database.
        
        Args:
            username: Admin username
            password: Admin password
            email: Admin email
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database.
        
        Returns:
            Dict[str, Any]: Database information
        """
        pass
