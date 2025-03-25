#!/usr/bin/env python3
"""
Database migration script for authentication system.

This script updates the database schema to add authentication-related tables and fields.
"""

import os
import sys
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

# Get the database path
DB_DIR = Path(__file__).parent
DB_PATH = os.path.join(DB_DIR, 'kpi_system.db')

# SQL for users table
USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    employee_id INTEGER,
    role TEXT NOT NULL CHECK (role IN ('admin', 'manager', 'employee')),
    active BOOLEAN DEFAULT 1,
    force_password_change BOOLEAN DEFAULT 0,
    reset_token TEXT UNIQUE,
    reset_token_expiry TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
"""

# SQL for schema version tracking
SCHEMA_VERSION_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
"""

# SQL for creating indexes
INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users(employee_id);",
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);"
]

# SQL for default admin user
ADMIN_USER_SQL = """
INSERT OR IGNORE INTO users (username, password_hash, role, active) 
VALUES (?, ?, 'admin', 1);
"""

def run_migration():
    """Run the database migration for authentication."""
    try:
        # Check if database exists
        if not os.path.exists(DB_PATH):
            print(f"Database file not found at {DB_PATH}")
            print("Please run the database initialization script first.")
            sys.exit(1)
        
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create schema version table if it doesn't exist
        cursor.execute(SCHEMA_VERSION_SQL)
        
        # Check if migration has already been applied
        cursor.execute("SELECT version FROM schema_version WHERE version = '1.1'")
        if cursor.fetchone():
            print("Migration has already been applied.")
            conn.close()
            return
        
        # Create users table
        print("Creating users table...")
        cursor.execute(USERS_TABLE_SQL)
        
        # Create indexes
        print("Creating indexes...")
        for index_sql in INDEXES_SQL:
            cursor.execute(index_sql)
        
        # Add default admin user
        print("Adding default admin user...")
        admin_password = 'Admin123'  # For development only
        admin_hash = generate_password_hash(admin_password)
        cursor.execute(ADMIN_USER_SQL, ('admin', admin_hash))
        
        # Update schema version
        cursor.execute(
            "INSERT INTO schema_version (version, description) VALUES (?, ?)",
            ('1.1', 'Added authentication system')
        )
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully.")
        
        # Print default admin credentials for development
        print("\n--- DEVELOPMENT ONLY ---")
        print("Default admin credentials:")
        print("Username: admin")
        print("Password: Admin123")
        print("IMPORTANT: Change this password immediately in production!")
        print("-----------------------\n")
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    run_migration()
