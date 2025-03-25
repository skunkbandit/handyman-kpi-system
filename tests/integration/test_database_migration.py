"""
Integration tests for the database migration system.
This module tests that database migrations run correctly and maintain data integrity.
"""
import os
import pytest
import tempfile
import sqlite3
from kpi_system.backend.app.models import db
from kpi_system.backend.app.utils.migration_manager import MigrationManager
from kpi_system.backend.app.models.schema_version import SchemaVersion

def test_migration_manager_initialization(app):
    """Test that the migration manager initializes properly."""
    with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
        # Create a test database file
        conn = sqlite3.connect(temp_db.name)
        conn.close()
        
        # Initialize migration manager
        with app.app_context():
            manager = MigrationManager(db_path=temp_db.name)
            
            # Verify manager state
            assert manager.db_path == temp_db.name
            assert manager.migrations_dir is not None
            assert os.path.isdir(manager.migrations_dir)

def test_initial_migration(app):
    """Test that the initial migration creates all tables correctly."""
    with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
        # Configure app to use test database
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db.name}'
        
        with app.app_context():
            # Initialize migration manager
            manager = MigrationManager(db_path=temp_db.name)
            
            # Run initial migration
            result = manager.migrate()
            
            # Verify migration was successful
            assert result.success
            assert result.message == "Migration successful"
            
            # Verify schema version was recorded
            schema_version = db.session.query(SchemaVersion).order_by(SchemaVersion.id.desc()).first()
            assert schema_version is not None
            assert schema_version.version == "1.0.0"
            
            # Verify all tables were created
            conn = sqlite3.connect(temp_db.name)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            
            # Check for required tables
            required_tables = [
                'schema_version',
                'users',
                'employees',
                'skill_categories',
                'skills',
                'tool_categories',
                'tools',
                'evaluations',
                'eval_skills',
                'eval_tools',
                'special_skills'
            ]
            
            for table in required_tables:
                assert table in tables, f"Table '{table}' not created"
            
            conn.close()

def test_incremental_migration(app):
    """Test that incremental migrations apply correctly."""
    with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
        # Configure app to use test database
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db.name}'
        
        with app.app_context():
            # Initialize migration manager
            manager = MigrationManager(db_path=temp_db.name)
            
            # Apply initial migration
            manager.migrate()
            
            # Manually set schema version to a lower version to test upgrading
            db.session.query(SchemaVersion).delete()
            db.session.add(SchemaVersion(version="1.0.0"))
            db.session.commit()
            
            # Add test data
            from kpi_system.backend.app.models.user import User
            admin = User(username='migratetest', email='migrate@example.com', role='admin')
            admin.set_password('testpass')
            db.session.add(admin)
            db.session.commit()
            
            # Get user ID for later verification
            user_id = admin.id
            
            # Run migration to next version
            result = manager.migrate()
            
            # Verify migration was successful
            assert result.success
            assert "Migration successful" in result.message
            
            # Verify schema version was updated
            schema_version = db.session.query(SchemaVersion).order_by(SchemaVersion.id.desc()).first()
            assert schema_version is not None
            assert schema_version.version > "1.0.0"
            
            # Verify data was preserved
            admin = db.session.query(User).filter_by(id=user_id).first()
            assert admin is not None
            assert admin.username == 'migratetest'
            assert admin.email == 'migrate@example.com'
            
            # Verify new tables/columns exist if applicable to the migration
            conn = sqlite3.connect(temp_db.name)
            cursor = conn.cursor()
            
            # Check if reports table exists (added in later migration)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
            reports_table_exists = cursor.fetchone() is not None
            
            # If reports table should exist according to current migrations
            if schema_version.version >= "1.1.0":
                assert reports_table_exists, "Reports table not created in migration 1.1.0"
            
            conn.close()

def test_migration_idempotence(app):
    """Test that running the same migration twice has no effect."""
    with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
        # Configure app to use test database
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db.name}'
        
        with app.app_context():
            # Initialize migration manager
            manager = MigrationManager(db_path=temp_db.name)
            
            # Apply initial migration
            result1 = manager.migrate()
            assert result1.success
            
            # Get schema version after first migration
            schema_version1 = db.session.query(SchemaVersion).order_by(SchemaVersion.id.desc()).first()
            
            # Apply migration again
            result2 = manager.migrate()
            assert result2.success
            
            # Get schema version after second migration attempt
            schema_version2 = db.session.query(SchemaVersion).order_by(SchemaVersion.id.desc()).first()
            
            # Verify schema version hasn't changed since it's already at latest
            assert schema_version1.version == schema_version2.version
            
            # Verify message indicates no migration needed
            assert "already at latest version" in result2.message.lower() or "no migration needed" in result2.message.lower()

def test_migration_error_handling(app, monkeypatch):
    """Test that the migration manager handles errors gracefully."""
    with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
        # Configure app to use test database
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db.name}'
        
        with app.app_context():
            # Initialize migration manager
            manager = MigrationManager(db_path=temp_db.name)
            
            # Mock the execute_migration method to raise an exception
            def mock_execute_migration(*args, **kwargs):
                raise Exception("Test migration error")
            
            monkeypatch.setattr(manager, '_execute_migration', mock_execute_migration)
            
            # Attempt migration
            result = manager.migrate()
            
            # Verify error was handled
            assert not result.success
            assert "error" in result.message.lower()
            assert "test migration error" in result.message.lower()
            
            # Verify database was not left in an inconsistent state
            # (Would need to check specific tables based on your system's design)

def test_backup_before_migration(app):
    """Test that a backup is created before migration when requested."""
    with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
        # Configure app to use test database
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db.name}'
        
        with app.app_context():
            # Initialize migration manager
            manager = MigrationManager(db_path=temp_db.name)
            
            # Apply initial migration without backup
            manager.migrate()
            
            # Add test data
            from kpi_system.backend.app.models.user import User
            admin = User(username='backuptest', email='backup@example.com', role='admin')
            admin.set_password('testpass')
            db.session.add(admin)
            db.session.commit()
            
            # Force a migration with backup by setting version back
            db.session.query(SchemaVersion).delete()
            db.session.add(SchemaVersion(version="1.0.0"))
            db.session.commit()
            
            # Migrate with backup
            result = manager.migrate(backup=True)
            
            # Verify migration was successful
            assert result.success
            
            # Verify backup was created
            backup_path = result.backup_path
            assert backup_path is not None
            assert os.path.exists(backup_path)
            
            # Verify backup contains data
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            assert user_count > 0
            
            cursor.execute("SELECT username FROM users WHERE username = 'backuptest'")
            user = cursor.fetchone()
            assert user is not None
            assert user[0] == 'backuptest'
            
            conn.close()
            
            # Clean up backup file
            os.remove(backup_path)
