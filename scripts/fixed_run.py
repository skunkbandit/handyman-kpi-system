#!/usr/bin/env python3
"""
Run script for the KPI System application - Enhanced Version

This script sets up and runs the Flask development server with improved
import handling to resolve "module app has no attribute create_app" errors.
"""

import os
import sys
import importlib.util
import logging
import traceback
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
logging.info('Starting backend application - Enhanced Version')
logging.info(f'Current working directory: {os.getcwd()}')
logging.info(f'Python path: {sys.executable}')
logging.info('Python module search paths:')
for path in sys.path:
    logging.info(f'  {path}')

def debug_directory_structure(base_path):
    """Log directory structure for debugging"""
    try:
        for root, dirs, files in os.walk(base_path):
            rel_path = os.path.relpath(root, base_path)
            if rel_path == '.':
                logging.info(f"Directory structure of {base_path}:")
            else:
                logging.info(f"  {rel_path}/")
            
            for file in files:
                if rel_path == '.':
                    logging.info(f"  {file}")
                else:
                    logging.info(f"  {rel_path}/{file}")
    except Exception as e:
        logging.error(f"Error debugging directory structure: {e}")

try:
    # Set up common directory paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = current_dir
    app_dir = os.path.join(backend_dir, "app")
    parent_dir = os.path.dirname(backend_dir)
    
    logging.info(f'Backend directory: {backend_dir}')
    logging.info(f'App directory: {app_dir}')
    
    # Debug directory structure
    if not os.path.exists(app_dir):
        logging.error(f"App directory does not exist: {app_dir}")
        debug_directory_structure(backend_dir)
        raise FileNotFoundError(f"App directory not found: {app_dir}")
    
    # Make sure all important dirs are in path
    for path in [backend_dir, app_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
            logging.info(f'Added directory to path: {path}')
    
    # Method 1: Direct import using importlib
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
                logging.error(f"The app module does not have a create_app function")
                logging.info(f"Available attributes: {dir(app_module)}")
                raise ImportError("No create_app function found in app/__init__.py")
        else:
            logging.error(f"app/__init__.py not found at {init_path}")
            debug_directory_structure(backend_dir)
            raise FileNotFoundError(f"Cannot find {init_path}")
            
    except Exception as e:
        logging.error(f"Error using direct import approach: {e}")
        logging.error(traceback.format_exc())
        
        # Method 2: Standard import approach
        try:
            logging.info("Trying standard import approach")
            from app import create_app
            logging.info("Successfully imported create_app through standard import")
        except ImportError as e2:
            logging.error(f"Standard import approach failed: {e2}")
            logging.error(traceback.format_exc())
            
            # Method 3: Last resort with module injection
            try:
                logging.info("Trying backup import approach")
                # Try to import the module directly
                import app
                
                # Check if the module itself has the attribute
                if hasattr(app, "create_app"):
                    create_app = app.create_app
                    logging.info("Successfully retrieved create_app from app module")
                else:
                    logging.error("app module loaded but has no create_app attribute")
                    logging.info(f"Available attributes: {dir(app)}")
                    
                    # Look for functions that might be the app factory
                    factory_candidates = [attr for attr in dir(app) 
                                        if callable(getattr(app, attr)) and attr.endswith("_app")]
                    
                    if factory_candidates:
                        logging.info(f"Found potential app factory candidates: {factory_candidates}")
                        create_app = getattr(app, factory_candidates[0])
                        logging.info(f"Using {factory_candidates[0]} as create_app")
                    else:
                        logging.error("No suitable app factory function found")
                        raise ImportError("Could not locate the create_app function using any import method")
            except Exception as e3:
                logging.error(f"Backup import approach failed: {e3}")
                logging.error(traceback.format_exc())
                raise ImportError("Could not locate the create_app function using any import method")
    
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
