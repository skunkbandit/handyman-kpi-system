#!/usr/bin/env python3
"""
Script to apply the fixed run.py file to the installed KPI System.
"""

import os
import sys
import shutil
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='apply_fixed_run.log',
    filemode='w'
)

# Add console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def find_installation_path():
    """Find the KPI System installation path"""
    # Common installation paths
    possible_paths = [
        r"C:\Program Files\Handyman KPI System",
        r"C:\Program Files (x86)\Handyman KPI System",
        os.path.join(os.environ.get('LOCALAPPDATA', ''), "Programs", "Handyman KPI System")
    ]
    
    # Check each path
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return path
    
    return None

def verify_app_directory(installation_path):
    """Verify that the app directory exists and has the required files"""
    app_path = os.path.join(installation_path, "kpi-system", "backend", "app")
    
    if not os.path.exists(app_path):
        logging.error(f"App directory does not exist: {app_path}")
        return False
    
    init_file = os.path.join(app_path, "__init__.py")
    if not os.path.exists(init_file):
        logging.error(f"__init__.py not found in app directory: {init_file}")
        return False
    
    # Verify we have the create_app function in the __init__.py file
    with open(init_file, 'r') as f:
        content = f.read()
        if "def create_app" not in content:
            logging.error(f"create_app function not found in {init_file}")
            return False
    
    logging.info(f"App directory verified: {app_path}")
    logging.info(f"__init__.py contains create_app function: {init_file}")
    return True

def backup_original_file(file_path):
    """Create a backup of the original file"""
    timestamp = time.strftime("%Y%m%d%H%M%S")
    backup_path = f"{file_path}.bak.{timestamp}"
    
    try:
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            logging.info(f"Backed up original file to: {backup_path}")
            return backup_path
        else:
            logging.warning(f"Original file not found: {file_path}")
            return None
    except Exception as e:
        logging.error(f"Failed to backup file: {e}")
        return None

def apply_fixed_run_py(installation_path, fixed_run_path):
    """Apply the fixed run.py file to the installation"""
    if not installation_path:
        logging.error("Installation path not found")
        return False
    
    if not os.path.exists(fixed_run_path):
        logging.error(f"Fixed run.py not found: {fixed_run_path}")
        return False
    
    # Target path for run.py
    run_py_path = os.path.join(installation_path, "kpi-system", "backend", "run.py")
    
    # Backup original file
    backup_path = backup_original_file(run_py_path)
    
    # Copy the fixed file
    try:
        shutil.copy2(fixed_run_path, run_py_path)
        logging.info(f"Successfully applied fixed run.py to: {run_py_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to apply fixed run.py: {e}")
        if backup_path and os.path.exists(backup_path):
            try:
                # Restore from backup if copy failed
                shutil.copy2(backup_path, run_py_path)
                logging.info(f"Restored original file from backup")
            except Exception as restore_error:
                logging.error(f"Failed to restore original file: {restore_error}")
        return False

def main():
    """Main function to apply the fixed run.py"""
    logging.info("Starting to apply fixed run.py...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the fixed run.py
    fixed_run_path = os.path.join(script_dir, "fixed_run.py")
    
    # Find installation path
    logging.info("Looking for KPI System installation...")
    installation_path = find_installation_path()
    
    if not installation_path:
        logging.error("KPI System installation not found")
        print("\nERROR: Could not find KPI System installation.")
        return 1
    
    logging.info(f"Found installation at: {installation_path}")
    
    # Verify app directory exists and has required files
    if not verify_app_directory(installation_path):
        logging.error("App directory verification failed")
        print("\nERROR: App directory verification failed.")
        return 1
    
    # Apply the fixed run.py
    if apply_fixed_run_py(installation_path, fixed_run_path):
        logging.info("Successfully applied fixed run.py")
        print("\nSUCCESS: Applied fixed run.py to installation.")
        print(f"Installation path: {installation_path}")
        return 0
    else:
        logging.error("Failed to apply fixed run.py")
        print("\nERROR: Failed to apply fixed run.py.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
