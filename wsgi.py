"""
WSGI Entry Point for Production Deployment

This file serves as the entry point for WSGI-compatible web servers (e.g., Gunicorn, uWSGI).
It sets up the Flask application with production-ready configuration.

Usage:
    # With Gunicorn
    gunicorn --bind 0.0.0.0:5000 wsgi:app
    
    # With uWSGI
    uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app
"""

import os
import sys
from pathlib import Path

# Add the application directory to the Python path
app_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(app_dir))

# Set the environment variable for configuration
os.environ.setdefault('FLASK_ENV', 'production')

# Import and create the Flask application
from kpi-system.backend.app import create_app

# Create the application instance
app = create_app()

# Application initialization hook - runs when the WSGI server starts
@app.before_first_request
def initialize_application():
    """
    Initialize application services before handling the first request.
    This is useful for setting up database connections, caches, etc.
    """
    app.logger.info("Initializing application services...")
    
    # Ensure instance directories exist
    for directory in ['logs', 'backups', 'temp', 'database']:
        path = Path(app.instance_path) / directory
        path.mkdir(exist_ok=True)
    
    # Initialize services
    from kpi-system.backend.services import initialize_services
    initialize_services(app)
    
    app.logger.info("Application initialization complete")


if __name__ == "__main__":
    # When run directly, use built-in development server
    # This is NOT recommended for production
    app.run(host='0.0.0.0', port=5000)
