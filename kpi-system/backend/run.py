#!/usr/bin/env python3
"""
Run script for the KPI System application.

This script sets up and runs the Flask development server with enhanced
module import handling to prevent common import errors.
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
logging.info('Starting backend application')
logging.info(f'Current working directory: {os.getcwd()}')
logging.info(f'Python path: {sys.executable}')
logging.info('Python module search paths:')
for path in sys.path:
    logging.info(f'  {path}')

try:
    # Configure the path for module imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(current_dir, "app")
    parent_dir = os.path.dirname(current_dir)
    
    # Add necessary directories to path
    for path in [app_dir, current_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
            logging.info(f'Added directory to path: {path}')
    
    # Use direct module loading with multiple fallback strategies
    create_app = None
    
    # Strategy 1: Direct module loading using importlib
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
        else:
            logging.error(f"app/__init__.py not found at {init_path}")
    except Exception as e:
        logging.error(f"Error using direct import approach: {e}")
    
    # Strategy 2: Standard import approach
    if create_app is None:
        try:
            logging.info("Trying standard import approach")
            from app import create_app
            logging.info("Successfully imported create_app through standard import")
        except ImportError as e:
            logging.error(f"Standard import approach failed: {e}")
    
    # Strategy 3: Backup import approach
    if create_app is None:
        try:
            logging.info("Trying backup import approach")
            import app
            
            # Check if the module has the create_app attribute
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
        except Exception as e:
            logging.error(f"Backup import approach failed: {e}")
    
    # Final check - if we still don't have create_app, raise an error
    if create_app is None:
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
