#!/usr/bin/env python
"""
Production Environment Setup Script for KPI System

This script sets up the production environment for the KPI System,
including directory structure, configuration, and initial database.
"""

import os
import sys
import argparse
import logging
import shutil
import subprocess
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import migration manager
from database.migrations.migration_manager import MigrationManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("setup_production.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Production Setup")

def create_directory_structure(base_dir):
    """
    Create the directory structure for production deployment.
    
    Args:
        base_dir (str): Base directory for the deployment
        
    Returns:
        dict: Dictionary mapping directory names to paths
    """
    logger.info(f"Creating directory structure in {base_dir}")
    
    # Define directory structure
    directories = {
        'database': os.path.join(base_dir, 'database'),
        'uploads': os.path.join(base_dir, 'uploads'),
        'backups': os.path.join(base_dir, 'backups'),
        'logs': os.path.join(base_dir, 'logs'),
        'instance': os.path.join(base_dir, 'instance'),
    }
    
    # Create directories
    for name, path in directories.items():
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"Created directory: {path}")
        else:
            logger.info(f"Directory already exists: {path}")
    
    return directories

def create_instance_config(instance_dir, secret_key=None):
    """
    Create instance-specific configuration.
    
    Args:
        instance_dir (str): Instance directory
        secret_key (str, optional): Secret key for the application
        
    Returns:
        str: Path to the config file
    """
    import secrets
    
    # Generate secret key if not provided
    if secret_key is None:
        secret_key = secrets.token_hex(32)
    
    # Create config file
    config_path = os.path.join(instance_dir, 'config.py')
    
    with open(config_path, 'w') as f:
        f.write(f"""# Instance-specific configuration for KPI System
SECRET_KEY = '{secret_key}'
FLASK_ENV = 'production'
DEBUG = False
TESTING = False

# Database settings
DATABASE_PATH = '{os.path.join(os.path.dirname(instance_dir), 'database', 'kpi_system.db').replace('\\', '/')}'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

# File paths
UPLOAD_FOLDER = '{os.path.join(os.path.dirname(instance_dir), 'uploads').replace('\\', '/')}'
BACKUP_FOLDER = '{os.path.join(os.path.dirname(instance_dir), 'backups').replace('\\', '/')}'
LOG_FILE = '{os.path.join(os.path.dirname(instance_dir), 'logs', 'kpi_system.log').replace('\\', '/')}'

# Logging settings
LOG_LEVEL = 'INFO'

# Email settings (update with actual values)
MAIL_SERVER = 'smtp.example.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'user@example.com'
MAIL_PASSWORD = 'password'
MAIL_DEFAULT_SENDER = 'kpi-system@example.com'

# Admin email for error notifications
ADMINS = ['admin@example.com']

# Security settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = 28800  # 8 hours in seconds

# Health check key
HEALTH_CHECK_KEY = '{secrets.token_urlsafe(16)}'
""")
    
    logger.info(f"Created instance config file: {config_path}")
    return config_path

def setup_database(db_path, migrations_dir):
    """
    Set up the production database.
    
    Args:
        db_path (str): Path to the database file
        migrations_dir (str): Directory containing migration scripts
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Setting up database at {db_path}")
    
    # Ensure database directory exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created database directory: {db_dir}")
    
    # Run migrations
    manager = MigrationManager(db_path, migrations_dir)
    success = manager.migrate()
    
    if success:
        logger.info("Database setup completed successfully")
    else:
        logger.error("Database setup failed")
        
    return success

def create_wsgi_file(base_dir):
    """
    Create WSGI file for production deployment.
    
    Args:
        base_dir (str): Base directory for the deployment
        
    Returns:
        str: Path to the WSGI file
    """
    wsgi_path = os.path.join(base_dir, 'wsgi.py')
    
    with open(wsgi_path, 'w') as f:
        f.write("""#!/usr/bin/env python
import os
import sys

