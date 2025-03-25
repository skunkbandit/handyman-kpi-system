"""
Test suite for PostgreSQL database adapter.

This module contains comprehensive tests for the PostgreSQL database adapter
with mocking to avoid requiring an actual PostgreSQL server for testing.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the main project directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import the get_adapter function
from installer.shared.database.adapters import get_adapter


class TestPostgreSQLAdapter(unittest.TestCase):
    """Test PostgreSQL database adapter with mocking."""
    
    def setUp(self):
        """Set up test environment."""
        # PostgreSQL configuration
        self.config = {
            'host': 'localhost',
            'port': '5432',
            'user': 'postgres',
            'password': 'password',
            'name': 'test_handyman_kpi'
        }
        
        # Simple schema for testing
        self.schema = """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            salt VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            is_admin BOOLEAN DEFAULT FALSE
        );
        """
        
        # Patch psycopg2 to avoid requiring an actual PostgreSQL server
        self.psycopg2_patcher = patch('installer.shared.database.adapters.postgresql.psycopg2')
        self.mock_psycopg2 = self.psycopg2_patcher.start()
        
        # Set up the mock connector
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.mock_psycopg2.connect.return_value = self.mock_connection
        
        # Successful connection test result
        self.mock_cursor.fetchone.return_value = (1,)
        
        # Create adapter
        self.adapter = get_adapter('postgresql', self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.psycopg2_patcher.stop()
    
    def test_adapter_creation(self):
        """Test adapter creation."""
        # Test with valid configuration
        adapter = get_adapter('postgresql', self.config)
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.host, self.config['host'])
        self.assertEqual(adapter.port, int(self.config['port']))
        self.assertEqual(adapter.user, self.config['user'])
        self.assertEqual(adapter.password, self.config['password'])
        self.assertEqual(adapter.database, self.config['name'])
        
        # Test with default configuration
        adapter = get_adapter('postgresql', {})
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.host, 'localhost')
        self.assertEqual(adapter.port, 5432)
        self.assertEqual(adapter.user, 'postgres')
        self.assertEqual(adapter.password, '')
        self.assertEqual(adapter.database, 'handyman_kpi')
    
    def test_connection(self):
        """Test database connection."""
        # Test connection with valid configuration
        self.assertTrue(self.adapter.test_connection())
        
        # Verify mock was called with correct parameters
        self.mock_psycopg2.connect.assert_called_with(
            host='localhost',
            port=5432,
            user='postgres',
            password='password',
            dbname='postgres'  # Should connect to default database first
        )
        
        # Verify SELECT 1 was executed
        self.mock_cursor.execute.assert_called_with("SELECT 1")
    
    def test_connection_failure(self):
        """Test connection failure scenarios."""
        # Make connection fail
        self.mock_psycopg2.connect.side_effect = self.mock_psycopg2.Error("Test error")
        
        # Test connection (should fail)
        self.assertFalse(self.adapter.test_connection())
        
        # Reset side effect
        self.mock_psycopg2.connect.side_effect = None
        
        # Make query fail
        self.mock_cursor.execute.side_effect = self.mock_psycopg2.Error("Test error")
        
        # Test connection (should fail)
        self.assertFalse(self.adapter.test_connection())
        
        # Reset side effect
        self.mock_cursor.execute.side_effect = None
        
        # Make fetchone return invalid result
        self.mock_cursor.fetchone.return_value = (0,)
        
        # Test connection (should fail)
        self.assertFalse(self.adapter.test_connection())
    
    def test_missing_psycopg2(self):
        """Test behavior when psycopg2 is not installed."""
        # Stop current patcher
        self.psycopg2_patcher.stop()
        
        # Create new patcher that simulates ImportError
        import_error_patcher = patch('installer.shared.database.adapters.postgresql.psycopg2', None)
        import_error_patcher.start()
        
        try:
            # Create adapter (should work, but operations will fail)
            adapter = get_adapter('postgresql', self.config)
            
            # Operations should fail gracefully
            self.assertFalse(adapter.test_connection())
            self.assertFalse(adapter.initialize(self.schema))
            self.assertFalse(adapter.create_admin_user("admin", "password", "admin@example.com"))
            
            # get_database_info should return error information
            info = adapter.get_database_info()
            self.assertEqual(info['type'], 'postgresql')
            self.assertIn('error', info)
            self.assertIn('not installed', info['error'])
        
        finally:
            # Stop the import error patcher
            import_error_patcher.stop()
            
            # Restart the original patcher
            self.psycopg2_patcher = patch('installer.shared.database.adapters.postgresql.psycopg2')
            self.mock_psycopg2 = self.psycopg2_patcher.start()
            self.mock_connection = MagicMock()
            self.mock_cursor = MagicMock()
            self.mock_connection.cursor.return_value = self.mock_cursor
            self.mock_psycopg2.connect.return_value = self.mock_connection
            self.mock_cursor.fetchone.return_value = (1,)
            
            # Recreate adapter
            self.adapter = get_adapter('postgresql', self.config)
    
    def test_initialization(self):
        """Test database initialization."""
        # Set up expected behavior
        self.mock_cursor.execute.return_value = None
        
        # First connection to postgres database will check if our database exists
        self.mock_cursor.fetchone.side_effect = [
            None,  # Database doesn't exist
            (1,)   # Other fetchone calls
        ]
        
        # Initialize database
        self.assertTrue(self.adapter.initialize(self.schema))
        
        # Verify CREATE DATABASE was executed
        create_db_calls = [call for call, _ in self.mock_cursor.execute.call_args_list 
                          if "CREATE DATABASE" in str(call)]
        self.assertTrue(any(create_db_calls))
        
        # Verify schema statement was executed
        schema_calls = [call for call, _ in self.mock_cursor.execute.call_args_list 
                       if "CREATE TABLE" in str(call)]
        self.assertTrue(any(schema_calls))
    
    def test_initialization_database_exists(self):
        """Test initialization when database already exists."""
        # Set up expected behavior
        self.mock_cursor.execute.return_value = None
        
        # First connection to postgres database will check if our database exists
        self.mock_cursor.fetchone.side_effect = [
            (1,),  # Database exists
            (1,)   # Other fetchone calls
        ]
        
        # Initialize database
        self.assertTrue(self.adapter.initialize(self.schema))
        
        # Verify CREATE DATABASE was NOT executed
        create_db_calls = [call for call, _ in self.mock_cursor.execute.call_args_list 
                          if "CREATE DATABASE" in str(call)]
        self.assertFalse(any(create_db_calls))
        
        # Verify schema statement was executed
        schema_calls = [call for call, _ in self.mock_cursor.execute.call_args_list 
                       if "CREATE TABLE" in str(call)]
        self.assertTrue(any(schema_calls))
    
    def test_initialization_failure(self):
        """Test initialization failure scenarios."""
        # Make first connection fail
        self.mock_psycopg2.connect.side_effect = self.mock_psycopg2.Error("Test error")
        
        # Test initialization (should fail)
        self.assertFalse(self.adapter.initialize(self.schema))
        
        # Reset side effect
        self.mock_psycopg2.connect.side_effect = None
        
        # Make CREATE DATABASE fail
        def side_effect(query, *args, **kwargs):
            if "CREATE DATABASE" in query:
                raise self.mock_psycopg2.Error("Test error")
            return None
        
        self.mock_cursor.execute.side_effect = side_effect
        
        # Test initialization (should fail)
        self.assertFalse(self.adapter.initialize(self.schema))
    
    def test_admin_user_creation(self):
        """Test admin user creation."""
        # Setup for users table exists check
        def table_exists_side_effect(query, *args, **kwargs):
            if "SELECT to_regclass" in query:
                self.mock_cursor.fetchone.return_value = ('users',)  # Table exists
            return None
        
        self.mock_cursor.execute.side_effect = table_exists_side_effect
        
        # Setup for user exists check
        self.mock_cursor.fetchone.side_effect = [
            ('users',),   # Table exists check
            None,         # User doesn't exist
            (1,)          # Other fetchone calls
        ]
        
        # Create admin user
        username = "admin"
        password = "Password123"
        email = "admin@example.com"
        
        # Reset side effect for execute
        self.mock_cursor.execute.side_effect = None
        
        self.assertTrue(self.adapter.create_admin_user(username, password, email))
        
        # Verify table check was performed
        table_check_calls = [call for call, _ in self.mock_cursor.execute.call_args_list 
                           if "SELECT to_regclass" in str(call)]
        self.assertTrue(any(table_check_calls))
        
        # Verify INSERT was performed
        insert_calls = [call for call, _ in self.mock_cursor.execute.call_args_list 
                      if "INSERT INTO users" in str(call)]
        self.assertTrue(any(insert_calls))
    
    def test_admin_user_update(self):
        """Test admin user update if already exists."""
        # Setup for users table exists check
        def table_exists_side_effect(query, *args, **kwargs):
            if "SELECT to_regclass" in query:
                self.mock_cursor.fetchone.return_value = ('users',)  # Table exists
            return None
        
        self.mock_cursor.execute.side_effect = table_exists_side_effect
        
        # Setup for user exists check
        self.mock_cursor.fetchone.side_effect = [
            ('users',),   # Table exists check
            (1,),         # User exists
            (1,)          # Other fetchone calls
        ]
        
        # Create/update admin user
        username = "admin"
        password = "NewPassword456"
        email = "admin@example.com"
        
        # Reset side effect for execute
        self.mock_cursor.execute.side_effect = None
        
        self.assertTrue(self.adapter.create_admin_user(username, password, email))
        
        # Verify UPDATE was performed instead of INSERT
        update_calls = [call for call, _ in self.mock_cursor.execute.call_args_list 
                      if "UPDATE users SET" in str(call)]
        self.assertTrue(any(update_calls))
    
    def test_admin_user_with_missing_table(self):
        """Test admin user creation with missing users table."""
        # Setup for users table missing
        def table_exists_side_effect(query, *args, **kwargs):
            if "SELECT to_regclass" in query:
                self.mock_cursor.fetchone.return_value = (None,)  # Table doesn't exist
            return None
        
        self.mock_cursor.execute.side_effect = table_exists_side_effect
        
        # Attempt to create admin user without users table
        self.assertFalse(self.adapter.create_admin_user("admin", "password", "admin@example.com"))
    
    def test_admin_user_creation_error(self):
        """Test admin user creation error handling."""
        # Setup for table check success but execution failure
        def side_effect(query, *args, **kwargs):
            if "SELECT to_regclass" in query:
                self.mock_cursor.fetchone.return_value = ('users',)  # Table exists
            elif "SELECT id FROM users" in query:
                self.mock_cursor.fetchone.return_value = None  # User doesn't exist
            elif "INSERT INTO users" in query:
                raise self.mock_psycopg2.Error("Test error")
            return None
        
        self.mock_cursor.execute.side_effect = side_effect
        
        # Attempt to create admin user (should fail)
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
        # Setup mock cursor for database info queries
        expected_version = "14.2"
        expected_table_count = 1
        expected_db_size = 8192
        
        def side_effect(query, *args, **kwargs):
            if "SELECT version()" in query:
                self.mock_cursor.fetchone.return_value = (f"PostgreSQL {expected_version}",)
            elif "SELECT count(*) FROM information_schema.tables" in query:
                self.mock_cursor.fetchone.return_value = (expected_table_count,)
            elif "SELECT pg_database_size" in query:
                self.mock_cursor.fetchone.return_value = (expected_db_size,)
            elif "SELECT tablename" in query:
                self.mock_cursor.fetchall.return_value = [("users", 1)]
            return None
        
        self.mock_cursor.execute.side_effect = side_effect
        
        # Get database info
        info = self.adapter.get_database_info()
        
        # Verify information
        self.assertEqual(info['type'], 'postgresql')
        self.assertEqual(info['version'], expected_version)
        self.assertEqual(info['host'], self.config['host'])
        self.assertEqual(info['port'], int(self.config['port']))
        self.assertEqual(info['database'], self.config['name'])
        self.assertEqual(info['size_bytes'], expected_db_size)
        self.assertEqual(info['table_count'], expected_table_count)
        self.assertIn('users', info['tables'])
        self.assertEqual(info['tables']['users']['row_count'], 1)
    
    def test_get_database_info_with_error(self):
        """Test getting database information with error."""
        # Make connection raise exception
        self.mock_psycopg2.connect.side_effect = self.mock_psycopg2.Error("Test error")
        
        # Get database info (should return error info)
        info = self.adapter.get_database_info()
        self.assertEqual(info['type'], 'postgresql')
        self.assertIn('host', info)
        self.assertIn('error', info)
        self.assertIn('Test error', info['error'])


if __name__ == '__main__':
    unittest.main()
