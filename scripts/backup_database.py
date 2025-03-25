#!/usr/bin/env python
"""
Database Backup Utility

This script creates backups of the application database and manages retention policies.
It can be run manually or scheduled via cron/scheduled tasks.

Usage:
    python -m scripts.backup_database [--output-dir DIR] [--retention DAYS] [--scheduled]
    
Options:
    --output-dir DIR      : Directory to store backups (default: instance/backups)
    --retention DAYS      : Number of days to keep backups (default: 7)
    --scheduled           : Run in scheduled mode with minimal output
    --verbose             : Show detailed output
"""

import os
import sys
import argparse
import sqlite3
import logging
import datetime
import shutil
import hashlib
import glob
import json
from pathlib import Path

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Database Backup Utility')
    parser.add_argument('--output-dir', help='Directory to store backups')
    parser.add_argument('--retention', type=int, help='Days to keep backups')
    parser.add_argument('--scheduled', action='store_true', help='Run in scheduled mode')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    return parser.parse_args()


def setup_logging(verbose=False, scheduled=False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    
    if scheduled:
        # When running in scheduled mode, log to a file
        log_dir = os.path.join('instance', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'backup.log')
        handlers = [
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    else:
        # When running manually, just log to console
        handlers = [logging.StreamHandler()]
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    return logging.getLogger('database_backup')


def calculate_file_hash(filepath):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    
    with open(filepath, "rb") as f:
        # Read and update hash in chunks for memory efficiency
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def backup_database(db_path, output_dir, logger):
    """Create a backup of the database"""
    if not os.path.exists(db_path):
        logger.error(f"Database file {db_path} does not exist")
        return None
    
    # Create backup directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"kpi_backup_{timestamp}.db"
    backup_path = os.path.join(output_dir, backup_filename)
    
    try:
        # Create backup connection
        conn = sqlite3.connect(db_path)
        # Backup database
        with sqlite3.connect(backup_path) as backup_conn:
            conn.backup(backup_conn)
        conn.close()
        
        # Calculate file hash
        file_hash = calculate_file_hash(backup_path)
        file_size = os.path.getsize(backup_path)
        
        logger.info(f"Created backup at {backup_path} ({file_size} bytes)")
        
        # Create metadata file
        metadata = {
            'filename': backup_filename,
            'original_db': db_path,
            'timestamp': timestamp,
            'datetime': datetime.datetime.now().isoformat(),
            'size': file_size,
            'hash': file_hash
        }
        
        metadata_path = f"{backup_path}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Record backup in database if it exists
        try:
            record_backup_in_db(db_path, backup_filename, file_size, file_hash, logger)
        except Exception as e:
            logger.warning(f"Could not record backup in database: {str(e)}")
        
        return backup_path
    
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except:
                pass
        return None


def record_backup_in_db(db_path, filename, size, file_hash, logger):
    """Record backup information in the database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if backups table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='backups';
        """)
        
        if not cursor.fetchone():
            logger.warning("Backups table does not exist in the database")
            conn.close()
            return False
        
        # Insert backup record
        cursor.execute("""
            INSERT INTO backups (
                filename, created_at, file_size, file_hash, is_automatic,
                status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            filename,
            datetime.datetime.now().isoformat(),
            size,
            file_hash,
            1,  # is_automatic = True
            'success',
            'Backup created via backup_database.py script'
        ))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        logger.warning(f"Could not record backup in database: {str(e)}")
        return False


def clean_old_backups(output_dir, retention_days, logger):
    """Delete backups older than retention_days"""
    if not os.path.exists(output_dir):
        logger.warning(f"Backup directory {output_dir} does not exist")
        return
    
    # Calculate cutoff date
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
    
    # Get all backup files
    backup_files = glob.glob(os.path.join(output_dir, "kpi_backup_*.db"))
    
    count_removed = 0
    for backup_file in backup_files:
        try:
            # Extract date from filename
            filename = os.path.basename(backup_file)
            date_str = filename.replace("kpi_backup_", "").split(".")[0]
            file_date = datetime.datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            
            # Check if file is older than cutoff
            if file_date < cutoff_date:
                # Remove backup file
                os.remove(backup_file)
                count_removed += 1
                
                # Remove metadata file if it exists
                metadata_file = f"{backup_file}.json"
                if os.path.exists(metadata_file):
                    os.remove(metadata_file)
                
                logger.info(f"Removed old backup: {filename}")
        except Exception as e:
            logger.warning(f"Error processing backup file {backup_file}: {str(e)}")
    
    logger.info(f"Removed {count_removed} old backups beyond {retention_days} days retention period")


def verify_backup(backup_path, logger):
    """Verify the integrity of a backup file"""
    if not os.path.exists(backup_path):
        logger.error(f"Backup file {backup_path} does not exist")
        return False
    
    # Check if metadata file exists
    metadata_path = f"{backup_path}.json"
    if not os.path.exists(metadata_path):
        logger.warning(f"Metadata file {metadata_path} not found, skipping verification")
        return True
    
    try:
        # Read metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Calculate current hash
        current_hash = calculate_file_hash(backup_path)
        
        # Compare with stored hash
        if current_hash != metadata.get('hash'):
            logger.error(f"Backup verification failed: Hash mismatch for {backup_path}")
            return False
        
        # Try to open the database to check structure
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Check if basic tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                logger.error(f"Backup verification failed: No tables found in {backup_path}")
                conn.close()
                return False
            
            # Check if key tables exist
            essential_tables = ['employees', 'evaluations', 'users', 'skills']
            missing_tables = [table for table in essential_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"Backup verification failed: Missing tables {missing_tables} in {backup_path}")
                conn.close()
                return False
            
            conn.close()
            
        except sqlite3.Error as e:
            logger.error(f"Backup verification failed: Cannot open database {backup_path}: {str(e)}")
            return False
        
        logger.info(f"Backup verification successful for {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Backup verification failed for {backup_path}: {str(e)}")
        return False


def main():
    """Main function"""
    args = parse_args()
    logger = setup_logging(args.verbose, args.scheduled)
    
    # Get database path from environment or use default
    db_path = os.environ.get(
        'DATABASE_PATH', 
        os.path.join('instance', 'database', 'kpi.db')
    )
    
    # Get output directory
    output_dir = args.output_dir or os.environ.get(
        'BACKUP_DIR',
        os.path.join('instance', 'backups')
    )
    
    # Get retention days
    retention_days = args.retention or int(os.environ.get(
        'BACKUP_RETENTION_DAYS', 
        '7'
    ))
    
    logger.info(f"Starting database backup from {db_path} to {output_dir}")
    logger.info(f"Retention policy: Keep backups for {retention_days} days")
    
    # Create backup
    backup_path = backup_database(db_path, output_dir, logger)
    
    if not backup_path:
        logger.error("Backup failed")
        sys.exit(1)
    
    # Verify backup
    if not verify_backup(backup_path, logger):
        logger.error("Backup verification failed")
        sys.exit(1)
    
    # Clean old backups
    clean_old_backups(output_dir, retention_days, logger)
    
    logger.info("Backup process completed successfully")


if __name__ == '__main__':
    main()
