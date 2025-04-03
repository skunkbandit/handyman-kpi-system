#!/usr/bin/env python3
"""
Fix script for the KPI System application.

This script fixes the 'module app has no attribute create_app' error by
ensuring proper structure and imports.
"""

import os
import sys
import shutil
import logging
from pathlib import Path

def setup_logging():
    """Configure logging to both file and console"""
    try:
        log_dir = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / "Handyman KPI System" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "app_import_fix.log"
        
        # Set up file handler
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    except Exception as e:
        print(f"Error setting up logging: {e}")
        # Fallback to basic console logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s'
        )
        return logging.getLogger()

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

def fix_run_py(installation_path):
    """Fix the run.py file in the installation"""
    if not installation_path:
        logger.error("Installation path not found")
        return False
    
    # Paths to relevant files
    backend_dir = os.path.join(installation_path, "kpi-system", "backend")
    run_py_path = os.path.join(backend_dir, "run.py")
    app_dir = os.path.join(backend_dir, "app")
    init_py_path = os.path.join(app_dir, "__init__.py")
    
    # Check if required directories and files exist
    if not os.path.exists(backend_dir):
        logger.error(f"Backend directory not found: {backend_dir}")
        return False
        
    if not os.path.exists(app_dir):
        logger.error(f"App directory not found: {app_dir}")
        return False
    
    if not os.path.exists(init_py_path):
        logger.error(f"app/__init__.py not found: {init_py_path}")
        return False
    
    # Create backup of original run.py if it exists
    if os.path.exists(run_py_path):
        backup_path = run_py_path + ".bak.original"
        try:
            shutil.copy2(run_py_path, backup_path)
            logger.info(f"Created backup of original run.py: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup of run.py: {e}")
            return False
    
    # Create the new run.py with improved import handling
    try:
        with open(run_py_path, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
Run script for the KPI System application - Fixed version

This script sets up and runs the Flask development server with enhanced
module import handling to resolve the 'module app has no attribute create_app' error.
"""

import os
import sys
import importlib.util
import logging
from pathlib import Path

# Set up logging
try:
    app_data_dir = os.environ.get('KPI_SYSTEM_APP_DATA', os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
        "Handyman KPI System"
    ))
    logs_dir = os.path.join(app_data_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=os.path.join(logs_dir, 'backend.log'),
        filemode='a'
    )
except Exception as e:
    # Fallback logging to stdout if file logging fails
    print(f"Warning: Could not set up file logging: {e}")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Log execution environment for debugging
logging.info('=' * 80)
logging.info('Starting backend application - Fixed runner')
logging.info(f'Current working directory: {os.getcwd()}')
logging.info(f'Python path: {sys.executable}')
logging.info('Python module search paths:')
for path in sys.path:
    logging.info(f'  {path}')

try:
    # Ensure important directories are in the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = current_dir
    app_dir = os.path.join(backend_dir, "app")
    parent_dir = os.path.dirname(backend_dir)
    
    # Make sure all important dirs are in path
    for path in [backend_dir, app_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
            logging.info(f'Added directory to path: {path}')
    
    # Direct import of the create_app function using spec
    try:
        init_path = os.path.join(app_dir, "__init__.py")
        if os.path.exists(init_path):
            logging.info(f"Found app/__init__.py at {init_path}")
            
            # Load the module manually
            spec = importlib.util.spec_from_file_location("app", init_path)
            app_module = importlib.util.module_from_spec(spec)
            sys.modules["app"] = app_module
            spec.loader.exec_module(app_module)
            
            # Get create_app function directly
            if hasattr(app_module, "create_app"):
                create_app = app_module.create_app
                logging.info("Successfully loaded create_app function using importlib")
            else:
                logging.error("The app module does not have a create_app function")
                raise ImportError("No create_app function found in app/__init__.py")
        else:
            logging.error(f"app/__init__.py not found at {init_path}")
            raise FileNotFoundError(f"Cannot find {init_path}")
            
    except Exception as e:
        logging.error(f"Error using direct import approach: {e}")
        
        # Fallback to standard import approach
        try:
            logging.info("Trying standard import approach")
            from app import create_app
            logging.info("Successfully imported create_app through standard import")
        except ImportError as e2:
            logging.error(f"Standard import approach failed: {e2}")
            
            # Last resort: try to dynamically fix the app's __init__.py
            try:
                logging.info("Attempting last resort fix")
                # Import the module directly as a backup
                import app
                
                # Check if the module itself has the attribute
                if hasattr(app, "create_app"):
                    create_app = app.create_app
                    logging.info("Successfully retrieved create_app from app module")
                else:
                    logging.error("app module loaded but has no create_app attribute")
                    
                    # Look for functions that might be the app factory
                    factory_candidates = [attr for attr in dir(app) 
                                        if callable(getattr(app, attr)) and attr.endswith("_app")]
                    
                    if factory_candidates:
                        logging.info(f"Found potential app factory candidates: {factory_candidates}")
                        create_app = getattr(app, factory_candidates[0])
                        logging.info(f"Using {factory_candidates[0]} as create_app")
                    else:
                        logging.error("No suitable app factory function found")
                        raise ImportError("No viable create_app function found")
            except Exception as e3:
                logging.error(f"Last resort fix failed: {e3}")
                raise e3
    
    # Create the application instance
    app = create_app()
    logging.info('Application instance created successfully')

    if __name__ == '__main__':
        # Get host and port from environment variables with defaults
        host = os.environ.get('FLASK_HOST', '127.0.0.1')
        port = int(os.environ.get('FLASK_PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        
        logging.info(f'Starting Flask server on {host}:{port} (debug: {debug})')
        
        # Run the application
        app.run(host=host, port=port, debug=debug)
        
except Exception as e:
    logging.exception(f'Error starting application: {e}')
    # Re-raise to ensure the error is visible
    raise
''')
        logger.info(f"Created new run.py with improved import handling at: {run_py_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create new run.py: {e}")
        return False

def create_fix_launcher_script(installation_path):
    """Create a batch script to fix the application in-place"""
    fix_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fix_app_import.bat")
    
    try:
        with open(fix_script_path, 'w') as f:
            f.write(f'''@echo off
echo ===============================================================
echo Handyman KPI System - App Import Fix
echo ===============================================================
echo.

set INSTALL_DIR="{installation_path}"

echo Installation directory: %INSTALL_DIR%
echo.

if not exist "%INSTALL_DIR%" (
    echo ERROR: Installation directory not found.
    echo Please make sure the KPI System is installed.
    pause
    exit /b 1
)

echo Checking for required directories...
if not exist "%INSTALL_DIR%\\kpi-system\\backend" (
    echo ERROR: Backend directory not found.
    pause
    exit /b 1
)

if not exist "%INSTALL_DIR%\\kpi-system\\backend\\app" (
    echo ERROR: App directory not found.
    pause
    exit /b 1
)

echo Backing up original run.py...
if exist "%INSTALL_DIR%\\kpi-system\\backend\\run.py" (
    copy /Y "%INSTALL_DIR%\\kpi-system\\backend\\run.py" "%INSTALL_DIR%\\kpi-system\\backend\\run.py.bak"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to backup run.py.
        echo You may need to run this script as administrator.
        pause
        exit /b 1
    )
    echo Backup created: %INSTALL_DIR%\\kpi-system\\backend\\run.py.bak
) else (
    echo WARNING: Original run.py not found.
)

echo Installing fixed run.py...
copy /Y "{os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixed_run.py")}" "%INSTALL_DIR%\\kpi-system\\backend\\run.py"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install fixed run.py.
    echo You may need to run this script as administrator.
    pause
    exit /b 1
)

echo.
echo ===============================================================
echo Fix applied successfully!
echo The application should now start correctly.
echo ===============================================================
echo.

echo Press any key to launch the application...
pause > nul

start "" "%INSTALL_DIR%\\handyman_kpi_launcher_detached.py"

echo.
echo Application started. Press any key to exit...
pause > nul
''')
        logger.info(f"Created fix launcher script at: {fix_script_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create fix launcher script: {e}")
        return False

def create_fixed_run_py_file():
    """Create a standalone fixed run.py file to be copied by the fix script"""
    fixed_run_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixed_run.py")
    
    try:
        with open(fixed_run_py_path, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
Run script for the KPI System application - Fixed version

This script sets up and runs the Flask development server with enhanced
module import handling to resolve the 'module app has no attribute create_app' error.
"""

import os
import sys
import importlib.util
import logging
from pathlib import Path

# Set up logging
try:
    app_data_dir = os.environ.get('KPI_SYSTEM_APP_DATA', os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
        "Handyman KPI System"
    ))
    logs_dir = os.path.join(app_data_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=os.path.join(logs_dir, 'backend.log'),
        filemode='a'
    )
