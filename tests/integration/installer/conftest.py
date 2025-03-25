"""
Test fixtures for installer integration tests.

This module provides fixtures for testing the installer components
in an integrated manner.
"""

import os
import sys
import pytest
import tempfile
import shutil
import sqlite3
from contextlib import closing

# Add the project root to the path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import installer modules
from installer.core.config import ConfigManager
from installer.core.database import DatabaseManager
from installer.shared.database.adapters import SQLiteAdapter, MySQLAdapter, PostgreSQLAdapter


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing and clean it up after."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def config_file(temp_directory):
    """Create a temporary configuration file."""
    config_path = os.path.join(temp_directory, 'installer_config.json')
    
    # Create a basic configuration
    config = {
        'version': '1.0.0',
        'app_name': 'Handyman KPI System',
        'database': {
            'type': 'sqlite',
            'path': os.path.join(temp_directory, 'test_db.sqlite')
        },
        'installation_path': os.path.join(temp_directory, 'kpi_system'),
        'admin_user': {
            'username': 'admin',
            'email': 'admin@example.com'
        }
    }
    
    # Create config manager and save config
    config_manager = ConfigManager(config_path)
    config_manager.save_config(config)
    
    yield config_path


@pytest.fixture
def sqlite_database(temp_directory):
    """Create a temporary SQLite database for testing."""
    db_path = os.path.join(temp_directory, 'test_db.sqlite')
    
    # Create a test database with schema
    with closing(sqlite3.connect(db_path)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    email TEXT,
                    is_admin INTEGER DEFAULT 0
                )
            ''')
            cursor.execute('''
                CREATE TABLE skill_tiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    skill_tier_id INTEGER,
                    FOREIGN KEY (skill_tier_id) REFERENCES skill_tiers(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    score REAL NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                )
            ''')
            
            # Insert sample data
            cursor.execute('''
                INSERT INTO skill_tiers (name, description) VALUES
                ('Apprentice', 'Entry level worker, requires supervision'),
                ('Handyman', 'Basic skills, works independently on simple tasks'),
                ('Craftsman', 'Experienced technician with broad skills'),
                ('Master Craftsman', 'Expert with specialized knowledge'),
                ('Lead Craftsman', 'Team leader with project management skills')
            ''')
            conn.commit()
    
    yield db_path


@pytest.fixture
def database_config(sqlite_database):
    """Create a database configuration for testing."""
    return {
        'type': 'sqlite',
        'path': sqlite_database
    }


@pytest.fixture
def database_manager(database_config):
    """Create a database manager for testing."""
    manager = DatabaseManager(database_config)
    yield manager


@pytest.fixture
def mock_mysql_config():
    """Create a mock MySQL configuration for testing."""
    return {
        'type': 'mysql',
        'host': 'localhost',
        'port': 3306,
        'database': 'test_handyman',
        'user': 'test_user',
        'password': 'test_password'
    }


@pytest.fixture
def mock_postgresql_config():
    """Create a mock PostgreSQL configuration for testing."""
    return {
        'type': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'database': 'test_handyman',
        'user': 'test_user',
        'password': 'test_password'
    }


@pytest.fixture
def sample_schema_dir(temp_directory):
    """Create a directory with sample schema files for different database types."""
    schema_dir = os.path.join(temp_directory, 'schema')
    os.makedirs(schema_dir, exist_ok=True)
    
    # SQLite schema
    with open(os.path.join(schema_dir, 'schema_sqlite.sql'), 'w') as f:
        f.write('''
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
    
    # MySQL schema
    with open(os.path.join(schema_dir, 'schema_mysql.sql'), 'w') as f:
        f.write('''
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                salt VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                is_admin TINYINT DEFAULT 0
            );
            
            CREATE TABLE skill_tiers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT
            );
            
            CREATE TABLE employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                phone VARCHAR(50),
                skill_tier_id INT,
                FOREIGN KEY (skill_tier_id) REFERENCES skill_tiers(id)
            );
            
            CREATE TABLE evaluations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id INT NOT NULL,
                date DATE NOT NULL,
                score FLOAT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );
        ''')
    
    # PostgreSQL schema
    with open(os.path.join(schema_dir, 'schema_postgresql.sql'), 'w') as f:
        f.write('''
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                salt VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                is_admin BOOLEAN DEFAULT FALSE
            );
            
            CREATE TABLE skill_tiers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT
            );
            
            CREATE TABLE employees (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                phone VARCHAR(50),
                skill_tier_id INTEGER,
                FOREIGN KEY (skill_tier_id) REFERENCES skill_tiers(id)
            );
            
            CREATE TABLE evaluations (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER NOT NULL,
                date DATE NOT NULL,
                score FLOAT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );
        ''')
    
    yield schema_dir
