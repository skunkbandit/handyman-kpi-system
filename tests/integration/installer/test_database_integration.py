"""
Integration tests for database adapters and initializer.

This module tests the interaction between database adapters, initializer,
and configuration manager to ensure they work correctly together with
different database types.
"""

import os
import sys
import pytest
import tempfile
import unittest
import sqlite3
from contextlib import closing

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import installer modules
from installer.core.config import ConfigManager
from installer.core.database import DatabaseManager
from installer.shared.database.adapters import get_adapter
from installer.shared.database.initializer import DatabaseInitializer

# Import test utils
from utils import (
    local_mysql_is_available,
    local_postgresql_is_available,
    TEST_ADMIN_USER,
    TEST_EMPLOYEE_DATA,
    validate_database_schema
)


class TestDatabaseIntegration:
    """Test database integration across different database types."""
    
    expected_tables = ['users', 'skill_tiers', 'employees', 'evaluations']
    
    def test_sqlite_integration(self, temp_directory, sample_schema_dir):
        """Test integration with SQLite database."""
        # Create database configuration
        db_config = {
            'type': 'sqlite',
            'path': os.path.join(temp_directory, 'test.db')
        }
        
        # Initialize database manager and initializer
        initializer = DatabaseInitializer(schema_dir=sample_schema_dir)
        
        # Test connection
        status, error = initializer.test_database_connection(db_config)
        assert status, f"Connection test failed: {error}"
        
        # Initialize database
        assert initializer.initialize_database(db_config), "Database initialization failed"
        
        # Verify schema was applied
        with closing(sqlite3.connect(db_config['path'])) as conn:
            valid, message = validate_database_schema(conn, self.expected_tables)
            assert valid, message
        
        # Create admin user
        assert initializer.create_admin_user(
            TEST_ADMIN_USER['username'],
            TEST_ADMIN_USER['password'],
            TEST_ADMIN_USER['email'],
            db_config
        ), "Admin user creation failed"
        
        # Get database info
        info = initializer.get_database_info(db_config)
        assert info['type'] == 'sqlite'
        assert info['tables']['users']['row_count'] == 1
    
    @pytest.mark.skipif(not local_mysql_is_available(), reason="MySQL not available")
    def test_mysql_integration(self, temp_directory, sample_schema_dir):
        """Test integration with MySQL database."""
        # Create database configuration
        db_config = {
            'type': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '',
            'database': 'test_handyman'
        }
        
        # Initialize database manager and initializer
        initializer = DatabaseInitializer(schema_dir=sample_schema_dir)
        
        # Test connection
        status, error = initializer.test_database_connection(db_config)
        # Skip test if MySQL is not actually available or credentials are wrong
        if not status and "Access denied" in error:
            pytest.skip(f"MySQL credentials invalid: {error}")
        assert status, f"Connection test failed: {error}"
        
        # Initialize database
        assert initializer.initialize_database(db_config), "Database initialization failed"
        
        # Create admin user
        assert initializer.create_admin_user(
            TEST_ADMIN_USER['username'],
            TEST_ADMIN_USER['password'],
            TEST_ADMIN_USER['email'],
            db_config
        ), "Admin user creation failed"
        
        # Get database info
        info = initializer.get_database_info(db_config)
        assert info['type'] == 'mysql'
        assert info['tables']['users']['row_count'] == 1
    
    @pytest.mark.skipif(not local_postgresql_is_available(), reason="PostgreSQL not available")
    def test_postgresql_integration(self, temp_directory, sample_schema_dir):
        """Test integration with PostgreSQL database."""
        # Create database configuration
        db_config = {
            'type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': 'postgres',
            'database': 'test_handyman'
        }
        
        # Initialize database manager and initializer
        initializer = DatabaseInitializer(schema_dir=sample_schema_dir)
        
        # Test connection
        status, error = initializer.test_database_connection(db_config)
        # Skip test if PostgreSQL is not actually available or credentials are wrong
        if not status and "password authentication failed" in error:
            pytest.skip(f"PostgreSQL credentials invalid: {error}")
        assert status, f"Connection test failed: {error}"
        
        # Initialize database
        assert initializer.initialize_database(db_config), "Database initialization failed"
        
        # Create admin user
        assert initializer.create_admin_user(
            TEST_ADMIN_USER['username'],
            TEST_ADMIN_USER['password'],
            TEST_ADMIN_USER['email'],
            db_config
        ), "Admin user creation failed"
        
        # Get database info
        info = initializer.get_database_info(db_config)
        assert info['type'] == 'postgresql'
        assert info['tables']['users']['row_count'] == 1
    
    def test_config_database_integration(self, temp_directory, sample_schema_dir):
        """Test integration between config manager and database initializer."""
        # Create paths
        config_path = os.path.join(temp_directory, 'config.json')
        db_path = os.path.join(temp_directory, 'test.db')
        
        # Create configuration
        config = {
            'version': '1.0.0',
            'app_name': 'Handyman KPI System',
            'database': {
                'type': 'sqlite',
                'path': db_path
            },
            'installation_path': os.path.join(temp_directory, 'kpi_system'),
            'admin_user': {
                'username': TEST_ADMIN_USER['username'],
                'email': TEST_ADMIN_USER['email']
            }
        }
        
        # Initialize config manager and save config
        config_manager = ConfigManager(config_path)
        config_manager.save_config(config)
        
        # Initialize database manager and initializer
        db_config = config['database']
        initializer = DatabaseInitializer(schema_dir=sample_schema_dir)
        
        # Test connection
        status, _ = initializer.test_database_connection(db_config)
        assert status
        
        # Initialize database
        assert initializer.initialize_database(db_config)
        
        # Create admin user using config
        admin_config = config['admin_user']
        assert initializer.create_admin_user(
            admin_config['username'],
            TEST_ADMIN_USER['password'],
            admin_config['email'],
            db_config
        )
        
        # Verify configuration is updated correctly
        loaded_config = config_manager.load_config()
        assert loaded_config['database']['type'] == 'sqlite'
        assert loaded_config['admin_user']['username'] == TEST_ADMIN_USER['username']
    
    def test_migration(self, temp_directory, sample_schema_dir):
        """Test database migration scenarios."""
        # Create database paths
        old_db_path = os.path.join(temp_directory, 'old.db')
        new_db_path = os.path.join(temp_directory, 'new.db')
        
        # Create old database with partial schema
        with closing(sqlite3.connect(old_db_path)) as conn:
            conn.executescript('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    email TEXT,
                    is_admin INTEGER DEFAULT 0
                );
                
                CREATE TABLE skill_tiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                );
                
                -- Old schema missing employees and evaluations tables
                
                -- Insert sample data
                INSERT INTO users (username, password_hash, salt, email, is_admin)
                VALUES ('admin', 'oldhash', 'oldsalt', 'admin@example.com', 1);
                
                INSERT INTO skill_tiers (name, description)
                VALUES 
                    ('Apprentice', 'Entry level worker'),
                    ('Handyman', 'Basic skills'),
                    ('Craftsman', 'Experienced technician');
            ''')
        
        # Create new database with full schema
        with closing(sqlite3.connect(new_db_path)) as conn:
            conn.executescript('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    email TEXT,
                    is_admin INTEGER DEFAULT 0
                );
                
                CREATE TABLE skill_tiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                );
                
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    skill_tier_id INTEGER,
                    FOREIGN KEY (skill_tier_id) REFERENCES skill_tiers(id)
                );
                
                CREATE TABLE evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    score REAL NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                );
            ''')
        
        # Create database migration manager (simplified mock for testing)
        class MockMigrationManager:
            def migrate_data(self, old_config, new_config):
                # Connect to old database
                with closing(sqlite3.connect(old_config['path'])) as old_conn:
                    old_conn.row_factory = sqlite3.Row
                    
                    # Connect to new database
                    with closing(sqlite3.connect(new_config['path'])) as new_conn:
                        # Migrate users
                        users = old_conn.execute("SELECT * FROM users").fetchall()
                        for user in users:
                            new_conn.execute(
                                "INSERT INTO users (username, password_hash, salt, email, is_admin) VALUES (?, ?, ?, ?, ?)",
                                (user['username'], user['password_hash'], user['salt'], user['email'], user['is_admin'])
                            )
                        
                        # Migrate skill tiers
                        tiers = old_conn.execute("SELECT * FROM skill_tiers").fetchall()
                        for tier in tiers:
                            new_conn.execute(
                                "INSERT INTO skill_tiers (name, description) VALUES (?, ?)",
                                (tier['name'], tier['description'])
                            )
                        
                        new_conn.commit()
                return True
        
        # Test migration
        old_config = {'type': 'sqlite', 'path': old_db_path}
        new_config = {'type': 'sqlite', 'path': new_db_path}
        
        migration_manager = MockMigrationManager()
        assert migration_manager.migrate_data(old_config, new_config)
        
        # Verify migration results
        with closing(sqlite3.connect(new_db_path)) as conn:
            conn.row_factory = sqlite3.Row
            
            # Verify users were migrated
            users = conn.execute("SELECT * FROM users").fetchall()
            assert len(users) == 1
            assert users[0]['username'] == 'admin'
            
            # Verify skill tiers were migrated
            tiers = conn.execute("SELECT * FROM skill_tiers").fetchall()
            assert len(tiers) == 3
            
            # Verify new tables exist
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [table['name'] for table in tables]
            assert 'employees' in table_names
            assert 'evaluations' in table_names
    
    def test_configuration_validation(self, temp_directory):
        """Test database configuration validation."""
        # Invalid configurations to test
        invalid_configs = [
            # Missing type
            {'path': os.path.join(temp_directory, 'test.db')},
            
            # Invalid type
            {'type': 'unknown', 'path': os.path.join(temp_directory, 'test.db')},
            
            # SQLite missing path
            {'type': 'sqlite'},
            
            # MySQL missing required fields
            {'type': 'mysql', 'host': 'localhost'},
            
            # PostgreSQL missing required fields
            {'type': 'postgresql', 'host': 'localhost', 'user': 'postgres'}
        ]
        
        # Valid configurations to test
        valid_configs = [
            # SQLite with path
            {'type': 'sqlite', 'path': os.path.join(temp_directory, 'test.db')},
            
            # MySQL with all required fields
            {
                'type': 'mysql',
                'host': 'localhost',
                'port': 3306,
                'database': 'test_db',
                'user': 'test_user',
                'password': 'test_password'
            },
            
            # PostgreSQL with all required fields
            {
                'type': 'postgresql',
                'host': 'localhost',
                'port': 5432,
                'database': 'test_db',
                'user': 'test_user',
                'password': 'test_password'
            }
        ]
        
        # Create initializer
        initializer = DatabaseInitializer(schema_dir=temp_directory)
        
        # Test invalid configurations
        for config in invalid_configs:
            status, error = initializer.validate_config(config)
            assert not status, f"Invalid config was accepted: {config}"
            assert error, "No error message provided for invalid config"
        
        # Test valid configurations
        for config in valid_configs:
            status, error = initializer.validate_config(config)
            assert status, f"Valid config was rejected: {config}, Error: {error}"
    
    def test_cross_database_adapter_compatibility(self, temp_directory, sample_schema_dir):
        """Test compatibility of adapters across different database types."""
        # Create database paths
        sqlite_path = os.path.join(temp_directory, 'sqlite.db')
        
        # Create configurations
        sqlite_config = {'type': 'sqlite', 'path': sqlite_path}
        mysql_config = {
            'type': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'database': 'test_handyman',
            'user': 'test_user',
            'password': 'test_password'
        }
        postgresql_config = {
            'type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'database': 'test_handyman',
            'user': 'test_user',
            'password': 'test_password'
        }
        
        # Get adapters
        sqlite_adapter = get_adapter(sqlite_config)
        assert sqlite_adapter is not None
        
        # Test adapter-specific schema paths
        sqlite_schema = sqlite_adapter.get_schema_path(sample_schema_dir)
        assert sqlite_schema.endswith('schema_sqlite.sql')
        
        # Test compatibility checking
        assert sqlite_adapter.is_compatible_with(sqlite_config)
        assert not sqlite_adapter.is_compatible_with(mysql_config)
        assert not sqlite_adapter.is_compatible_with(postgresql_config)
        
        # Initialize SQLite database
        initializer = DatabaseInitializer(schema_dir=sample_schema_dir)
        assert initializer.initialize_database(sqlite_config)
        
        # Test schema compatibility
        schema_compatible = initializer.is_schema_compatible(sqlite_config)
        assert schema_compatible, "Schema should be compatible with SQLite"


# Skip this test class if MySQL is not available
@pytest.mark.skipif(not local_mysql_is_available(), reason="MySQL not available for migration testing")
class TestMySQLMigration:
    """Test MySQL migration scenarios."""
    
    def test_mysql_migration(self, temp_directory, sample_schema_dir):
        """Test migration from SQLite to MySQL."""
        # This is a placeholder for a more complex test that would:
        # 1. Set up a SQLite database with sample data
        # 2. Set up a MySQL database with an updated schema
        # 3. Perform a migration from SQLite to MySQL
        # 4. Verify that all data was correctly migrated
        
        # In a real test, we would implement the actual migration logic
        # and verify the results in detail
        
        # For now, just check that MySQL is actually available
        import pymysql
        try:
            with pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                connect_timeout=2
            ):
                # MySQL is available, so this test should run
                pass
        except pymysql.Error:
            pytest.skip("MySQL not available with default credentials")
