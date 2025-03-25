"""
Test suite for database initializer.

This module contains comprehensive tests for the DatabaseInitializer class
to ensure it correctly initializes databases using the appropriate adapter.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open

# Add the main project directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import the DatabaseInitializer class
from installer.shared.database.initializer import DatabaseInitializer


class TestDatabaseInitializer(unittest.TestCase):
    """Test DatabaseInitializer class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for schema files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create schema files
        self.sqlite_schema = "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT);"
        self.mysql_schema = "CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255));"
        self.postgresql_schema = "CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(255));"
        
        with open(os.path.join(self.temp_dir, 'schema_sqlite.sql'), 'w') as f:
            f.write(self.sqlite_schema)
        
        with open(os.path.join(self.temp_dir, 'schema_mysql.sql'), 'w') as f:
            f.write(self.mysql_schema)
        
        with open(os.path.join(self.temp_dir, 'schema_postgresql.sql'), 'w') as f:
            f.write(self.postgresql_schema)
        
        # Create initializer with test schema directory
        self.initializer = DatabaseInitializer(schema_dir=self.temp_dir)
        
        # Common database configuration
        self.sqlite_config = {'type': 'sqlite', 'path': 'test.db'}
        self.mysql_config = {
            'type': 'mysql',
            'host': 'localhost',
            'port': '3306',
            'user': 'root',
            'password': 'password',
            'name': 'test_db'
        }
        self.postgresql_config = {
            'type': 'postgresql',
            'host': 'localhost',
            'port': '5432',
            'user': 'postgres',
            'password': 'password',
            'name': 'test_db'
        }
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initializer_creation(self):
        """Test initializer creation."""
        # Test with explicit schema directory
        initializer = DatabaseInitializer(schema_dir=self.temp_dir)
        self.assertEqual(initializer.schema_dir, self.temp_dir)
        
        # Test with default schema directory
        with patch('os.path.dirname', return_value='/fake/path'):
            initializer = DatabaseInitializer()
            self.assertEqual(initializer.schema_dir, '/fake/path/..')
    
    def test_get_schema_path(self):
        """Test getting schema file path."""
        # Test valid database types
        self.assertEqual(
            self.initializer._get_schema_path('sqlite'),
            os.path.join(self.temp_dir, 'schema_sqlite.sql')
        )
        
        self.assertEqual(
            self.initializer._get_schema_path('mysql'),
            os.path.join(self.temp_dir, 'schema_mysql.sql')
        )
        
        self.assertEqual(
            self.initializer._get_schema_path('postgresql'),
            os.path.join(self.temp_dir, 'schema_postgresql.sql')
        )
    
    def test_read_schema(self):
        """Test reading schema files."""
        # Test reading SQLite schema
        schema = self.initializer._read_schema('sqlite')
        self.assertEqual(schema, self.sqlite_schema)
        
        # Test reading MySQL schema
        schema = self.initializer._read_schema('mysql')
        self.assertEqual(schema, self.mysql_schema)
        
        # Test reading PostgreSQL schema
        schema = self.initializer._read_schema('postgresql')
        self.assertEqual(schema, self.postgresql_schema)
    
    def test_read_schema_file_not_found(self):
        """Test reading schema file that doesn't exist."""
        # Test with non-existent schema file and no fallback
        with self.assertRaises(FileNotFoundError):
            # Remove the SQLite schema file
            os.remove(os.path.join(self.temp_dir, 'schema_sqlite.sql'))
            
            # Attempt to read the schema (should fail)
            self.initializer._read_schema('sqlite')
    
    def test_read_schema_with_fallback(self):
        """Test reading schema file with fallback to SQLite schema."""
        # Create initializer with custom schema directory
        custom_dir = os.path.join(self.temp_dir, 'custom')
        os.makedirs(custom_dir)
        
        # Create only SQLite schema in custom directory
        with open(os.path.join(custom_dir, 'schema_sqlite.sql'), 'w') as f:
            f.write(self.sqlite_schema)
        
        # Create initializer with custom schema directory
        initializer = DatabaseInitializer(schema_dir=custom_dir)
        
        # Test reading MySQL schema (should fall back to SQLite)
        with patch('logging.Logger.warning') as mock_warning:
            schema = initializer._read_schema('mysql')
            
            # Verify warning was logged
            mock_warning.assert_called_once()
            self.assertIn('fallback', str(mock_warning.call_args))
            
            # Verify SQLite schema was returned as fallback
            self.assertEqual(schema, self.sqlite_schema)
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_test_database_connection(self, mock_get_adapter):
        """Test testing database connection."""
        # Set up mock adapter
        mock_adapter = MagicMock()
        mock_adapter.test_connection.return_value = True
        mock_get_adapter.return_value = mock_adapter
        
        # Test connection (should succeed)
        success, error = self.initializer.test_database_connection(self.sqlite_config)
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # Verify adapter was created with correct type
        mock_get_adapter.assert_called_with('sqlite', self.sqlite_config)
        
        # Verify test_connection was called
        mock_adapter.test_connection.assert_called_once()
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_test_database_connection_failure(self, mock_get_adapter):
        """Test testing database connection failure."""
        # Set up mock adapter that fails connection test
        mock_adapter = MagicMock()
        mock_adapter.test_connection.return_value = False
        mock_get_adapter.return_value = mock_adapter
        
        # Test connection (should fail)
        success, error = self.initializer.test_database_connection(self.sqlite_config)
        self.assertFalse(success)
        self.assertEqual(error, "Connection test failed")
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_test_database_connection_exception(self, mock_get_adapter):
        """Test testing database connection with exception."""
        # Set up mock get_adapter to raise exception
        mock_get_adapter.side_effect = ValueError("Unsupported database type")
        
        # Test connection (should fail)
        success, error = self.initializer.test_database_connection(self.sqlite_config)
        self.assertFalse(success)
        self.assertEqual(error, "Unsupported database type")
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_initialize_database(self, mock_get_adapter):
        """Test initializing database."""
        # Set up mock adapter
        mock_adapter = MagicMock()
        mock_adapter.initialize.return_value = True
        mock_get_adapter.return_value = mock_adapter
        
        # Initialize database (should succeed)
        self.assertTrue(self.initializer.initialize_database(self.sqlite_config))
        
        # Verify adapter was created with correct type
        mock_get_adapter.assert_called_with('sqlite', self.sqlite_config)
        
        # Verify initialize was called with correct schema
        mock_adapter.initialize.assert_called_once()
        schema = mock_adapter.initialize.call_args[0][0]
        self.assertEqual(schema, self.sqlite_schema)
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_initialize_database_failure(self, mock_get_adapter):
        """Test initializing database failure."""
        # Set up mock adapter that fails initialization
        mock_adapter = MagicMock()
        mock_adapter.initialize.return_value = False
        mock_get_adapter.return_value = mock_adapter
        
        # Initialize database (should fail)
        self.assertFalse(self.initializer.initialize_database(self.sqlite_config))
        
        # Verify initialize was called
        mock_adapter.initialize.assert_called_once()
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_initialize_database_exception(self, mock_get_adapter):
        """Test initializing database with exception."""
        # Set up mock get_adapter to raise exception
        mock_get_adapter.side_effect = ValueError("Unsupported database type")
        
        # Initialize database (should fail)
        self.assertFalse(self.initializer.initialize_database(self.sqlite_config))
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_create_admin_user(self, mock_get_adapter):
        """Test creating admin user."""
        # Set up mock adapter
        mock_adapter = MagicMock()
        mock_adapter.create_admin_user.return_value = True
        mock_get_adapter.return_value = mock_adapter
        
        # Create admin user (should succeed)
        username = "admin"
        password = "Password123"
        email = "admin@example.com"
        
        self.assertTrue(self.initializer.create_admin_user(
            username, password, email, self.sqlite_config
        ))
        
        # Verify adapter was created with correct type
        mock_get_adapter.assert_called_with('sqlite', self.sqlite_config)
        
        # Verify create_admin_user was called with correct parameters
        mock_adapter.create_admin_user.assert_called_with(username, password, email)
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_create_admin_user_failure(self, mock_get_adapter):
        """Test creating admin user failure."""
        # Set up mock adapter that fails user creation
        mock_adapter = MagicMock()
        mock_adapter.create_admin_user.return_value = False
        mock_get_adapter.return_value = mock_adapter
        
        # Create admin user (should fail)
        self.assertFalse(self.initializer.create_admin_user(
            "admin", "password", "admin@example.com", self.sqlite_config
        ))
        
        # Verify create_admin_user was called
        mock_adapter.create_admin_user.assert_called_once()
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_create_admin_user_exception(self, mock_get_adapter):
        """Test creating admin user with exception."""
        # Set up mock get_adapter to raise exception
        mock_get_adapter.side_effect = ValueError("Unsupported database type")
        
        # Create admin user (should fail)
        self.assertFalse(self.initializer.create_admin_user(
            "admin", "password", "admin@example.com", self.sqlite_config
        ))
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_get_database_info(self, mock_get_adapter):
        """Test getting database information."""
        # Set up mock adapter
        mock_adapter = MagicMock()
        expected_info = {
            'type': 'sqlite',
            'version': '3.36.0',
            'path': 'test.db',
            'size_bytes': 4096,
            'table_count': 1,
            'tables': {'users': {'row_count': 1}}
        }
        mock_adapter.get_database_info.return_value = expected_info
        mock_get_adapter.return_value = mock_adapter
        
        # Get database info
        info = self.initializer.get_database_info(self.sqlite_config)
        
        # Verify adapter was created with correct type
        mock_get_adapter.assert_called_with('sqlite', self.sqlite_config)
        
        # Verify get_database_info was called
        mock_adapter.get_database_info.assert_called_once()
        
        # Verify returned info matches expected info
        self.assertEqual(info, expected_info)
    
    @patch('installer.shared.database.initializer.get_adapter')
    def test_get_database_info_exception(self, mock_get_adapter):
        """Test getting database information with exception."""
        # Set up mock get_adapter to raise exception
        mock_get_adapter.side_effect = ValueError("Unsupported database type")
        
        # Get database info (should return error info)
        info = self.initializer.get_database_info(self.sqlite_config)
        
        self.assertEqual(info['type'], 'sqlite')
        self.assertIn('error', info)
        self.assertEqual(info['error'], "Unsupported database type")
    
    def test_integration_with_sqlite(self):
        """Integration test with SQLite adapter."""
        # Use a real SQLite database for this test
        db_path = os.path.join(self.temp_dir, 'integration_test.db')
        config = {'type': 'sqlite', 'path': db_path}
        
        # Test connection
        success, error = self.initializer.test_database_connection(config)
        self.assertTrue(success, f"Connection test failed: {error}")
        
        # Initialize database
        self.assertTrue(self.initializer.initialize_database(config))
        
        # Create admin user
        self.assertTrue(self.initializer.create_admin_user(
            "admin", "Password123", "admin@example.com", config
        ))
        
        # Get database info
        info = self.initializer.get_database_info(config)
        
        # Verify information
        self.assertEqual(info['type'], 'sqlite')
        self.assertIn('version', info)
        self.assertEqual(info['path'], db_path)
        self.assertIn('size_bytes', info)
        self.assertEqual(info['table_count'], 1)
        self.assertIn('users', info['tables'])
        self.assertEqual(info['tables']['users']['row_count'], 1)


if __name__ == '__main__':
    unittest.main()
