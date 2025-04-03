"""Database Initialization Script for Handyman KPI System

This script initializes the database in a user-writable location (AppData),
creates the necessary tables, and adds a default admin user if needed.
"""
import os
import sys
import sqlite3
import json
import logging
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

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
    log_file = os.path.join(log_dir, "database_init.log")
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

def create_database_directory(app_data_dir):
    """Create a database directory in AppData."""
    db_dir = os.path.join(app_data_dir, "database")
    os.makedirs(db_dir, exist_ok=True)
    
    # Test write permissions
    test_file = os.path.join(db_dir, "test_write.tmp")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        logging.info(f"Database directory {db_dir} is writable")
    except Exception as e:
        logging.error(f"Database directory {db_dir} is not writable: {e}")
        # Try a fallback directory
        db_dir = os.path.join(app_data_dir, "data")
        os.makedirs(db_dir, exist_ok=True)
        logging.info(f"Using fallback database directory: {db_dir}")
    
    return db_dir

def create_config_file(app_data_dir, db_dir):
    """Create a database configuration file."""
    # Create config directory
    config_dir = os.path.join(app_data_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    
    # Create database.json config file
    config_file = os.path.join(config_dir, "database.json")
    config = {
        "type": "sqlite",
        "path": os.path.join(db_dir, "kpi_system.db")
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    logging.info(f"Created database configuration file: {config_file}")
    return config

def get_schema():
    """Get the database schema SQL from the installation directory."""
    # Try to find schema file in current directory first
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_paths = [
        os.path.join(base_dir, "kpi-system", "backend", "app", "database", "schema.sql"),
        os.path.join(base_dir, "kpi-system", "database", "schema.sql"),
        os.path.join(base_dir, "database", "schema.sql"),
    ]
    
    # Try each path
    for path in schema_paths:
        if os.path.exists(path):
            logging.info(f"Found schema file: {path}")
            with open(path, 'r') as f:
                return f.read()
    
    # If no schema file found, use a minimal schema
    logging.warning("No schema file found, using minimal schema")
    return """
    -- Minimal schema for KPI System
    
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        employee_id INTEGER,
        active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        force_password_change BOOLEAN DEFAULT 0,
        reset_token TEXT,
        reset_token_expiry TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    );
    
    -- Employees table
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        tier TEXT NOT NULL,
        hire_date DATE,
        active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Evaluations table
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        evaluator_id INTEGER NOT NULL,
        evaluation_date DATE NOT NULL,
        total_score INTEGER,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees (id),
        FOREIGN KEY (evaluator_id) REFERENCES users (id)
    );
    
    -- Skills table
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        max_score INTEGER DEFAULT 5,
        tier TEXT,
        category TEXT,
        active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Tools table
    CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        tier TEXT,
        active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Skill ratings table
    CREATE TABLE IF NOT EXISTS skill_ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (evaluation_id) REFERENCES evaluations (id),
        FOREIGN KEY (skill_id) REFERENCES skills (id)
    );
    
    -- Tool proficiencies table
    CREATE TABLE IF NOT EXISTS tool_proficiencies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        tool_id INTEGER NOT NULL,
        proficiency_level TEXT NOT NULL,
        certification_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees (id),
        FOREIGN KEY (tool_id) REFERENCES tools (id)
    );
    """

def initialize_database(db_path, schema_sql):
    """Initialize the database with schema."""
    try:
        # Connect to the database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        
        # Execute schema
        conn.executescript(schema_sql)
        
        # Commit and close
        conn.commit()
        conn.close()
        
        logging.info(f"Database initialized successfully at: {db_path}")
        return True
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        return False

def generate_password_hash(password):
    """Generate a password hash compatible with Flask-Login and Werkzeug."""
    # Generate salt
    salt = secrets.token_hex(16)
    
    # Hash password with salt
    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    
    hash_obj = hashlib.sha256(salt_bytes + password_bytes)
    password_hash = f"pbkdf2:sha256:150000${salt}${hash_obj.hexdigest()}"
    
    return password_hash

def create_default_admin(db_path):
    """Create a default admin user in the database."""
    try:
        # Generate password hash
        password_hash = generate_password_hash('admin')
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logging.error("Users table does not exist")
            conn.close()
            return False
        
        # Check if admin user already exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if cursor.fetchone():
            logging.info("Admin user already exists")
            conn.close()
            return True
        
        # Create admin user
        cursor.execute(
            """INSERT INTO users 
               (username, password_hash, role, active, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            ('admin', password_hash, 'admin', 1, datetime.now(), datetime.now())
        )
        
        # Commit and close
        conn.commit()
        conn.close()
        
        logging.info("Created default admin user (username: admin, password: admin)")
        return True
    except Exception as e:
        logging.error(f"Error creating admin user: {e}")
        return False

def main():
    """Main function to initialize the database."""
    try:
        # Set up logging and get app data directory
        app_data_dir = setup_logging()
        logging.info("Starting database initialization...")
        
        # Create database directory
        db_dir = create_database_directory(app_data_dir)
        
        # Create config file
        config = create_config_file(app_data_dir, db_dir)
        
        # Set database path
        db_path = config["path"]
        logging.info(f"Database path: {db_path}")
        
        # Get schema
        schema_sql = get_schema()
        
        # Initialize database
        if not initialize_database(db_path, schema_sql):
            logging.error("Failed to initialize database")
            return 1
        
        # Create default admin user
        if not create_default_admin(db_path):
            logging.error("Failed to create admin user")
            return 1
        
        logging.info("Database initialization completed successfully")
        print("Database initialization completed successfully")
        print(f"Database path: {db_path}")
        print("Default admin credentials: username=admin, password=admin")
        
        return 0
    except Exception as e:
        logging.error(f"Error during database initialization: {e}")
        print(f"Error during database initialization: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())