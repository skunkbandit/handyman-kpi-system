# Database initialization and management components

"""
Database components for the Handyman KPI System Installer.

This module provides database adapters and schema files for various database systems.
"""

# Import database adapters dynamically to avoid import errors
# if a specific database driver is not installed
try:
    from .adapters.sqlite import SQLiteAdapter
except ImportError:
    SQLiteAdapter = None

try:
    from .adapters.mysql import MySQLAdapter
except ImportError:
    MySQLAdapter = None

try:
    from .adapters.postgresql import PostgreSQLAdapter
except ImportError:
    PostgreSQLAdapter = None

__all__ = [
    'SQLiteAdapter',
    'MySQLAdapter',
    'PostgreSQLAdapter',
]
