#!/usr/bin/env python
"""
Database Migration Utility

This script runs database migrations to update the database schema to the latest version
or to a specific target version.

Usage:
    python -m scripts.migrate_database [--target-version VERSION] [--downgrade] [--backup]
    
Options:
    --target-version VERSION  : Migrate to a specific version (default: latest)
    --downgrade               : Downgrade the database to the target version
    --backup                  : Create a backup before migrating
    --dry-run                 : Show what migrations would be applied without executing them
    --verbose                 : Show detailed output
"""

import os
import sys
import argparse
import sqlite3
import logging
import datetime
import importlib
import re
from pathlib import Path

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.migrations.migration_manager import MigrationManager


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Database Migration Utility')
    parser.add_argument('--target-version', help='Target version to migrate to')
    parser.add_argument('--downgrade', action='store_true', help='Downgrade to target version')
    parser.add_argument('--backup', action='store_true', help='Create a backup before migrating')
    parser.add_argument('--dry-run', action='store_true', help='Show migrations without executing')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    return parser.parse_args()


def setup_logging(verbose=False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger('migration')


def backup_database(db_path, logger):
    """Create a backup of the database"""
    if not os.path.exists(db_path):
        logger.warning(f"Database file {db_path} does not exist - no backup needed")
        return True

    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"pre_migration_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Create backup connection
        conn = sqlite3.connect(db_path)
        # Backup database
        with sqlite3.connect(backup_path) as backup_conn:
            conn.backup(backup_conn)
        conn.close()
        logger.info(f"Created backup at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        return False


def main():
    """Main function"""
    args = parse_args()
    logger = setup_logging(args.verbose)
    
    # Get database path - use environment variable if set, otherwise use default
    db_path = os.environ.get(
        'DATABASE_PATH', 
        os.path.join('instance', 'database', 'kpi.db')
    )
    
    # Make sure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    logger.info(f"Using database at {db_path}")
    
    # Create backup if requested
    if args.backup:
        if not backup_database(db_path, logger):
            logger.error("Aborting migration due to backup failure")
            sys.exit(1)
    
    # Initialize migration manager
    migration_manager = MigrationManager(db_path, logger)
    
    try:
        # Get current version
        current_version = migration_manager.get_current_version()
        logger.info(f"Current database version: {current_version or 'No version - new database'}")
        
        # Get all available migrations
        available_migrations = migration_manager.get_available_migrations()
        logger.info(f"Found {len(available_migrations)} available migrations")
        
        if args.dry_run:
            logger.info("DRY RUN - no changes will be made")
        
        # Run migrations
        if args.downgrade:
            if not args.target_version:
                logger.error("Target version must be specified for downgrade")
                sys.exit(1)
            
            logger.info(f"Downgrading to version {args.target_version}")
            if not args.dry_run:
                success = migration_manager.downgrade_to_version(args.target_version)
                if success:
                    logger.info(f"Successfully downgraded to version {args.target_version}")
                else:
                    logger.error("Downgrade failed")
                    sys.exit(1)
        else:
            target_version = args.target_version or 'latest'
            logger.info(f"Upgrading to version {target_version}")
            if not args.dry_run:
                success = migration_manager.upgrade_to_version(target_version)
                if success:
                    new_version = migration_manager.get_current_version()
                    logger.info(f"Successfully upgraded to version {new_version}")
                else:
                    logger.error("Upgrade failed")
                    sys.exit(1)
        
        logger.info("Migration complete")
    
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
