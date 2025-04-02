# Database Schema Fix Script

import os
import sys
import sqlite3
import json
import logging
from pathlib import Path

# Configure logging
def setup_logging():
    app_data_dir = os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
        "Handyman KPI System"
    )
    
    # Create log directory
    log_dir = os.path.join(app_data_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up logging
    log_file = os.path.join(log_dir, "database_schema_fix.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
    
    return app_data_dir

def get_database_path(app_data_dir):
    """Get the database path from config file or use default."""
    config_file = os.path.join(app_data_dir, "config", "database.json")
    
    if os.path.exists(config_file):
        import json
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'path' in config:
                    logging.info(f"Using database path from config: {config['path']}")
                    return config['path']
        except Exception as e:
            logging.error(f"Error reading config file: {e}")
    
    # Default path
    db_path = os.path.join(app_data_dir, "database", "kpi_system.db")
    logging.info(f"Using default database path: {db_path}")
    return db_path

def get_schema_path():
    """Get the path to the schema.sql file."""
    # Look in various locations for schema.sql
    possible_paths = [
        r"C:\Users\dtest\KPI Project\kpi-system\database\schema.sql",
        r"C:\Users\dtest\KPI Project\database\schema.sql",
        r"C:\Program Files\Handyman KPI System\kpi-system\database\schema.sql",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logging.info(f"Found schema file at: {path}")
            return path
    
    logging.error("Could not find schema.sql file")
    return None

def get_table_schema(db_path, table_name):
    """Get the schema for a specific table from the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Close connection
        conn.close()
        
        if not columns:
            logging.warning(f"Table {table_name} does not exist in the database")
            return None
        
        # Format column info as a dictionary
        column_info = {}
        for col in columns:
            col_id, name, data_type, not_null, default_val, is_pk = col
            column_info[name] = {
                'type': data_type,
                'not_null': bool(not_null),
                'default': default_val,
                'primary_key': bool(is_pk)
            }
        
        return column_info
    
    except Exception as e:
        logging.error(f"Error getting table schema: {e}")
        return None

def get_expected_schema(schema_path, table_name):
    """Parse the schema.sql file to get the expected schema for a table."""
    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Find the CREATE TABLE statement for the specific table
        import re
        table_pattern = re.compile(r'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+' + table_name + r'\s*\((.*?)\);', re.DOTALL | re.IGNORECASE)
        match = table_pattern.search(schema_sql)
        
        if not match:
            logging.error(f"Could not find CREATE TABLE statement for {table_name} in schema.sql")
            return None
        
        table_def = match.group(1)
        
        # Parse column definitions
        columns = {}
        
        for line in table_def.split('\n'):
            line = line.strip()
            if not line or line.startswith('--') or line.startswith('FOREIGN KEY') or line.startswith('PRIMARY KEY'):
                continue
                
            # Extract column name
            col_match = re.match(r'(\w+)', line)
            if not col_match:
                continue
                
            col_name = col_match.group(1)
            
            # Extract column type
            type_match = re.search(r'\s+([\w\(\)]+)', line)
            col_type = type_match.group(1) if type_match else "TEXT"
            
            # Check for primary key
            is_pk = "PRIMARY KEY" in line.upper()
            
            # Check for not null constraint
            not_null = "NOT NULL" in line.upper()
            
            # Extract default value if present
            default_match = re.search(r'DEFAULT\s+(.+?)(?:,|$|\s+CHECK)', line, re.IGNORECASE)
            default_val = default_match.group(1) if default_match else None
            
            columns[col_name] = {
                'type': col_type,
                'not_null': not_null,
                'default': default_val,
                'primary_key': is_pk
            }
        
        return columns
    
    except Exception as e:
        logging.error(f"Error parsing schema file: {e}")
        return None

def recreate_database(db_path, schema_path):
    """Drop and recreate the database using the schema file."""
    try:
        # Backup the existing database if it exists
        if os.path.exists(db_path):
            backup_path = f"{db_path}.bak"
            import shutil
            shutil.copy2(db_path, backup_path)
            logging.info(f"Created database backup at: {backup_path}")
        
        # Read schema SQL
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute the schema SQL
        conn.executescript(schema_sql)
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        logging.info("Recreated database with correct schema")
        return True
    
    except Exception as e:
        logging.error(f"Error recreating database: {e}")
        return False

def fix_database_schema(db_path, table_name, expected_columns, current_columns):
    """Fix the database schema by adding missing columns."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if current_columns is None:
            # Table doesn't exist, create it from scratch
            schema_path = get_schema_path()
            if not schema_path:
                logging.error("Cannot create table without schema file")
                return False
                
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                
            conn.executescript(schema_sql)
            conn.commit()
            logging.info(f"Created table {table_name} from schema file")
            conn.close()
            return True
        
        # Find missing columns
        missing_columns = []
        for col_name, col_def in expected_columns.items():
            if col_name not in current_columns:
                col_type = col_def['type']
                
                # Handle NOT NULL columns differently - need to provide a default value
                if col_def['not_null'] and col_def['default'] is None:
                    # Choose appropriate default based on type
                    if col_type.upper() in ['INTEGER', 'INT']:
                        default_val = "0"
                    elif col_type.upper() == 'BOOLEAN':
                        default_val = "0"
                    else:  # TEXT, VARCHAR, etc.
                        default_val = "''"
                        
                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type} NOT NULL DEFAULT {default_val}"
                else:
                    # Regular case - use the default if specified
                    constraints = ""
                    if col_def['not_null']:
                        constraints += " NOT NULL"
                    if col_def['default'] is not None:
                        constraints += f" DEFAULT {col_def['default']}"
                    
                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}{constraints}"
                
                missing_columns.append((col_name, alter_sql))
        
        # Add missing columns
        success = True
        for col_name, alter_sql in missing_columns:
            try:
                cursor.execute(alter_sql)
                logging.info(f"Added missing column: {col_name}")
            except Exception as e:
                logging.error(f"Error adding column {col_name}: {e}")
                success = False
        
        # Commit changes if any were made
        if missing_columns:
            conn.commit()
        
        conn.close()
        
        if not success:
            logging.warning("Not all columns could be added - attempting to recreate database")
            schema_path = get_schema_path()
            if schema_path:
                return recreate_database(db_path, schema_path)
            return False
        
        if missing_columns:
            logging.info(f"Fixed {len(missing_columns)} missing columns in {table_name}")
        else:
            logging.info(f"No missing columns in {table_name}")
            
        return True
    
    except Exception as e:
        logging.error(f"Error fixing database schema: {e}")
        return False

def add_default_admin_user(db_path):
    """Add default admin user if no users exist."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logging.error("Users table does not exist")
            conn.close()
            return False
        
        # Check if users table has any records
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # Generate password hash for 'admin'
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash('admin')
            
            # Insert default admin user
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, active)
                VALUES (?, ?, ?, ?)
            """, ('admin', password_hash, 'admin', 1))
            
            conn.commit()
            logging.info("Added default admin user (username: admin, password: admin)")
        
        conn.close()
        return True
    
    except Exception as e:
        logging.error(f"Error adding default admin user: {e}")
        return False

