#!/usr/bin/env python
"""
Database Migration Script for KPI System

This script is a wrapper around the migration manager that simplifies the 
process of migrating the database to the latest schema version.
"""

import os
import sys
import argparse
import logging
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
        logging.FileHandler("migration.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Database Migration")

def migrate_database(db_path, target_version=None):
    """
    Migrate the database to the latest version.
    
    Args:
        db_path (str): Path to the SQLite database file
        target_version (str, optional): Target version to migrate to
        
    Returns:
        bool: True if migration was successful, False otherwise
    """
    # Resolve paths
    db_path = os.path.abspath(db_path)
    migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'migrations'))
    
    logger.info(f"Starting database migration for {db_path}")
    logger.info(f"Using migrations from {migrations_dir}")
    
    # Check if database file exists
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created database directory: {db_dir}")
    
    # Check if migrations directory exists
    if not os.path.exists(migrations_dir):
        logger.error(f"Migrations directory not found: {migrations_dir}")
        return False
    
    # Create migration manager and run migrations
    manager = MigrationManager(db_path, migrations_dir)
    success = manager.migrate(target_version)
    
    if success:
        logger.info("Database migration completed successfully")
    else:
        logger.error("Database migration failed")
        
    return success

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Database Migration Script for KPI System")
    parser.add_argument("--db", help="Path to the SQLite database file")
    parser.add_argument("--target", help="Target version to migrate to (default: latest)")
    parser.add_argument("--env", choices=["dev", "test", "prod"], default="dev", 
                        help="Environment to use (uses environment-specific database path)")
    
    args = parser.parse_args()
    
    # Determine database path
    if args.db:
        db_path = args.db
    else:
        # Default database paths based on environment
        if args.env == "test":
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_database.db'))
        elif args.env == "prod":
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'kpi_system.db'))
        else:  # dev
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'kpi_system_dev.db'))
    
    # Run migration
    success = migrate_database(db_path, args.target)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())