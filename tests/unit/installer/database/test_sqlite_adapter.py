"""
Test suite for SQLite database adapter.

This module contains comprehensive tests for the SQLite database adapter
to ensure it functions correctly and handles edge cases appropriately.
"""

import os
import sys
import unittest
import tempfile
import shutil
import sqlite3
from unittest.mock import patch, MagicMock

# Add the main project directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from installer.shared.database.adapters import get_adapter


class TestSQLiteAdapter(unittest.TestCase):
    """Test SQLite database adapter."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test database
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
        
        # Create adapter
        self.adapter = get_adapter('sqlite', self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_adapter_creation(self):
        """Test adapter creation."""
        # Test with valid configuration
        adapter = get_adapter('sqlite', self.config)
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.db_path, self.db_path)
        
        # Test with missing path (should use default)
        adapter = get_adapter('sqlite', {})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.db_path, 'data/database.db')
    
    def test_connection(self):
        """Test database connection."""
        # Test connection to new database (should create file)
        self.assertTrue(self.adapter.test_connection())
        self.assertTrue(os.path.exists(self.db_path))
        
        # Test connection to existing database
        self.assertTrue(self.adapter.test_connection())
    
    def test_connection_failure(self):
        """Test connection failure scenarios."""
        # Test with invalid path (directory instead of file)
        invalid_dir = os.path.join(self.temp_dir, 'invalid_dir')
        os.makedirs(invalid_dir, exist_ok=True)
        
        adapter = get_adapter('sqlite', {'path': invalid_dir})
        self.assertFalse(adapter.test_connection())
    
    def test_initialization(self):
        """Test database initialization."""
        # Initialize database
        self.assertTrue(self.adapter.initialize(self.schema))
        self.assertTrue(os.path.exists(self.db_path))
        
        # Verify table was created
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()
    
    def test_initialization_with_invalid_schema(self):
        """Test initialization with invalid schema."""
        # Test with invalid SQL
        invalid_schema = "CREATE TABLE invalid_syntax (id INTEGER PRIMARY"  # Missing closing parenthesis
        self.assertFalse(self.adapter.initialize(invalid_schema))
    
    def test_admin_user_creation(self):
        """Test admin user creation."""
        # Initialize database
        self.adapter.initialize(self.schema)
        
        # Create admin user
        username = "admin"
        password = "Password123"
        email = "admin@example.com"
        
        self.assertTrue(self.adapter.create_admin_user(username, password, email))
        
        # Verify admin user was created
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(user)
        self.assertEqual(user[1], username)
        self.assertEqual(user[2], email)
        self.assertEqual(user[3], 1)  # is_admin = 1
    
    def test_admin_user_update(self):
        """Test admin user update if already exists."""
        # Initialize database and create initial admin user
        self.adapter.initialize(self.schema)
        
        username = "admin"
        password1 = "Password123"
        email1 = "admin@example.com"
        
        self.adapter.create_admin_user(username, password1, email1)
        
        # Update admin user with new email and password
        password2 = "NewPassword456"
        email2 = "new_admin@example.com"
        
        self.assertTrue(self.adapter.create_admin_user(username, password2, email2))
        
        # Verify admin user was updated
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(user)
        self.assertEqual(user[1], username)
        self.assertEqual(user[2], email2)
        self.assertEqual(user[3], 1)  # is_admin = 1
    
    def test_admin_user_with_missing_table(self):
        """Test admin user creation with missing users table."""
        # Initialize empty database
        conn = sqlite3.connect(self.db_path)
        conn.close()
        
        # Attempt to create admin user without users table
        self.assertFalse(self.adapter.create_admin_user("admin", "password", "admin@example.com"))
    
    def test_password_hashing(self):
        """Test password hashing."""
        password = "TestPassword123"
        salt = "0123456789abcdef"
        
        # Hash password
        password_hash = self.adapter._hash_password(password, salt)
        
        # Verify hash is not empty and is a hex string
        self.assertTrue(password_hash)
        self.assertTrue(all(c in '0123456789abcdef' for c in password_hash))
        
        # Same password and salt should produce same hash
        password_hash2 = self.adapter._hash_password(password, salt)
        self.assertEqual(password_hash, password_hash2)
        
        # Different password should produce different hash
        password_hash3 = self.adapter._hash_password("DifferentPassword", salt)
        self.assertNotEqual(password_hash, password_hash3)
        
        # Different salt should produce different hash
        password_hash4 = self.adapter._hash_password(password, "fedcba9876543210")
        self.assertNotEqual(password_hash, password_hash4)
    
    def test_get_database_info(self):
        """Test getting database information."""
        # Initialize database with schema and create admin user
        self.adapter.initialize(self.schema)
        self.adapter.create_admin_user("admin", "password", "admin@example.com")
        
        # Get database info
        info = self.adapter.get_database_info()
        
        # Verify information
        self.assertEqual(info['type'], 'sqlite')
        self.assertEqual(info['path'], self.db_path)
        self.assertIn('version', info)
        self.assertIn('size_bytes', info)
        self.assertEqual(info['table_count'], 1)
        self.assertIn('users', info['tables'])
        self.assertEqual(info['tables']['users']['row_count'], 1)
    
    def test_get_database_info_with_error(self):
        """Test getting database information with error."""
        # Create adapter with non-existent database
        adapter = get_adapter('sqlite', {'path': os.path.join(self.temp_dir, 'nonexistent.db')})
        
        # Get database info (should return error info)
        info = adapter.get_database_info()
        self.assertEqual(info['type'], 'sqlite')
        self.assertIn('path', info)
        self.assertIn('error', info)
    
    @patch('sqlite3.connect')
    def test_connection_error(self, mock_connect):
        """Test connection error handling."""
        # Mock sqlite3.connect to raise exception
        mock_connect.side_effect = sqlite3.Error("Test error")
        
        # Test connection (should fail)
        self.assertFalse(self.adapter.test_connection())
    
    @patch('sqlite3.connect')
    def test_initialization_error(self, mock_connect):
        """Test initialization error handling."""
        # Create mock connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        # Make executescript raise exception
        mock_connection.executescript.side_effect = sqlite3.Error("Test error")
        
        # Configure the mock to return our mock connection
        mock_connect.return_value = mock_connection
        
        # Test initialization (should fail)
        self.assertFalse(self.adapter.initialize(self.schema))
    
    @patch('sqlite3.connect')
    def test_admin_user_creation_error(self, mock_connect):
        """Test admin user creation error handling."""
        # Create mock connection and cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = True  # Pretend users table exists
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        # Make execute raise exception
        mock_cursor.execute.side_effect = sqlite3.Error("Test error")
        
        # Configure the mock to return our mock connection
        mock_connect.return_value = mock_connection
        
        # Test admin user creation (should fail)
        self.assertFalse(self.adapter.create_admin_user("admin", "password", "admin@example.com"))


if __name__ == '__main__':
    unittest.main()
