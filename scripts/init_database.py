#!/usr/bin/env python3
"""
Initialize the KPI system database with required tables.

This script creates the SQLite database file and sets up all required tables
for the KPI system based on the models defined in the application.
"""

import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from werkzeug.security import generate_password_hash

# Path to the database file and directory
DB_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "kpi-system" / "database"
DB_FILE = DB_DIR / "kpi_system.db"

# Get the schema.sql file
SCHEMA_FILE = DB_DIR / "schema.sql"

def read_schema_file():
    """Read the SQL schema from file"""
    try:
        with open(SCHEMA_FILE, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Schema file not found: {SCHEMA_FILE}")
        sys.exit(1)

def create_database():
    """Create the SQLite database and initialize tables"""
    # Create database directory if it doesn't exist
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        print(f"Created database directory: {DB_DIR}")
    
    # Check if database already exists
    db_exists = os.path.exists(DB_FILE)
    
    if db_exists:
        choice = input(f"Database file already exists: {DB_FILE}\nDo you want to reinitialize it? (y/n): ")
        if choice.lower() != 'y':
            print("Database initialization canceled.")
            return
    
    # Read schema from file
    schema_sql = read_schema_file()
    
    # Connect to the database
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Execute schema script
        print("Creating database schema...")
        cursor.executescript(schema_sql)
        
        # Create admin user with secure password hashing
        print("\nCreating admin user:")
        username = input("Enter admin username (default: admin): ") or "admin"
        password = input("Enter admin password (default: Admin123): ") or "Admin123"
        
        # Use Werkzeug's password hashing
        password_hash = generate_password_hash(password)
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            # Update existing user
            cursor.execute(
                "UPDATE users SET password_hash = ?, role = 'admin', active = 1 WHERE username = ?",
                (password_hash, username)
            )
        else:
            # Create new user
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, active, created_at, updated_at) VALUES (?, ?, 'admin', 1, ?, ?)",
                (username, password_hash, datetime.now(), datetime.now())
            )
        
        # Commit all changes
        conn.commit()
        print(f"Admin user '{username}' created successfully.")
        print("\nDatabase initialization completed!")
        
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
        if os.path.exists(DB_FILE) and not db_exists:
            os.remove(DB_FILE)
            print("Removed incomplete database file.")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to run the database initialization"""
    print("Initializing KPI System Database")
    create_database()

if __name__ == "__main__":
    main()
