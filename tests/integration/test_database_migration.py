"""
Integration tests for database migration scripts.
"""
import pytest
import os
import tempfile
import sqlite3
from kpi_system.backend.app.models import db
from kpi_system.database.migrate_auth import run_migration

def test_schema_creation():
    """Test that the database schema can be created from schema.sql."""
    # Create a temporary database
    fd, path = tempfile.mkstemp()
    conn = sqlite3.connect(path)
    
    try:
        # Read the schema file
        schema_path = os.path.join('database', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema creation script
        conn.executescript(schema_sql)
        
        # Verify tables were created
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check that core tables exist
        expected_tables = [
            'employees',
            'skill_categories',
            'skills',
            'tool_categories',
            'tools',
            'evaluations',
            'eval_skills',
            'eval_tools',
            'special_skills',
            'users',
            'schema_version'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in schema"
            
        # Check schema version
        cursor.execute("SELECT version FROM schema_version")
        version = cursor.fetchone()[0]
        assert version == 1, "Initial schema version should be 1"
            
    finally:
        conn.close()
        os.close(fd)
        os.unlink(path)

def test_auth_migration(app):
    """Test the auth migration script."""
    with app.app_context():
        # Create a temporary database with the app's schema
        temp_db_fd, temp_db_path = tempfile.mkstemp()
        
        try:
            temp_db_uri = f"sqlite:///{temp_db_path}"
            app.config['SQLALCHEMY_DATABASE_URI'] = temp_db_uri
            db.create_all()
            
            # Add a test user without auth fields
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            
            # First make sure the users table doesn't have the auth columns yet
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Let's assume auth migration adds 'last_login' and 'failed_login_attempts'
            assert 'last_login' not in columns
            assert 'failed_login_attempts' not in columns
            
            # Insert a test user
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ('testuser', 'test@example.com', 'hash', 'employee')
            )
            conn.commit()
            
            # Run the auth migration
            run_migration(temp_db_path)
            
            # Verify the migration was successful
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # New columns should be present
            assert 'last_login' in columns
            assert 'failed_login_attempts' in columns
            
            # Original data should be preserved
            cursor.execute("SELECT username, email FROM users WHERE username=?", ('testuser',))
            user = cursor.fetchone()
            assert user is not None
            assert user[0] == 'testuser'
            assert user[1] == 'test@example.com'
            
            # Schema version should be updated
            cursor.execute("SELECT version FROM schema_version")
            version = cursor.fetchone()[0]
            assert version == 2, "Schema version should be updated to 2 after auth migration"
            
            conn.close()
            
        finally:
            os.close(temp_db_fd)
            os.unlink(temp_db_path)