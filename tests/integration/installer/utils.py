"""
Utility functions for integration testing of the installer components.

This module provides helper functions for creating test environments,
mocking database connections, and validating integration behavior.
"""

import os
import sys
import json
import socket
import tempfile
import subprocess
from contextlib import closing
from functools import lru_cache

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Test environment constants
TEST_ADMIN_USER = {
    'username': 'admin',
    'password': 'StrongPassword123!',
    'email': 'admin@example.com'
}

TEST_EMPLOYEE_DATA = [
    {
        'name': 'John Smith',
        'email': 'john.smith@example.com',
        'phone': '555-123-4567',
        'skill_tier': 'Craftsman'
    },
    {
        'name': 'Jane Doe',
        'email': 'jane.doe@example.com',
        'phone': '555-987-6543',
        'skill_tier': 'Master Craftsman'
    },
    {
        'name': 'Mike Johnson',
        'email': 'mike.johnson@example.com',
        'phone': '555-456-7890',
        'skill_tier': 'Apprentice'
    }
]


def is_port_in_use(port, host='localhost'):
    """Check if a port is in use on the host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def find_free_port(start_port=10000, end_port=11000):
    """Find a free port in the given range."""
    for port in range(start_port, end_port):
        if not is_port_in_use(port):
            return port
    raise RuntimeError(f"No free ports found in range {start_port}-{end_port}")


@lru_cache(maxsize=None)
def local_mysql_is_available():
    """Check if MySQL is available for testing."""
    try:
        import pymysql
        with closing(pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            connect_timeout=2
        )):
            return True
    except (ImportError, pymysql.Error):
        return False


@lru_cache(maxsize=None)
def local_postgresql_is_available():
    """Check if PostgreSQL is available for testing."""
    try:
        import psycopg2
        with closing(psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='postgres',
            connect_timeout=2
        )):
            return True
    except (ImportError, psycopg2.Error):
        return False


def create_test_configuration(config_path, database_type='sqlite', temp_dir=None):
    """Create a test configuration file with the specified database type."""
    if temp_dir is None:
        temp_dir = tempfile.gettempdir()
    
    config = {
        'version': '1.0.0',
        'app_name': 'Handyman KPI System',
        'installation_path': os.path.join(temp_dir, 'kpi_system'),
        'admin_user': {
            'username': TEST_ADMIN_USER['username'],
            'email': TEST_ADMIN_USER['email']
        }
    }
    
    # Set database configuration based on type
    if database_type == 'sqlite':
        config['database'] = {
            'type': 'sqlite',
            'path': os.path.join(temp_dir, 'test_db.sqlite')
        }
    elif database_type == 'mysql':
        config['database'] = {
            'type': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'database': 'test_handyman',
            'user': 'test_user',
            'password': 'test_password'
        }
    elif database_type == 'postgresql':
        config['database'] = {
            'type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'database': 'test_handyman',
            'user': 'test_user',
            'password': 'test_password'
        }
    else:
        raise ValueError(f"Unsupported database type: {database_type}")
    
    # Save the configuration
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    return config


def copy_directory_structure(source_dir, dest_dir):
    """Copy directory structure from source to destination."""
    for root, dirs, files in os.walk(source_dir):
        for dir_name in dirs:
            src_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(src_path, source_dir)
            dest_path = os.path.join(dest_dir, rel_path)
            os.makedirs(dest_path, exist_ok=True)


def validate_database_schema(connection, expected_tables):
    """Validate that the database has the expected tables."""
    if hasattr(connection, 'cursor'):
        cursor = connection.cursor()
    else:
        cursor = connection
    
    # Get list of tables
    if connection.__class__.__module__.startswith('sqlite'):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    elif connection.__class__.__module__.startswith('pymysql'):
        cursor.execute("SHOW TABLES")
    elif connection.__class__.__module__.startswith('psycopg2'):
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
        """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    # Check if all expected tables exist
    missing_tables = set(expected_tables) - set(tables)
    if missing_tables:
        return False, f"Missing tables: {', '.join(missing_tables)}"
    
    return True, "Schema validated successfully"
