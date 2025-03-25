"""
Test suite for database adapter factory function.

This module contains tests for the get_adapter factory function to ensure
it correctly creates adapters for different database types and handles errors.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the main project directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import the get_adapter function
from installer.shared.database.adapters import get_adapter


class TestAdapterFactory(unittest.TestCase):
    """Test database adapter factory function."""
    
    def test_get_sqlite_adapter(self):
        """Test getting SQLite adapter."""
        adapter = get_adapter('sqlite', {'path': 'test.db'})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.__class__.__name__, 'DatabaseAdapter')
        self.assertEqual(adapter.__module__, 'installer.shared.database.adapters.sqlite')
    
    @patch('installer.shared.database.adapters.mysql.mysql')
    def test_get_mysql_adapter(self, mock_mysql):
        """Test getting MySQL adapter."""
        # Set up mock
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_mysql.connector.connect.return_value = mock_connection
        
        adapter = get_adapter('mysql', {
            'host': 'localhost',
            'port': '3306',
            'user': 'root',
            'password': 'password',
            'name': 'test_db'
        })
        
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.__class__.__name__, 'DatabaseAdapter')
        self.assertEqual(adapter.__module__, 'installer.shared.database.adapters.mysql')
    
    @patch('installer.shared.database.adapters.postgresql.psycopg2')
    def test_get_postgresql_adapter(self, mock_psycopg2):
        """Test getting PostgreSQL adapter."""
        # Set up mock
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_connection
        
        adapter = get_adapter('postgresql', {
            'host': 'localhost',
            'port': '5432',
            'user': 'postgres',
            'password': 'password',
            'name': 'test_db'
        })
        
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.__class__.__name__, 'DatabaseAdapter')
        self.assertEqual(adapter.__module__, 'installer.shared.database.adapters.postgresql')
    
    def test_get_adapter_unsupported_type(self):
        """Test getting adapter for unsupported database type."""
        with self.assertRaises(ValueError) as context:
            get_adapter('unsupported', {})
        
        self.assertIn('Unsupported database type', str(context.exception))
    
    @patch('installer.shared.database.adapters.__import__')
    def test_get_adapter_import_error(self, mock_import):
        """Test handling of import error when getting adapter."""
        # Set up mock to raise ImportError
        mock_import.side_effect = ImportError("Test import error")
        
        with self.assertRaises(ImportError) as context:
            get_adapter('mysql', {})
        
        self.assertIn('Failed to load database adapter', str(context.exception))
        self.assertIn('Test import error', str(context.exception))


if __name__ == '__main__':
    unittest.main()
