"""Database adapters for the Handyman KPI System Installer.

This package contains database adapters for different database types,
including SQLite, MySQL, and PostgreSQL.
"""

from .base import BaseDatabaseAdapter

# Dictionary of adapter class names by database type
ADAPTER_TYPES = {
    'sqlite': 'sqlite',
    'mysql': 'mysql',
    'postgresql': 'postgresql'
}

def get_adapter(db_type, config):
    """
    Factory function to get the appropriate database adapter.
    
    Args:
        db_type (str): Database type ('sqlite', 'mysql', or 'postgresql')
        config (dict): Database configuration
        
    Returns:
        DatabaseAdapter: Appropriate database adapter
        
    Raises:
        ValueError: If db_type is not supported
        ImportError: If required database library is not installed
    """
    if db_type not in ADAPTER_TYPES:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    try:
        adapter_module = __import__(
            f"{ADAPTER_TYPES[db_type]}",
            globals(),
            locals(),
            ['DatabaseAdapter'],
            1
        )
        return adapter_module.DatabaseAdapter(config)
    except ImportError as e:
        # Re-raise with clearer message
        raise ImportError(f"Failed to load database adapter for {db_type}: {str(e)}")