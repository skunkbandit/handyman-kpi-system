import os
import sys
import webbrowser
import time
import json
import sqlite3
import threading

# Constants
APP_NAME = "Handyman KPI System"
APP_PORT = 5000
APP_HOST = "127.0.0.1"

# Use AppData directory for user-specific data instead of Program Files
APP_DATA_DIR = os.path.join(os.environ['APPDATA'], APP_NAME)
DB_PATH = os.path.join(APP_DATA_DIR, "database.db")
CONFIG_PATH = os.path.join(APP_DATA_DIR, "config.json")

# Default configuration
DEFAULT_CONFIG = {
    "database": {
        "type": "sqlite",
        "file": DB_PATH
    },
    "server": {
        "host": APP_HOST,
        "port": APP_PORT
    },
    "first_run": True
}

# Ensure config exists
def ensure_config():
    if not os.path.exists(APP_DATA_DIR):
        try:
            os.makedirs(APP_DATA_DIR, exist_ok=True)
            print(f"Created application data directory: {APP_DATA_DIR}")
        except Exception as e:
            print(f"Error creating application data directory: {e}")
            raise
    
    if not os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            print(f"Created default configuration file: {CONFIG_PATH}")
            return DEFAULT_CONFIG
        except Exception as e:
            print(f"Error creating configuration file: {e}")
            raise
    else:
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading configuration file: {e}")
            print("Attempting to create new configuration file...")
            with open(CONFIG_PATH, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG

# Console-based setup instead of GUI-based wizard
def console_setup_wizard():
    """
    Display a simple console-based setup wizard for first-time users.
    """
    config = ensure_config()
    
    print("=" * 70)
    print(f"Welcome to {APP_NAME}!")
    print("=" * 70)
    print("This wizard will help you set up your system for first use.")
    print()
    
    print("Database Configuration:")
    print("Using SQLite (Recommended for single-user or testing)")
    print(f"Database location: {DB_PATH}")
    print()
    
    print("Admin Account Setup:")
    admin_username = input("Enter admin username [admin]: ").strip() or "admin"
    admin_password = input("Enter admin password [admin]: ").strip() or "admin"
    admin_email = input("Enter admin email [admin@example.com]: ").strip() or "admin@example.com"
    
    print()
    print("Saving configuration...")
    
    # Update configuration
    config["first_run"] = False
    
    # Write config file
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
        
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
    # Initialize SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create admin user
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, email, role)
    VALUES (?, ?, ?, ?)
    ''', (admin_username, admin_password, admin_email, 'admin'))
    
    conn.commit()
    conn.close()
    
    print("Initial setup completed successfully!")
    print("Press Enter to start the application...")
    input()
    
    return config

# Set up proper Python path
def setup_python_path():
    # Get current script directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the application directory to Python path if not already there
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    # Also add the parent directory to support imports like 'from app import X'
    parent_dir = os.path.dirname(app_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Print Python path for debugging
    print("Python path:")
    for p in sys.path:
        print(f"  {p}")

# Main function
def main():
    print(f"Starting {APP_NAME}...")
    print(f"Application data directory: {APP_DATA_DIR}")
    
    try:
        # Load or create configuration
        config = ensure_config()
        
        # Show setup wizard if this is the first run
        if config.get("first_run", True):
            config = console_setup_wizard()
        
        # Ensure database directory exists
        db_dir = os.path.dirname(DB_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Set up Python path properly
        setup_python_path()
        
        # Print server information
        print(f"Starting server on {config['server']['host']}:{config['server']['port']}")
        
        # Import the app with more detailed error handling
        try:
            # Import the Flask app
            from app import app
            print("Successfully imported Flask app")
        except ImportError as e:
            print(f"Error importing app module: {e}")
            print("Current sys.path:")
            for p in sys.path:
                print(f"  {p}")
            print("Attempting alternative import...")
            try:
                # Try importing from wsgi file
                import wsgi
                from app import app
                print("Successfully imported Flask app via wsgi module")
            except ImportError as e:
                print(f"Alternative import also failed: {e}")
                
                # One more attempt - try to create the app manually
                print("Attempting to create app instance directly...")
                try:
                    from app import create_app
                    app = create_app()
                    print("Successfully created app instance directly")
                except ImportError as e:
                    print(f"Direct app creation also failed: {e}")
                    raise
        
        # Update app configuration to use the correct database path
        app.config['DATABASE'] = DB_PATH
        
        # Give the server a moment to start before opening browser
        def open_browser():
            time.sleep(2)  # Wait for server to start
            webbrowser.open(f"http://{config['server']['host']}:{config['server']['port']}")
            print(f"Opened browser to http://{config['server']['host']}:{config['server']['port']}")
        
        # Start browser in a separate thread
        threading.Thread(target=open_browser).start()
        
        # Serve the application - this will block until the server is stopped
        try:
            from waitress import serve
            print(f"Starting waitress server on {config['server']['host']}:{config['server']['port']}")
            serve(app, host=config['server']['host'], port=config['server']['port'])
        except ImportError:
            print(f"Waitress not available. Starting Flask development server on {config['server']['host']}:{config['server']['port']}")
            app.run(host=config['server']['host'], port=config['server']['port'])
            
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"ERROR STARTING APPLICATION: {e}")
        print("=" * 50)
        
        # Get more detailed error information
        import traceback
        traceback.print_exc()
        
        print("\nPlease check the following:")
        print("1. Make sure all required Python packages are installed")
        print("2. Check that no other application is using port", APP_PORT)
        print("3. Verify the database configuration is correct")
        print(f"4. Ensure you have write permission to {APP_DATA_DIR}")
        print("\nApplication could not start due to the errors above.")
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()