except Exception as e:
    # Fallback logging to stdout if file logging fails
    print(f"Warning: Could not set up file logging: {e}")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Log execution environment for debugging
logging.info('=' * 80)
logging.info('Starting backend application - Fixed runner')
logging.info(f'Current working directory: {os.getcwd()}')
logging.info(f'Python path: {sys.executable}')
logging.info('Python module search paths:')
for path in sys.path:
    logging.info(f'  {path}')

try:
    # Ensure important directories are in the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = current_dir
    app_dir = os.path.join(backend_dir, "app")
    parent_dir = os.path.dirname(backend_dir)
    
    # Make sure all important dirs are in path
    for path in [backend_dir, app_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
            logging.info(f'Added directory to path: {path}')
    
    # Direct import of the create_app function using spec
    try:
        init_path = os.path.join(app_dir, "__init__.py")
        if os.path.exists(init_path):
            logging.info(f"Found app/__init__.py at {init_path}")
            
            # Load the module manually
            spec = importlib.util.spec_from_file_location("app", init_path)
            app_module = importlib.util.module_from_spec(spec)
            sys.modules["app"] = app_module
            spec.loader.exec_module(app_module)
            
            # Get create_app function directly
            if hasattr(app_module, "create_app"):
                create_app = app_module.create_app
                logging.info("Successfully loaded create_app function using importlib")
            else:
                logging.error("The app module does not have a create_app function")
                raise ImportError("No create_app function found in app/__init__.py")
        else:
            logging.error(f"app/__init__.py not found at {init_path}")
            raise FileNotFoundError(f"Cannot find {init_path}")
            
    except Exception as e:
        logging.error(f"Error using direct import approach: {e}")
        
        # Fallback to standard import approach
        try:
            logging.info("Trying standard import approach")
            from app import create_app
            logging.info("Successfully imported create_app through standard import")
        except ImportError as e2:
            logging.error(f"Standard import approach failed: {e2}")
            
            # Last resort: try to dynamically fix the app's __init__.py
            try:
                logging.info("Attempting last resort fix")
                # Import the module directly as a backup
                import app
                
                # Check if the module itself has the attribute
                if hasattr(app, "create_app"):
                    create_app = app.create_app
                    logging.info("Successfully retrieved create_app from app module")
                else:
                    logging.error("app module loaded but has no create_app attribute")
                    
                    # Look for functions that might be the app factory
                    factory_candidates = [attr for attr in dir(app) 
                                        if callable(getattr(app, attr)) and attr.endswith("_app")]
                    
                    if factory_candidates:
                        logging.info(f"Found potential app factory candidates: {factory_candidates}")
                        create_app = getattr(app, factory_candidates[0])
                        logging.info(f"Using {factory_candidates[0]} as create_app")
                    else:
                        logging.error("No suitable app factory function found")
                        raise ImportError("No viable create_app function found")
            except Exception as e3:
                logging.error(f"Last resort fix failed: {e3}")
                raise e3
    
    # Create the application instance
    app = create_app()
    logging.info('Application instance created successfully')

    if __name__ == '__main__':
        # Get host and port from environment variables with defaults
        host = os.environ.get('FLASK_HOST', '127.0.0.1')
        port = int(os.environ.get('FLASK_PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        
        logging.info(f'Starting Flask server on {host}:{port} (debug: {debug})')
        
        # Run the application
        app.run(host=host, port=port, debug=debug)
        
except Exception as e:
    logging.exception(f'Error starting application: {e}')
    # Re-raise to ensure the error is visible
    raise
''')
        logger.info(f"Created fixed run.py file at: {fixed_run_py_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create fixed run.py file: {e}")
        return False

def main():
    """Main function to run the fix script"""
    logger.info("Starting app import fix script")
    
    # Find the installation path
    logger.info("Looking for KPI System installation")
    installation_path = find_installation_path()
    
    if installation_path:
        logger.info(f"Found installation at: {installation_path}")
        
        # Create the fixed run.py file
        if create_fixed_run_py_file():
            # Create the batch script to apply the fix
            if create_fix_launcher_script(installation_path):
                logger.info("Fix script created successfully")
                print("\nFix prepared successfully!")
                print(f"To apply the fix, run the batch file: fix_app_import.bat")
            else:
                logger.error("Failed to create fix launcher script")
                print("\nError: Failed to create fix launcher script")
        else:
            logger.error("Failed to create fixed run.py file")
            print("\nError: Failed to create fixed run.py file")
    else:
        logger.error("KPI System installation not found")
        print("\nError: Could not find KPI System installation.")
        print("Please make sure the application is installed correctly.")
    
    logger.info("App import fix script completed")

if __name__ == "__main__":
    # Set up logging
    logger = setup_logging()
    
    # Run the main function
    main()
