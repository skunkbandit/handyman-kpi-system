# Fix Admin User Script

import os
import sys
import sqlite3
import logging
import hashlib
import secrets
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
    log_file = os.path.join(log_dir, "admin_user_fix.log")
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

def check_admin_user(db_path):
    """Check if admin user exists and is valid."""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logging.error("Users table does not exist")
            conn.close()
            return False
        
        # Check if admin user exists
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            logging.warning("Admin user does not exist")
            conn.close()
            return False
        
        # Try to log in with the admin user
        # This is to check if the password hash is valid
        logging.info("Admin user exists, checking password hash format...")
        
        # Check password hash format
        password_hash = admin_user[2]
        if not password_hash:
            logging.warning("Admin user has no password hash")
            conn.close()
            return False
        
        # For Flask-generated hash, it should start with one of these
        if password_hash.startswith(('pbkdf2:sha256', 'sha256$', '$2b$')):
            logging.info("Admin user has a valid-looking password hash format")
            conn.close()
            return True
        
        logging.warning("Admin user has an unusual password hash format")
        conn.close()
        return False
    
    except Exception as e:
        logging.error(f"Error checking admin user: {e}")
        return False

def fix_admin_user(db_path):
    """Fix admin user by recreating it with the correct credentials."""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logging.error("Users table does not exist")
            conn.close()
            return False
        
        # Delete existing admin user
        cursor.execute("DELETE FROM users WHERE username = 'admin'")
        
        # Create a new admin user with a proper password hash
        # Try to import werkzeug to generate password hash
        try:
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash('admin')
            logging.info("Generated password hash using werkzeug")
        except ImportError:
            # Fall back to a simple hash if werkzeug is not available
            salt = secrets.token_hex(8)
            password = 'admin'
            password_bytes = password.encode('utf-8')
            salt_bytes = salt.encode('utf-8')
            
            # Use PBKDF2 with SHA256
            password_hash = 'pbkdf2:sha256:150000$' + salt + '$' + hashlib.pbkdf2_hmac(
                'sha256',
                password_bytes,
                salt_bytes,
                150000,
                dklen=32
            ).hex()
            logging.info("Generated password hash using hashlib")
        
        # Determine the schema of the users table
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'salt' in column_names:
            # If the table has a salt column
            salt = secrets.token_hex(8)
            query = """
                INSERT INTO users (username, password_hash, salt, role, active)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query, ('admin', password_hash, salt, 'admin', 1))
        else:
            # If no salt column
            query = """
                INSERT INTO users (username, password_hash, role, active)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, ('admin', password_hash, 'admin', 1))
        
        # Check if employee_id column exists and is required
        is_employee_id_required = False
        for column in columns:
            if column[1] == 'employee_id' and column[3] == 1:  # notnull constraint
                is_employee_id_required = True
                break
        
        if is_employee_id_required:
            # We need to add an employee for the admin user
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
            if cursor.fetchone():
                # Check if any employees exist
                cursor.execute("SELECT employee_id FROM employees LIMIT 1")
                employee = cursor.fetchone()
                
                if employee:
                    # Link admin user to the first employee
                    cursor.execute("UPDATE users SET employee_id = ? WHERE username = 'admin'", (employee[0],))
                else:
                    # Create a new employee
                    cursor.execute("""
                        INSERT INTO employees (name, tier, active)
                        VALUES (?, ?, ?)
                    """, ('Admin User', 'Lead Craftsman', 1))
                    
                    # Get the new employee ID
                    employee_id = cursor.lastrowid
                    
                    # Link admin user to the new employee
                    cursor.execute("UPDATE users SET employee_id = ? WHERE username = 'admin'", (employee_id,))
        
        # Commit and close
        conn.commit()
        conn.close()
        
        logging.info("Admin user fixed successfully")
        return True
    
    except Exception as e:
        logging.error(f"Error fixing admin user: {e}")
        return False

def main():
    """Main function to fix admin user."""
    try:
        # Setup logging
        app_data_dir = setup_logging()
        logging.info("Starting admin user fix...")
        
        # Get database path
        db_path = get_database_path(app_data_dir)
        if not os.path.exists(db_path):
            logging.error(f"Database file not found: {db_path}")
            return 1
        
        # Check admin user
        if check_admin_user(db_path):
            logging.info("Admin user is valid")
            print("Admin user is valid")
            return 0
        
        # Fix admin user
        if not fix_admin_user(db_path):
            logging.error("Failed to fix admin user")
            return 1
        
        logging.info("Admin user fix completed successfully")
        print("Admin user fix completed successfully")
        print("You can now log in with username: admin, password: admin")
        return 0
    
    except Exception as e:
        logging.error(f"Error during admin user fix: {e}")
        print(f"Error during admin user fix: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