def main():
    """Main function to fix database schema."""
    try:
        # Setup logging
        app_data_dir = setup_logging()
        logging.info("Starting database schema fix...")
        
        # Get database path
        db_path = get_database_path(app_data_dir)
        
        # Check if database directory exists
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logging.info(f"Created database directory: {db_dir}")
        
        # Get schema path
        schema_path = get_schema_path()
        if not schema_path:
            logging.error("Cannot proceed without schema file")
            return 1
        
        # Check if database exists
        if not os.path.exists(db_path):
            logging.warning(f"Database file does not exist: {db_path}")
            
            # Create database directory
            db_dir = os.path.dirname(db_path)
            os.makedirs(db_dir, exist_ok=True)
            
            # Create empty database
            conn = sqlite3.connect(db_path)
            conn.close()
            logging.info(f"Created empty database file: {db_path}")
            
            # Initialize with schema
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                
            conn = sqlite3.connect(db_path)
            conn.executescript(schema_sql)
            conn.commit()
            conn.close()
            
            logging.info("Initialized database with schema")
            
            # Add default admin user
            add_default_admin_user(db_path)
            
            print("Database created and initialized successfully")
            logging.info("Database created and initialized successfully")
            return 0
        
        # Check if it's better to recreate the database
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                logging.warning("Users table missing - recreating database")
                conn.close()
                return recreate_database(db_path, schema_path) and add_default_admin_user(db_path)
            
            # Check column count in users table
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            conn.close()
            
            # If too many columns are missing, better to recreate
            expected_schema = get_expected_schema(schema_path, "users")
            if expected_schema and len(columns) < len(expected_schema) / 2:
                logging.warning("Too many missing columns - recreating database")
                return recreate_database(db_path, schema_path) and add_default_admin_user(db_path)
        
        except Exception as e:
            logging.error(f"Error checking database integrity: {e}")
            # If we can't even check, better to recreate
            return recreate_database(db_path, schema_path) and add_default_admin_user(db_path)
        
        # Fix Users table schema
        current_users_schema = get_table_schema(db_path, "users")
        expected_users_schema = get_expected_schema(schema_path, "users")
        
        if expected_users_schema is None:
            logging.error("Failed to parse expected users schema")
            return 1
        
        # Check for employee_id column specifically
        if current_users_schema is None or 'employee_id' not in current_users_schema:
            logging.warning("employee_id column is missing from users table")
        
        # Fix schema
        if not fix_database_schema(db_path, "users", expected_users_schema, current_users_schema):
            logging.error("Failed to fix users table schema")
            return 1
        
        # Ensure default admin user exists
        add_default_admin_user(db_path)
        
        logging.info("Database schema fix completed successfully")
        print("Database schema fix completed successfully")
        print(f"Database path: {db_path}")
        return 0
    
    except Exception as e:
        logging.error(f"Error during database schema fix: {e}")
        print(f"Error during database schema fix: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
