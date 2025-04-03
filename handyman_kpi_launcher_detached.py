"""Detached Launcher for Handyman KPI System

This launcher starts the application as a detached process with no console window.
"""

import os
import sys
import json
import time
import logging
import subprocess
import ctypes
from pathlib import Path

# Windows process creation flags
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008

def setup_logging():
    """Configure logging to file."""
    app_data_dir = os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
        "Handyman KPI System"
    )
    
    log_dir = os.path.join(app_data_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "launcher.log")
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return app_data_dir

def find_flask_app():
    """Find the path to the Flask application."""
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in the project root or in a subdirectory
    if os.path.exists(os.path.join(script_dir, "kpi-system")):
        backend_path = os.path.join(script_dir, "kpi-system", "backend")
    elif os.path.basename(script_dir) == "kpi-system":
        backend_path = os.path.join(script_dir, "backend")
    else:
        # Try one level up
        parent_dir = os.path.dirname(script_dir)
        if os.path.exists(os.path.join(parent_dir, "kpi-system")):
            backend_path = os.path.join(parent_dir, "kpi-system", "backend")
        else:
            # Last resort: check if we're in the backend directory
            if os.path.basename(script_dir) == "backend":
                backend_path = script_dir
            else:
                # Try finding the installation directory from registry
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Handyman KPI System") as key:
                        install_dir = winreg.QueryValueEx(key, "InstallPath")[0]
                        backend_path = os.path.join(install_dir, "kpi-system", "backend")
                except:
                    logging.error("Could not find backend directory")
                    backend_path = None
    
    if backend_path and os.path.exists(backend_path):
        logging.info(f"Found backend directory: {backend_path}")
        run_py = os.path.join(backend_path, "run.py")
        if os.path.exists(run_py):
            return run_py
    
    logging.error("Could not locate run.py")
    return None

def check_python_installation():
    """Check Python installation and environment."""
    python_exe = sys.executable
    logging.info(f"Python executable: {python_exe}")
    
    # Check for pythonw.exe
    if python_exe.endswith("python.exe"):
        pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
        if os.path.exists(pythonw_exe):
            logging.info(f"Using pythonw.exe: {pythonw_exe}")
            return pythonw_exe
    
    return python_exe

def get_database_path(app_data_dir):
    """Get the database path."""
    config_file = os.path.join(app_data_dir, "config", "database.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'path' in config:
                    db_path = config['path']
                    logging.info(f"Database path from config: {db_path}")
                    return db_path
        except Exception as e:
            logging.error(f"Error reading config file: {e}")
    
    # Default path
    db_path = os.path.join(app_data_dir, "database", "kpi_system.db")
    logging.info(f"Using default database path: {db_path}")
    return db_path

def initialize_database_if_needed(app_data_dir, python_exe):
    """Initialize database if it doesn't exist."""
    db_path = get_database_path(app_data_dir)
    
    if not os.path.exists(db_path):
        logging.warning(f"Database file not found: {db_path}")
        
        # Find initialize_database.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        init_db_script = os.path.join(script_dir, "initialize_database.py")
        
        if not os.path.exists(init_db_script):
            # Try one level up
            init_db_script = os.path.join(os.path.dirname(script_dir), "initialize_database.py")
        
        if os.path.exists(init_db_script):
            logging.info(f"Running database initialization: {init_db_script}")
            try:
                subprocess.run([python_exe, init_db_script], check=True)
                logging.info("Database initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing database: {e}")
                return False
        else:
            logging.error("Could not find initialize_database.py")
            return False
    
    return True

def launch_app(flask_app_path, python_exe):
    """Launch the Flask application as a detached process."""
    try:
        # Use subprocess.Popen to create a detached process
        process = subprocess.Popen(
            [python_exe, flask_app_path],
            creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
            close_fds=True,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment to see if the process crashes immediately
        time.sleep(1)
        if process.poll() is not None:
            logging.error(f"Application failed to start: Exit code {process.returncode}")
            stderr = process.stderr.read().decode('utf-8', errors='ignore')
            logging.error(f"Error output: {stderr}")
            return False
        
        logging.info(f"Started application with PID: {process.pid}")
        return True
    
    except Exception as e:
        logging.error(f"Error launching application: {e}")
        return False

def create_browser_shortcut():
    """Create a desktop shortcut to access the application via web browser."""
    try:
        # Only create if we have access to the Desktop folder
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop_path):
            return
        
        shortcut_path = os.path.join(desktop_path, "Handyman KPI System (Browser).url")
        with open(shortcut_path, 'w') as f:
            f.write("[InternetShortcut]\n")
            f.write("URL=http://localhost:5000\n")
            f.write("IconIndex=0\n")
        
        logging.info(f"Created browser shortcut: {shortcut_path}")
    except Exception as e:
        logging.error(f"Error creating browser shortcut: {e}")

def main():
    """Main function to start the KPI System."""
    try:
        # Configure logging
        app_data_dir = setup_logging()
        logging.info("Starting Handyman KPI System launcher...")
        
        # Find the Flask application
        flask_app_path = find_flask_app()
        if not flask_app_path:
            logging.error("Cannot find Flask application")
            return 1
        
        # Check Python installation
        python_exe = check_python_installation()
        
        # Initialize database if needed
        if not initialize_database_if_needed(app_data_dir, python_exe):
            logging.warning("Continuing despite database initialization issues")
        
        # Launch the application
        if not launch_app(flask_app_path, python_exe):
            logging.error("Failed to launch application")
            return 1
        
        # Create browser shortcut
        create_browser_shortcut()
        
        logging.info("Application launched successfully")
        return 0
    
    except Exception as e:
        logging.error(f"Unhandled error in launcher: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())