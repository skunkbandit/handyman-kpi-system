"""MySQL database adapter for the Handyman KPI System Installer.

This module provides a database adapter for MySQL, including functions for
initializing databases, testing connections, and creating users.
"""

import os
import hashlib
import secrets
from typing import Dict, Optional, Any

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    # If MySQL connector is not installed, provide a placeholder
    # that will fail gracefully when used
    class MySQLError(Exception):
        pass
    
    def mysql_connector_missing(*args, **kwargs):
        raise ImportError("mysql-connector-python is not installed. Please install it with pip.")
    
    # Create a fake mysql.connector module
    class MySQLConnectorModule:
        def connect(self, *args, **kwargs):
            return mysql_connector_missing()
    
    mysql = type('', (), {'connector': MySQLConnectorModule()})() 


class DatabaseAdapter:
    """MySQL database adapter."""
    
    def __init__(self, config: Dict[str, str]):
        """Initialize MySQL adapter.
        
        Args:
            config: Database configuration containing host, port, user, password, and name
        """
        self.config = config
        self.host = config.get('host', 'localhost')
        self.port = int(config.get('port', '3306'))
        self.user = config.get('user', 'root')
        self.password = config.get('password', '')
        self.database = config.get('name', 'handyman_kpi')
    
    def _get_connection(self, use_database: bool = True):
        """Get MySQL connection.
        
        Args:
            use_database: Whether to connect to the specific database
            
        Returns:
            Connection: MySQL connection
        """
        conn_params = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password
        }
        
        if use_database:
            conn_params['database'] = self.database
        
        return mysql.connector.connect(**conn_params)
    
    def test_connection(self) -> bool:
        """Test database connection.
        
        Returns:
            bool: True if connection works, False otherwise
        """
        try:
            # First try connecting without specifying the database
            conn = self._get_connection(use_database=False)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            # Test succeeded
            return result == (1,)
        
        except MySQLError:
            return False
        except ImportError:
            return False
    
    def initialize(self, schema_sql: str) -> bool:
        """Initialize database with schema.
        
        Args:
            schema_sql: SQL schema to execute
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # First, create the database if it doesn't exist
            conn = self._get_connection(use_database=False)
            cursor = conn.cursor()
            
            # Create database with UTF-8 support
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
            conn.close()
            
            # Connect to the created database
            conn = self._get_connection(use_database=True)
            
            # Process schema SQL (possibly with multiple statements)
            for statement in schema_sql.split(';'):
                if statement.strip():
                    cursor = conn.cursor()
                    cursor.execute(statement)
                    conn.commit()
            
            conn.close()
            return True
        
        except MySQLError:
            return False
        except ImportError:
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
            conn = self._get_connection()
            cursor = conn.cursor(buffered=True)
            
            # Check if users table exists
            cursor.execute("SHOW TABLES LIKE 'users'")
            if not cursor.fetchone():
                return False
            
            # Check if admin user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Update existing admin user
                cursor.execute(
                    "UPDATE users SET password_hash = %s, salt = %s, email = %s, is_admin = 1 WHERE username = %s",
                    (password_hash, salt, email, username)
                )
            else:
                # Insert new admin user
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt, email, is_admin) VALUES (%s, %s, %s, %s, 1)",
                    (username, password_hash, salt, email)
                )
            
            conn.commit()
            conn.close()
            return True
        
        except MySQLError:
            return False
        except ImportError:
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
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get MySQL version
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s", (self.database,))
            table_count = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute(
                """
                SELECT SUM(data_length + index_length) 
                FROM information_schema.tables 
                WHERE table_schema = %s
                """, 
                (self.database,)
            )
            db_size = cursor.fetchone()[0] or 0
            
            # Get table information
            cursor.execute(
                """
                SELECT table_name, table_rows
                FROM information_schema.tables 
                WHERE table_schema = %s
                """, 
                (self.database,)
            )
            tables = cursor.fetchall()
            
            table_info = {}
            for table_name, row_count in tables:
                table_info[table_name] = {'row_count': row_count or 0}
            
            conn.close()
            
            return {
                'type': 'mysql',
                'version': version,
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'size_bytes': db_size,
                'table_count': table_count,
                'tables': table_info
            }
        
        except MySQLError as e:
            return {
                'type': 'mysql',
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'error': f'Error getting database information: {str(e)}'
            }
        except ImportError:
            return {
                'type': 'mysql',
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'error': 'mysql-connector-python is not installed'
            }