#!/usr/bin/env python
"""
Database Backup Script for KPI System

This script creates a backup of the KPI system database, including metadata
about the backup in the backups table. It can be run manually or scheduled
as a cron job or Windows scheduled task.
"""

import os
import sys
import sqlite3
import argparse
import logging
import datetime
import shutil
import hashlib
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Database Backup")

def calculate_checksum(filepath):
    """
    Calculate the SHA-256 checksum of a file.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        str: Hexadecimal checksum
    """
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()

def get_schema_version(conn):
    """
    Get the current database schema version.
    
    Args:
        conn: SQLite database connection
        
    Returns:
        str: Current schema version or "unknown"
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return "unknown"
    except Exception as e:
        logger.error(f"Error getting schema version: {e}")
        return "unknown"

def record_backup(conn, filename, description, size_bytes, checksum, user_id=None, is_automatic=True):
    """
    Record backup metadata in the backups table.
    
    Args:
        conn: SQLite database connection
        filename (str): Backup filename
        description (str): Backup description
        size_bytes (int): Backup file size in bytes
        checksum (str): File checksum
        user_id (int, optional): ID of the user who created the backup
        is_automatic (bool): Whether the backup was created automatically
        
    Returns:
        int: ID of the new backup record, or None if failed
    """
    try:
        cursor = conn.cursor()
        
        # Get the current schema version
        db_version = get_schema_version(conn)
        
        # Insert backup record
        cursor.execute(
            """
            INSERT INTO backups (
                filename, description, size_bytes, created_by, created_at,
                db_version, is_automatic, checksum
            ) VALUES (?, ?, ?, ?, datetime('now'), ?, ?, ?)
            """,
            (filename, description, size_bytes, user_id, db_version, is_automatic, checksum)
        )
        
        # Get the ID of the new record
        backup_id = cursor.lastrowid
        
        # Commit the transaction
        conn.commit()
        
        return backup_id
    except Exception as e:
        logger.error(f"Error recording backup: {e}")
        if conn:
            conn.rollback()
        return None

def enforce_retention_policy(backup_dir, retention_count, conn=None):
    """
    Delete old backups to enforce the retention policy.
    
    Args:
        backup_dir (str): Directory containing backups
        retention_count (int): Number of backups to keep
        conn (Connection, optional): Database connection to update backups table
        
    Returns:
        int: Number of backups deleted
    """
    try:
        # Get list of backup files
        backup_files = []
        for file in os.listdir(backup_dir):
            if file.endswith('.db') or file.endswith('.sqlite'):
                # Get file path and modification time
                file_path = os.path.join(backup_dir, file)
                mod_time = os.path.getmtime(file_path)
                backup_files.append((file, file_path, mod_time))
        
        # Sort by modification time (oldest first)
        backup_files.sort(key=lambda x: x[2])
        
        # Determine how many to delete
        delete_count = max(0, len(backup_files) - retention_count)
        if delete_count == 0:
            return 0
            
        # Delete oldest backups
        deleted_count = 0
        for filename, file_path, _ in backup_files[:delete_count]:
            try:
                # Delete the file
                os.remove(file_path)
                
                # Update the database if connection provided
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM backups WHERE filename = ?", (filename,))
                    conn.commit()
                
                logger.info(f"Deleted old backup: {filename}")
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting backup {filename}: {e}")
        
        return deleted_count
    except Exception as e:
        logger.error(f"Error enforcing retention policy: {e}")
        return 0

def backup_database(db_path, backup_dir, description=None, user_id=None, is_automatic=True, retention_count=10):
    """
    Create a backup of the database.
    
    Args:
        db_path (str): Path to the database file
        backup_dir (str): Directory to store backups
        description (str, optional): Backup description
        user_id (int, optional): ID of the user who created the backup
        is_automatic (bool): Whether the backup was created automatically
        retention_count (int): Number of backups to keep
        
    Returns:
        dict: Backup metadata or None if failed
    """
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        logger.info(f"Created backup directory: {backup_dir}")
    
    # Validate database path
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return None
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    db_filename = os.path.basename(db_path)
    backup_filename = f"{os.path.splitext(db_filename)[0]}_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Generate description if not provided
    if description is None:
        description = f"Automatic backup created on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Ensure the database is in a consistent state
        conn.execute("PRAGMA wal_checkpoint(FULL)")
        
        # Create a backup connection and back up the database
        # Close the main database connection first to avoid conflicts
        conn.close()
        
        # Copy the database file
        shutil.copy2(db_path, backup_path)
        
        # Get file size
        size_bytes = os.path.getsize(backup_path)
        
        # Calculate checksum
        checksum = calculate_checksum(backup_path)
        
        # Reconnect to record backup
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Record backup in the database
        backup_id = record_backup(
            conn, backup_filename, description, size_bytes, 
            checksum, user_id, is_automatic
        )
        
        # Enforce retention policy
        deleted_count = enforce_retention_policy(backup_dir, retention_count, conn)
        
        # Clean up
        conn.close()
        
        logger.info(f"Database backup created: {backup_path}")
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} old backups to enforce retention policy")
        
        # Return backup metadata
        return {
            'id': backup_id,
            'filename': backup_filename,
            'path': backup_path,
            'description': description,
            'size_bytes': size_bytes,
            'size_formatted': format_size(size_bytes),
            'timestamp': timestamp,
            'checksum': checksum
        }
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        
        # Clean up partial backup if it exists
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up partial backup: {cleanup_error}")
        
        return None

def format_size(size_bytes):
    """
    Format size in bytes to a human-readable string.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string (e.g., "1.23 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024 or unit == 'TB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Database Backup Tool for KPI System")
    parser.add_argument("--db", help="Path to the SQLite database file")
    parser.add_argument("--dir", help="Directory to store backup files")
    parser.add_argument("--desc", help="Backup description")
    parser.add_argument("--user", type=int, help="User ID of the backup creator")
    parser.add_argument("--auto", action="store_true", help="Mark as automatic backup")
    parser.add_argument("--retain", type=int, default=10, help="Number of backups to retain")
    parser.add_argument("--env", choices=["dev", "test", "prod"], default="prod", 
                        help="Environment to use (uses environment-specific paths)")
    
    args = parser.parse_args()
    
    # Determine database and backup paths
    if args.db and args.dir:
        db_path = args.db
        backup_dir = args.dir
    else:
        # Default paths based on environment
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        if args.env == "test":
            db_path = os.path.join(base_dir, 'tests', 'test_database.db')
            backup_dir = os.path.join(base_dir, 'tests', 'backups')
        elif args.env == "dev":
            db_path = os.path.join(base_dir, 'database', 'kpi_system_dev.db')
            backup_dir = os.path.join(base_dir, 'backups', 'dev')
        else:  # prod
            db_path = os.path.join(base_dir, 'database', 'kpi_system.db')
            backup_dir = os.path.join(base_dir, 'backups', 'prod')
    
    # Create the backup
    result = backup_database(
        db_path=db_path,
        backup_dir=backup_dir,
        description=args.desc,
        user_id=args.user,
        is_automatic=args.auto,
        retention_count=args.retain
    )
    
    # Report result
    if result:
        logger.info("Backup completed successfully")
        logger.info(f"Backup ID: {result['id']}")
        logger.info(f"Filename: {result['filename']}")
        logger.info(f"Size: {result['size_formatted']}")
        logger.info(f"Path: {result['path']}")
        return 0
    else:
        logger.error("Backup failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())