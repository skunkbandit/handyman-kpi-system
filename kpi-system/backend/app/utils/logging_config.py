"""
Logging Configuration Module for KPI System

This module provides logging configuration that can be used across the application.
It sets up different handlers based on the environment and configuration settings.
"""

import os
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler

def setup_logging(app):
    """
    Configure logging for the application.
    
    Args:
        app: Flask application instance
    """
    # Get log level from config
    log_level_name = app.config.get('LOG_LEVEL', 'INFO')
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    # Set up basic configuration
    logging.basicConfig(level=log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Create rotating file handler
    log_file = app.config.get('LOG_FILE')
    if log_file:
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # Add to application logger
        app.logger.addHandler(file_handler)
    
    # Add email handler for errors in production
    if not app.debug and not app.testing:
        if app.config.get('MAIL_SERVER'):
            auth = None
            if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
                auth = (app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'))
                
            secure = None
            if app.config.get('MAIL_USE_TLS'):
                secure = ()
                
            mail_handler = SMTPHandler(
                mailhost=(app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT')),
                fromaddr=app.config.get('MAIL_DEFAULT_SENDER'),
                toaddrs=app.config.get('ADMINS', ['admin@example.com']),
                subject='KPI System Error',
                credentials=auth,
                secure=secure
            )
            mail_handler.setFormatter(formatter)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
    
    # Set logger level
    app.logger.setLevel(log_level)
    
    # Log application startup
    app.logger.info('KPI System starting up')
    app.logger.info(f'Environment: {app.config.get("ENV", "development")}')
    app.logger.info(f'Debug: {app.debug}')
    
    return app.logger

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)
    
    # Create console handler if no handlers exist
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console_handler)
        
    return logger
