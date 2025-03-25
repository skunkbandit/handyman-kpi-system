"""
PostgreSQL database adapter for the Handyman KPI System Installer.

This module provides a database adapter for PostgreSQL, including functions for
initializing databases, testing connections, and creating users.
"""

import os
import hashlib
import secrets
from typing import Dict, Optional, Any, List

try:
    import psycopg2
    from psycopg2 import Error as PostgresError
except ImportError:
    # If psycopg2 is not installed, provide a placeholder
    # that will fail gracefully when used
    class PostgresError(Exception):
        pass
    
    def psycopg2_missing(*args, **kwargs):
        raise ImportError("psycopg2 is not installed. Please install it with pip.")
    
    # Create a fake psycopg2 module
    class Psycopg2Module:
        def connect(self, *args, **kwargs):
            return psycopg2_missing()
    
    psycopg2 = Psycopg2Module()


class DatabaseAdapter:
    """PostgreSQL database adapter."""
    
    def __init__(self, config: Dict[str, str]):
        """Initialize PostgreSQL adapter.
        
        Args:
            config: Database configuration containing host, port, user, password, and name
        """
        self.config = config
        self.host = config.get('host', 'localhost')
        self.port = int(config.get('port', '5432'))
        self.user = config.get('user', 'postgres')
        self.password = config.get('password', '')
        self.database = config.get('name', 'handyman_kpi')
    
    def _get_connection_params(self, use_database: bool = True) -> Dict[str, Any]:
        """Get PostgreSQL connection parameters.
        
        Args:
            use_database: Whether to connect to the specific database
            
        Returns:
            Dict[str, Any]: Connection parameters
        """
        conn_params = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password
        }
        
        if use_database:
            conn_params['database'] = self.database
        
        return conn_params
    
    def _execute_statements(self, statements: List[str], conn=None, close_conn: bool = True) -> bool:
        """Execute a list of SQL statements.
        
        Args:
            statements: List of SQL statements to execute
            conn: Optional existing connection
            close_conn: Whether to close the connection after execution
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create connection if not provided
            should_close = close_conn
            if conn is None:
                conn = psycopg2.connect(**self._get_connection_params())
                should_close = True
                
            # Execute each statement
            with conn.cursor() as cursor:
                for statement in statements:
                    if statement.strip():
                        cursor.execute(statement)
            
            # Commit changes
            conn.commit()
            
            # Close connection if requested
            if should_close:
                conn.close()
                
            return True
        
        except PostgresError:
            # Attempt to rollback if there was an error
            if conn:
                conn.rollback()
                if should_close:
                    conn.close()
            return False
        except ImportError:
            return False
    
    def test_connection(self) -> bool:
        """Test database connection.
        
        Returns:
            bool: True if connection works, False otherwise
        """
        try:
            # First try connecting without specifying the database
            conn = psycopg2.connect(**self._get_connection_params(use_database=False))
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            conn.close()
            
            # Test succeeded
            return result == (1,)
        
        except PostgresError:
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
            conn = psycopg2.connect(**self._get_connection_params(use_database=False))
            
            # Check if the database exists
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
                exists = cursor.fetchone()
                
                # If the database doesn't exist, create it
                if not exists:
                    # Need to autocommit to create a database
                    old_isolation_level = conn.isolation_level
                    conn.set_isolation_level(0)
                    with conn.cursor() as create_cursor:
                        create_cursor.execute(f"CREATE DATABASE {self.database}")
                    conn.set_isolation_level(old_isolation_level)
            
            conn.close()
            
            # Connect to the created database
            conn = psycopg2.connect(**self._get_connection_params(use_database=True))
            
            # Process schema SQL (split by semicolons)
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            return self._execute_statements(statements, conn)
        
        except PostgresError:
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
            conn = psycopg2.connect(**self._get_connection_params())
            
            # Check if users table exists
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'users'
                    )
                    """
                )
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    conn.close()
                    return False
                
                # Check if admin user already exists
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    # Update existing admin user
                    cursor.execute(
                        """
                        UPDATE users 
                        SET password_hash = %s, salt = %s, email = %s, is_admin = true 
                        WHERE username = %s
                        """,
                        (password_hash, salt, email, username)
                    )
                else:
                    # Insert new admin user
                    cursor.execute(
                        """
                        INSERT INTO users (username, password_hash, salt, email, is_admin) 
                        VALUES (%s, %s, %s, %s, true)
                        """,
                        (username, password_hash, salt, email)
                    )
            
            conn.commit()
            conn.close()
            return True
        
        except PostgresError:
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
            conn = psycopg2.connect(**self._get_connection_params())
            
            # Get PostgreSQL version
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                
                # Get table count
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    """
                )
                table_count = cursor.fetchone()[0]
                
                # Get database size
                cursor.execute("SELECT pg_database_size(%s)", (self.database,))
                db_size = cursor.fetchone()[0]
                
                # Get table information
                cursor.execute(
                    """
                    SELECT tablename, 
                           pg_total_relation_size(quote_ident(tablename)) as total_size
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    """
                )
                tables = cursor.fetchall()
                
                table_info = {}
                for table_name, table_size in tables:
                    # Get row count (approximate for large tables)
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    
                    table_info[table_name] = {
                        'row_count': row_count,
                        'size_bytes': table_size
                    }
            
            conn.close()
            
            return {
                'type': 'postgresql',
                'version': version,
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'size_bytes': db_size,
                'table_count': table_count,
                'tables': table_info
            }
        
        except PostgresError as e:
            return {
                'type': 'postgresql',
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'error': f'Error getting database information: {str(e)}'
            }
        except ImportError:
            return {
                'type': 'postgresql',
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'error': 'psycopg2 is not installed'
            }
