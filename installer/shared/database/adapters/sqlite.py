"""
SQLite database adapter for the Handyman KPI System Installer.

This module provides a database adapter for SQLite, including functions for
initializing databases, testing connections, and creating users.
"""

import os
import sqlite3
import hashlib
import secrets
from typing import Dict, Optional, Any


class DatabaseAdapter:
    """SQLite database adapter."""
    
    def __init__(self, config: Dict[str, str]):
        """Initialize SQLite adapter.
        
        Args:
            config: Database configuration containing 'path' key
        """
        self.config = config
        self.db_path = config.get('path', 'data/database.db')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
    
    def test_connection(self) -> bool:
        """Test database connection.
        
        Returns:
            bool: True if connection works, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return result == (1,)
        except sqlite3.Error:
            return False
    
    def initialize(self, schema_sql: str) -> bool:
        """Initialize database with schema.
        
        Args:
            schema_sql: SQL schema to execute
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.executescript(schema_sql)
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error:
            return False
    
    def create_admin_user(self, username: str, password: str, email: str) -> bool:
        """Create admin user in the database.
        
        Args:
            username: Admin username
            password: Admin password
            email: Admin email
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate salt and hash password
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)
            
            # Insert admin user
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                return False
            
            # Check if admin user already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing admin user
                cursor.execute(
                    "UPDATE users SET password_hash = ?, salt = ?, email = ?, is_admin = 1 WHERE username = ?",
                    (password_hash, salt, email, username)
                )
            else:
                # Insert new admin user
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt, email, is_admin) VALUES (?, ?, ?, ?, 1)",
                    (username, password_hash, salt, email)
                )
            
            conn.commit()
            conn.close()
            return True
        
        except sqlite3.Error:
            return False
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt.
        
        Args:
            password: Password to hash
            salt: Salt to use
            
        Returns:
            str: Hashed password
        """
        # Create hash with salt
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        # Use SHA-256 for hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password_bytes,
            salt_bytes,
            100000,  # Number of iterations
            dklen=64  # Length of the derived key
        )
        
        return password_hash.hex()
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the database.
        
        Returns:
            Dict[str, Any]: Database information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get SQLite version
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Get database size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            table_info = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                table_info[table] = {'row_count': row_count}
            
            conn.close()
            
            return {
                'type': 'sqlite',
                'version': version,
                'path': self.db_path,
                'size_bytes': db_size,
                'table_count': table_count,
                'tables': table_info
            }
        
        except sqlite3.Error:
            return {
                'type': 'sqlite',
                'path': self.db_path,
                'error': 'Error getting database information'
            }
