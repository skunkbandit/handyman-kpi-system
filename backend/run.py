#!/usr/bin/env python3
"""
Run script for the KPI System application.

This script sets up and runs the Flask development server.
"""

from app import create_app
import os

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Get host and port from environment variables with defaults
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Run the application
    app.run(host=host, port=port, debug=debug)