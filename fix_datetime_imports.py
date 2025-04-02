# Fix Datetime Imports Script

import os
import sys
import logging
import re
from pathlib import Path
import shutil

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
    log_file = os.path.join(log_dir, "datetime_fix.log")
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

def find_install_directory():
    """Find the KPI System installation directory."""
    possible_paths = [
        r"C:\Program Files\Handyman KPI System",
        r"C:\Handyman KPI System",
        r"C:\Users\dtest\KPI Project"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            # Check if it contains the backend directory
            backend_path = os.path.join(path, "kpi-system", "backend")
            if os.path.exists(backend_path):
                logging.info(f"Found KPI System at: {path}")
                return path
    
    # If not found, try to find via current directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(script_dir, "kpi-system")):
        return script_dir
    
    logging.warning("Could not find KPI System installation directory")
    return None

def find_user_model(install_dir):
    """Find the User model file."""
    user_model_path = os.path.join(install_dir, "kpi-system", "backend", "app", "models", "user.py")
    
    if os.path.exists(user_model_path):
        logging.info(f"Found User model at: {user_model_path}")
        return user_model_path
    
    # Try to find by searching
    for root, dirs, files in os.walk(install_dir):
        for file in files:
            if file == "user.py":
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    if "class User" in content and "def generate_reset_token" in content:
                        logging.info(f"Found User model at: {file_path}")
                        return file_path
    
    logging.error("Could not find User model")
    return None

def fix_datetime_imports(user_model_path):
    """Fix the datetime imports and usage in the User model."""
    try:
        # Read the file
        with open(user_model_path, 'r') as f:
            content = f.read()
        
        # Check how datetime is imported
        import_match = re.search(r'from\s+datetime\s+import\s+(.+)', content)
        if import_match:
            # There's already a 'from datetime import ...' statement
            imports = import_match.group(1)
            if 'timedelta' not in imports:
                # Add timedelta to the imports
                new_imports = imports.strip()
                if new_imports.endswith(','):
                    new_imports += ' timedelta'
                else:
                    new_imports += ', timedelta'
                
                content = content.replace(import_match.group(0), f'from datetime import {new_imports}')
                logging.info("Added timedelta to existing datetime imports")
        else:
            # Check if there's a 'import datetime' statement
            if 'import datetime' in content:
                # Replace datetime.timedelta with timedelta
                content = content.replace('datetime.timedelta', 'timedelta')
                
                # Add the correct import
                content = content.replace('import datetime', 'from datetime import datetime, timedelta')
                logging.info("Replaced 'import datetime' with correct imports")
            else:
                # Add the import if it doesn't exist
                content = 'from datetime import datetime, timedelta\n' + content
                logging.info("Added datetime imports")
        
        # Fix usages of datetime.timedelta
        content = content.replace('datetime.timedelta', 'timedelta')
        
        # Create a fixed file in the current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        fixed_file_path = os.path.join(script_dir, "fixed_user.py")
        
        with open(fixed_file_path, 'w') as f:
            f.write(content)
        
        logging.info(f"Created fixed file at: {fixed_file_path}")
        
        # Generate instructions for copying
        user_model_dir = os.path.dirname(user_model_path)
        logging.info(f"To apply the fix, copy {fixed_file_path} to {user_model_path}")
        print(f"To apply the fix, copy {fixed_file_path} to {user_model_path}")
        
        return True
    
    except Exception as e:
        logging.error(f"Error fixing datetime imports: {e}")
        return False

def main():
    """Main function to fix datetime imports."""
    try:
        # Setup logging
        app_data_dir = setup_logging()
        logging.info("Starting datetime imports fix...")
        
        # Find installation directory
        install_dir = find_install_directory()
        if not install_dir:
            logging.error("Could not find KPI System installation directory")
            return 1
        
        # Find User model
        user_model_path = find_user_model(install_dir)
        if not user_model_path:
            logging.error("Could not find User model")
            return 1
        
        # Fix datetime imports
        if not fix_datetime_imports(user_model_path):
            logging.error("Failed to fix datetime imports")
            return 1
        
        # If the installation is in a user-writable directory, try to apply the fix directly
        if not user_model_path.startswith(r"C:\Program Files"):
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                fixed_file_path = os.path.join(script_dir, "fixed_user.py")
                
                # Create a backup first
                backup_path = f"{user_model_path}.bak"
                shutil.copy2(user_model_path, backup_path)
                logging.info(f"Created backup at: {backup_path}")
                
                # Copy the fixed file to the destination
                shutil.copy2(fixed_file_path, user_model_path)
                logging.info(f"Applied fix to: {user_model_path}")
                print(f"Applied fix to: {user_model_path}")
            except Exception as e:
                logging.error(f"Error applying fix: {e}")
                print(f"Error applying fix: {e}")
                print("Fix file has been created, but could not be automatically applied.")
                print(f"You'll need to manually copy {fixed_file_path} to {user_model_path}")
        
        logging.info("Datetime imports fix completed successfully")
        print("Datetime imports fix completed successfully")
        return 0
    
    except Exception as e:
        logging.error(f"Error during datetime imports fix: {e}")
        print(f"Error during datetime imports fix: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
