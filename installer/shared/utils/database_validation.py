"""Database Validation Utilities for the KPI System Installer

This module provides utilities for validating database connections and settings.
"""

import os
from pathlib import Path

from .logging_utils import get_logger

logger = get_logger(__name__)


def validate_database_connection(db_type, connection_params):
    """
    Validate database connection parameters.
    
    Args:
        db_type (str): Database type ('sqlite', 'mysql', 'postgresql')
        connection_params (dict): Connection parameters for the database
        
    Returns:
        bool: True if the connection parameters are valid, False otherwise
    """
    try:
        if db_type.lower() == 'sqlite':
            # SQLite requires a valid file path
            path_str = connection_params.get('database')
            if not path_str:
                logger.warning("SQLite database path is missing")
                return False
                
            path = Path(path_str)
            
            # If the file exists, it should be a file and readable
            if path.exists() and (not path.is_file() or not os.access(path, os.R_OK)):
                logger.warning(f"SQLite database exists but is not a readable file: {path}")
                return False
                
            # If the file doesn't exist, its parent directory should exist and be writable
            if not path.exists():
                parent = path.parent
                if not parent.exists() or not os.access(parent, os.W_OK):
                    logger.warning(f"Parent directory for SQLite database does not exist or is not writable: {parent}")
                    return False
                    
            return True
            
        elif db_type.lower() in ('mysql', 'postgresql'):
            # Required parameters
            required_params = ['host', 'port', 'user', 'database']
            
            # Check if all required parameters are present
            for param in required_params:
                if param not in connection_params:
                    logger.warning(f"Required parameter '{param}' missing for {db_type} connection")
                    return False
                    
            # Validate port
            port = connection_params.get('port')
            try:
                port_num = int(port)
                if port_num < 1 or port_num > 65535:
                    logger.warning(f"Invalid port number: {port}")
                    return False
            except (ValueError, TypeError):
                logger.warning(f"Port is not a valid number: {port}")
                return False
                
            # Validate host (basic check)
            host = connection_params.get('host')
            if not host:
                logger.warning("Host is empty")
                return False
                
            # Validate database name (basic check)
            database = connection_params.get('database')
            if not database:
                logger.warning("Database name is empty")
                return False
                
            # Validate username (basic check)
            user = connection_params.get('user')
            if not user:
                logger.warning("Username is empty")
                return False
                
            return True
            
        else:
            # Unsupported database type
            logger.warning(f"Unsupported database type: {db_type}")
            return False
            
    except Exception as e:
        # Log but don't raise; return False instead
        logger.error(f"Error validating database connection: {e}")
        return False