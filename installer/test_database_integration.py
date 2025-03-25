"""
Integration test for database adapters and initializer.

This module tests the database adapters and initializer together to ensure
they work correctly with different database types.
"""

import os
import sys
import unittest
import tempfile
import shutil

# Add the parent directory to the path so we can import the installer package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from installer.shared.database.adapters import get_adapter
from installer.shared.database.initializer import DatabaseInitializer


class TestDatabaseIntegration(unittest.TestCase):
    """Test database integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        
        # Create schema directory and file
        self.schema_dir = os.path.join(self.temp_dir, 'schema')
        os.makedirs(self.schema_dir, exist_ok=True)
        
        # Create schema file
        with open(os.path.join(self.schema_dir, 'schema_sqlite.sql'), 'w') as f:
            f.write("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT,
                is_admin INTEGER DEFAULT 0
            );
            """)
        
        # Create initializer
        self.initializer = DatabaseInitializer(schema_dir=self.schema_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initializer_sqlite(self):
        """Test initializer with SQLite."""
        db_config = {
            'type': 'sqlite',
            'path': self.db_path
        }
        
        # Test connection
        status, _ = self.initializer.test_database_connection(db_config)
        self.assertTrue(status)
        
        # Initialize database
        self.assertTrue(self.initializer.initialize_database(db_config))
        
        # Create admin user
        self.assertTrue(self.initializer.create_admin_user(
            'admin', 'Password123', 'admin@example.com', db_config
        ))
        
        # Get database info
        info = self.initializer.get_database_info(db_config)
        self.assertEqual(info['type'], 'sqlite')
        self.assertEqual(info['table_count'], 1)
        self.assertIn('users', info['tables'])
        self.assertEqual(info['tables']['users']['row_count'], 1)
    
    def test_initializer_invalid_config(self):
        """Test initializer with invalid configuration."""
        db_config = {
            'type': 'unknown'
        }
        
        # Test connection
        status, error = self.initializer.test_database_connection(db_config)
        self.assertFalse(status)
        self.assertIn("Unsupported database type", error)
        
        # Initialize database should fail
        self.assertFalse(self.initializer.initialize_database(db_config))


# Run tests if executed directly
if __name__ == '__main__':
    unittest.main()
