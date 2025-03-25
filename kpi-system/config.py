"""
Configuration file for the KPI System.

This module defines configuration classes for different environments (development,
testing, production) and provides a factory method to create the appropriate
configuration instance based on the environment.
"""

import os
import secrets
from datetime import timedelta

class Config:
    """Base configuration class with settings common to all environments."""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'kpi_system.db'))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    
    # File upload settings
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Backup settings
    BACKUP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backups'))
    BACKUP_RETENTION_COUNT = 10
    
    # Email settings (placeholder - not implemented)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'user@example.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'password')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'kpi-system@example.com')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', 'kpi_system.log'))
    
    # Default pagination
    ITEMS_PER_PAGE = 20
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration."""
        # Ensure required directories exist
        for folder in [app.config['UPLOAD_FOLDER'], app.config['BACKUP_FOLDER'], 
                       os.path.dirname(app.config['LOG_FILE'])]:
            if not os.path.exists(folder):
                os.makedirs(folder)


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Override security for development
    SESSION_COOKIE_SECURE = False
    
    # Database for development
    DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'kpi_system_dev.db'))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    
    # Enable SQLAlchemy query logging
    SQLALCHEMY_ECHO = True
    
    # Mail settings for development
    MAIL_SUPPRESS_SEND = True  # Don't actually send emails in development
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with development configuration."""
        Config.init_app(app)
        # Additional development-specific initialization


class TestingConfig(Config):
    """Testing environment configuration."""
    
    DEBUG = False
    TESTING = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF protection in tests
    WTF_CSRF_ENABLED = False
    
    # Mail settings for testing
    MAIL_SUPPRESS_SEND = True
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with testing configuration."""
        Config.init_app(app)
        # Additional testing-specific initialization


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Get secret key from environment variable in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database for production
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 
                                  os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'kpi_system.db')))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    
    # Security headers for production
    SECURE_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
    }
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with production configuration."""
        Config.init_app(app)
        
        # Production logging to file
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=10*1024*1024, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Apply security headers
        @app.after_request
        def apply_security_headers(response):
            for header, value in app.config.get('SECURE_HEADERS', {}).items():
                response.headers[header] = value
            return response


class DockerConfig(ProductionConfig):
    """Docker container configuration."""
    
    # Override paths for Docker container
    DATABASE_PATH = '/app/data/kpi_system.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    UPLOAD_FOLDER = '/app/uploads'
    BACKUP_FOLDER = '/app/backups'
    LOG_FILE = '/app/logs/kpi_system.log'
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with Docker configuration."""
        ProductionConfig.init_app(app)
        # Additional Docker-specific initialization


# Dictionary mapping environment names to configuration classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """
    Get the configuration class based on the environment name.
    
    Args:
        config_name (str, optional): Environment name. If None, use the
            FLASK_ENV environment variable or default to 'development'.
            
    Returns:
        Config: Configuration class instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])