# Add application to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set instance path
os.environ['FLASK_APP'] = 'kpi-system.backend.run'
os.environ['FLASK_ENV'] = 'production'
os.environ['INSTANCE_PATH'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')

# Import the application
from kpi-system.backend.run import app as application

if __name__ == '__main__':
    application.run()
""")
    
    logger.info(f"Created WSGI file: {wsgi_path}")
    return wsgi_path

def install_requirements(requirements_file, venv_dir=None):
    """
    Install Python requirements.
    
    Args:
        requirements_file (str): Path to requirements.txt
        venv_dir (str, optional): Path to virtual environment directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Installing requirements")
    
    try:
        pip_cmd = 'pip'
        
        # Use virtualenv if specified
        if venv_dir:
            if os.name == 'nt':  # Windows
                pip_cmd = os.path.join(venv_dir, 'Scripts', 'pip')
            else:  # Unix-like
                pip_cmd = os.path.join(venv_dir, 'bin', 'pip')
        
        # Run pip install
        cmd = [pip_cmd, 'install', '-r', requirements_file]
        subprocess.run(cmd, check=True)
        
        logger.info("Requirements installed successfully")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to install requirements: {e}")
        return False
    except Exception as e:
        logger.error(f"Error installing requirements: {e}")
        return False

def create_systemd_service(base_dir, service_name="kpi-system"):
    """
    Create systemd service file for Linux deployment.
    
    Args:
        base_dir (str): Base directory for the deployment
        service_name (str): Name for the systemd service
        
    Returns:
        str: Path to the service file
    """
    service_path = os.path.join(base_dir, f"{service_name}.service")
    
    # Determine paths
    wsgi_path = os.path.join(base_dir, 'wsgi.py')
    venv_path = os.path.join(base_dir, 'venv')
    gunicorn_path = os.path.join(venv_path, 'bin', 'gunicorn')
    
    with open(service_path, 'w') as f:
        f.write(f"""[Unit]
Description=KPI System Web Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory={base_dir}
Environment="PATH={venv_path}/bin"
ExecStart={gunicorn_path} --workers 3 --bind unix:{base_dir}/kpi-system.sock -m 007 wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
""")
    
    logger.info(f"Created systemd service file: {service_path}")
    logger.info(f"To install the service, run:")
    logger.info(f"  sudo cp {service_path} /etc/systemd/system/")
    logger.info(f"  sudo systemctl daemon-reload")
    logger.info(f"  sudo systemctl enable {service_name}")
    logger.info(f"  sudo systemctl start {service_name}")
    
    return service_path

def setup_production(base_dir, requirements_file=None, venv_dir=None, create_service=False):
    """
    Set up the production environment.
    
    Args:
        base_dir (str): Base directory for the deployment
        requirements_file (str, optional): Path to requirements.txt
        venv_dir (str, optional): Path to virtual environment directory
        create_service (bool): Whether to create a systemd service file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory structure
        directories = create_directory_structure(base_dir)
        
        # Create instance config
        config_path = create_instance_config(directories['instance'])
        
        # Set up database
        migrations_dir = os.path.join(base_dir, 'database', 'migrations')
        db_path = os.path.join(directories['database'], 'kpi_system.db')
        db_success = setup_database(db_path, migrations_dir)
        
        # Create WSGI file
        wsgi_path = create_wsgi_file(base_dir)
        
        # Install requirements if specified
        if requirements_file:
            req_success = install_requirements(requirements_file, venv_dir)
            if not req_success:
                logger.warning("Failed to install requirements")
        
        # Create systemd service file if requested
        if create_service and os.name != 'nt':  # Not on Windows
            service_path = create_systemd_service(base_dir)
        
        logger.info("Production environment setup completed")
        logger.info(f"Base directory: {base_dir}")
        logger.info(f"Config file: {config_path}")
        logger.info(f"Database: {db_path}")
        logger.info(f"WSGI file: {wsgi_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error setting up production environment: {e}")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Production Environment Setup for KPI System")
    parser.add_argument("--dir", help="Base directory for the deployment")
    parser.add_argument("--req", help="Path to requirements.txt")
    parser.add_argument("--venv", help="Path to virtual environment directory")
    parser.add_argument("--service", action="store_true", help="Create systemd service file")
    
    args = parser.parse_args()
    
    # Determine base directory
    base_dir = args.dir or os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'production'))
    
    # Determine requirements file
    requirements_file = args.req
    if not requirements_file:
        default_req = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
        if os.path.exists(default_req):
            requirements_file = default_req
    
    # Run setup
    success = setup_production(
        base_dir=base_dir,
        requirements_file=requirements_file,
        venv_dir=args.venv,
        create_service=args.service
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())