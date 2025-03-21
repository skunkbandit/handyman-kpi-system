"""Test suite for database adapters.

This module contains tests for the database adapters to ensure they
function correctly with different database types.
"""

import os
import sys
import unittest
import tempfile
import shutil

# Add the parent directory to the path so we can import the installer package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # noqa

from installer.shared.database.adapters import get_adapter


class TestSQLiteAdapter(unittest.TestCase):
    """Test SQLite database adapter."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.config = {
            'path': self.db_path
        }
        
        # Simple schema for testing
        self.schema = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        );
        """
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_sqlite_connection(self):
        """Test SQLite connection."""
        adapter = get_adapter('sqlite', self.config)
        self.assertTrue(adapter.test_connection())
    
    def test_sqlite_initialization(self):
        """Test SQLite initialization."""
        adapter = get_adapter('sqlite', self.config)
        self.assertTrue(adapter.initialize(self.schema))
        
        # Check that the database was created
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_sqlite_admin_creation(self):
        """Test SQLite admin user creation."""
        adapter = get_adapter('sqlite', self.config)
        adapter.initialize(self.schema)
        
        # Create admin user
        self.assertTrue(adapter.create_admin_user('admin', 'password', 'admin@example.com'))
        
        # Get database info
        info = adapter.get_database_info()
        self.assertEqual(info['type'], 'sqlite')
        self.assertEqual(info['table_count'], 1)
        self.assertIn('users', info['tables'])
        self.assertEqual(info['tables']['users']['row_count'], 1)


# Run tests if executed directly
if __name__ == '__main__':
    unittest.main()