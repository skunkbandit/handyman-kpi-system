#!/usr/bin/env python3
"""
Run script for the KPI System application.

This script sets up and runs the Flask development server.
"""

import os
import sys
import logging

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
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=os.path.join(logs_dir, 'backend.log'),
        filemode='a'
    )
except Exception as e:
    # Fallback logging to stdout if file logging fails
    print(f"Warning: Could not set up file logging: {e}")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    for path in [current_dir, app_dir, parent_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)
            logging.info(f'Added directory to path: {path}')
    
    # Use the alternative import approach that was successful in testing
    try:
        # Attempt to import with the proven alternative approach
        import app
        create_app = app.create_app
        logging.info('Successfully imported app module')
    except ImportError as e:
        # Log the error but don't panic yet
        logging.error(f'Error importing app module directly: {e}')
        
        # Try the traditional approach as a backup
        try:
            from app import create_app
            logging.info('Successfully imported create_app from app module')
        except ImportError as e2:
            logging.error(f'Failed to import create_app from app: {e2}')
            # Re-raise the error for proper error handling
            raise e

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
