#!/usr/bin/env python3
"""
Initialize the KPI system database with required tables.

Modified for Windows installer to support different database types
and to use configuration from setup wizard.
"""

import os
import sys
import sqlite3
import argparse
import configparser
from datetime import datetime
from pathlib import Path
from werkzeug.security import generate_password_hash

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Initialize KPI system database")
    parser.add_argument('--config', required=True, help='Path to configuration file')
    return parser.parse_args()

def get_script_dir():
    """Get the directory containing this script."""
    return os.path.dirname(os.path.abspath(__file__))

def load_config(config_path):
    """Load configuration from file."""
    config = configparser.ConfigParser()
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    config.read(config_path)
    return config

def read_schema_file(db_type):
    """Read the SQL schema from file based on database type."""
    # Try to find schema file in various locations
    possible_paths = [
        # In the installed app structure
        os.path.join(os.path.dirname(os.path.dirname(get_script_dir())), 'database', f'schema_{db_type}.sql'),
        os.path.join(os.path.dirname(os.path.dirname(get_script_dir())), 'database', 'schema.sql'),
        # In the repository structure
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(get_script_dir()))), 'database', f'schema_{db_type}.sql'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(get_script_dir()))), 'database', 'schema.sql'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return f.read()
    
    raise FileNotFoundError(f"Schema file not found for {db_type}")

def init_sqlite_database(config):
    """Initialize SQLite database."""
    print("Initializing SQLite database...")
    
    # Paths
    app_dir = os.path.dirname(os.path.dirname(get_script_dir()))
    db_dir = os.path.join(app_dir, 'database')
    db_path = os.path.join(db_dir, config['DATABASE']['path'])
    
    # Create database directory if it doesn't exist
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Check if database already exists and backup if needed
    if os.path.exists(db_path):
        backup_path = f"{db_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        os.rename(db_path, backup_path)
        print(f"Existing database backed up to: {backup_path}")
    
    try:
        # Read schema
        schema_sql = read_schema_file('sqlite')
        
        # Connect to database
        print(f"Creating database at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute schema script
        cursor.executescript(schema_sql)
        
        # Create admin user
        if 'ADMIN' in config and 'username' in config['ADMIN'] and 'password' in config['ADMIN']:
            username = config['ADMIN']['username']
            password = config['ADMIN']['password']
            
            # Generate password hash
            password_hash = generate_password_hash(password)
            
            # Insert admin user
            print(f"Creating admin user: {username}")
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, active, created_at, updated_at) VALUES (?, ?, 'admin', 1, ?, ?)",
                (username, password_hash, now, now)
            )
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("SQLite database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing SQLite database: {e}")
        if os.path.exists(db_path):
            os.remove(db_path)
        return False

def init_mysql_database(config):
    """Initialize MySQL database."""
    print("Initializing MySQL database...")
    
    try:
        import pymysql
    except ImportError:
        print("Error: PyMySQL module not found. Please install it with 'pip install pymysql'")
        return False
    
    try:
        # Read schema
        schema_sql = read_schema_file('mysql')
        
        # Connection parameters
        host = config['DATABASE']['host']
        port = int(config['DATABASE']['port'])
        user = config['DATABASE']['user']
        password = config['DATABASE']['password']
        db_name = config['DATABASE']['name']
        
        # Connect to MySQL server
        print(f"Connecting to MySQL server at {host}:{port}")
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        print(f"Creating database {db_name} if not exists")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
        cursor.execute(f"USE `{db_name}`")
        
        # Execute schema script
        print("Creating tables...")
        # Split schema into individual statements
        statements = schema_sql.split(';')
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
        
        # Create admin user
        if 'ADMIN' in config and 'username' in config['ADMIN'] and 'password' in config['ADMIN']:
            username = config['ADMIN']['username']
            password = config['ADMIN']['password']
            
            # Generate password hash
            password_hash = generate_password_hash(password)
            
            # Insert admin user
            print(f"Creating admin user: {username}")
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, active, created_at, updated_at) VALUES (%s, %s, 'admin', 1, %s, %s)",
                (username, password_hash, now, now)
            )
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("MySQL database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing MySQL database: {e}")
        return False

def init_postgresql_database(config):
    """Initialize PostgreSQL database."""
    print("Initializing PostgreSQL database...")
    
    try:
        import psycopg2
    except ImportError:
        print("Error: psycopg2 module not found. Please install it with 'pip install psycopg2-binary'")
        return False
    
    try:
        # Read schema
        schema_sql = read_schema_file('postgresql')
        
        # Connection parameters
        host = config['DATABASE']['host']
        port = int(config['DATABASE']['port'])
        user = config['DATABASE']['user']
        password = config['DATABASE']['password']
        db_name = config['DATABASE']['name']
        
        # Connect to PostgreSQL server
        try:
            # Try to connect to the specific database first
            print(f"Connecting to PostgreSQL database {db_name} at {host}:{port}")
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=db_name
            )
        except psycopg2.OperationalError:
            # Connect to 'postgres' database to create the new database
            print(f"Database '{db_name}' doesn't exist, connecting to 'postgres' database")
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname='postgres'
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Create database
            print(f"Creating database {db_name}")
            cursor.execute(f"CREATE DATABASE {db_name}")
            conn.close()
            
            # Connect to the newly created database
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=db_name
            )
        
        cursor = conn.cursor()
        
        # Execute schema script
        print("Creating tables...")
        cursor.execute(schema_sql)
        
        # Create admin user
        if 'ADMIN' in config and 'username' in config['ADMIN'] and 'password' in config['ADMIN']:
            username = config['ADMIN']['username']
            password = config['ADMIN']['password']
            
            # Generate password hash
            password_hash = generate_password_hash(password)
            
            # Insert admin user
            print(f"Creating admin user: {username}")
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, active, created_at, updated_at) VALUES (%s, %s, 'admin', 1, %s, %s)",
                (username, password_hash, now, now)
            )
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("PostgreSQL database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing PostgreSQL database: {e}")
        return False

def main():
    """Main function."""
    # Parse command line arguments
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Check database type
    db_type = config['DATABASE']['type'].lower()
    
    # Initialize database based on type
    if db_type == 'sqlite':
        success = init_sqlite_database(config)
    elif db_type == 'mysql':
        success = init_mysql_database(config)
    elif db_type == 'postgresql':
        success = init_postgresql_database(config)
    else:
        print(f"Error: Unsupported database type: {db_type}")
        sys.exit(1)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
