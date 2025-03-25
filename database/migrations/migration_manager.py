"""
Migration Manager for KPI System Database

This script manages database migrations, ensuring that the schema is upgraded
in sequence without data loss. It uses the schema_version table to track which
migrations have been applied.
"""

import os
import sqlite3
import importlib.util
import logging
import datetime
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("migration.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Migration Manager")

class MigrationManager:
    def __init__(self, db_path, migrations_dir):
        """
        Initialize the migration manager.
        
        Args:
            db_path (str): Path to the SQLite database file
            migrations_dir (str): Directory containing migration scripts
        """
        self.db_path = db_path
        self.migrations_dir = migrations_dir
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish a connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            return False
            
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
            
    def ensure_version_table(self):
        """Create the schema_version table if it doesn't exist."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            ''')
            self.conn.commit()
            logger.info("Schema version table verified/created")
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to create version table: {e}")
            return False
            
    def get_current_version(self):
        """Get the current schema version from the database."""
        try:
            self.cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
            result = self.cursor.fetchone()
            if result:
                version = result['version']
                logger.info(f"Current database version: {version}")
                return version
            else:
                logger.info("No version found in database, assuming initial state")
                return "0.0.0"
        except sqlite3.Error as e:
            logger.error(f"Error retrieving current version: {e}")
            return None
            
    def get_available_migrations(self):
        """
        Get a list of available migration scripts sorted by version.
        
        Returns:
            list: List of (version, filepath) tuples sorted by version
        """
        migrations = []
        
        try:
            migration_files = [f for f in os.listdir(self.migrations_dir) 
                              if f.endswith('.py') and f != '__init__.py']
            
            for file in migration_files:
                # Extract version from filename format: v1_0_0_description.py
                if file.startswith('v'):
                    parts = file.split('_')
                    if len(parts) >= 3:  # At least v1_0_0
                        version = parts[0][1:] + '.' + parts[1] + '.' + parts[2]
                        filepath = os.path.join(self.migrations_dir, file)
                        migrations.append((version, filepath))
            
            # Sort by version
            migrations.sort(key=lambda x: [int(n) for n in x[0].split('.')])
            return migrations
            
        except Exception as e:
            logger.error(f"Error getting available migrations: {e}")
            return []
            
    def run_migration(self, filepath):
        """
        Run a single migration script.
        
        Args:
            filepath (str): Path to the migration script
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load the module dynamically
            module_name = os.path.basename(filepath).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module has the required functions
            if hasattr(module, 'upgrade') and callable(module.upgrade):
                # Begin transaction
                logger.info(f"Running migration: {filepath}")
                
                # Pass connection to the upgrade function
                module.upgrade(self.conn)
                
                # Get version and description
                version = getattr(module, 'version', 'unknown')
                description = getattr(module, 'description', 'No description provided')
                
                # Update schema version
                self.cursor.execute(
                    "INSERT INTO schema_version (version, description) VALUES (?, ?)",
                    (version, description)
                )
                
                # Commit transaction
                self.conn.commit()
                logger.info(f"Migration completed successfully: {version} - {description}")
                return True
            else:
                logger.error(f"Migration file {filepath} does not contain required 'upgrade' function")
                return False
                
        except Exception as e:
            # Rollback transaction
            if self.conn:
                self.conn.rollback()
            logger.error(f"Migration failed: {e}")
            return False
            
    def migrate(self, target_version=None):
        """
        Run all needed migrations to reach the target version.
        
        Args:
            target_version (str, optional): Target version to migrate to.
                If None, migrate to the latest version.
                
        Returns:
            bool: True if all migrations were successful, False otherwise
        """
        if not self.connect():
            return False
            
        if not self.ensure_version_table():
            self.close()
            return False
            
        current_version = self.get_current_version()
        if current_version is None:
            self.close()
            return False
            
        migrations = self.get_available_migrations()
        if not migrations:
            logger.info("No migrations found")
            self.close()
            return True
            
        # Filter migrations that need to be applied
        pending_migrations = []
        for version, filepath in migrations:
            if self._compare_versions(version, current_version) > 0:
                if target_version is None or self._compare_versions(version, target_version) <= 0:
                    pending_migrations.append((version, filepath))
                    
        if not pending_migrations:
            logger.info("Database is already at the latest version")
            self.close()
            return True
            
        # Run pending migrations
        success = True
        for version, filepath in pending_migrations:
            if not self.run_migration(filepath):
                success = False
                break
                
        self.close()
        return success
    
    def _compare_versions(self, version1, version2):
        """
        Compare two version strings.
        
        Args:
            version1 (str): First version (e.g., "1.0.0")
            version2 (str): Second version (e.g., "1.1.0")
            
        Returns:
            int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        v1 = [int(x) for x in version1.split('.')]
        v2 = [int(x) for x in version2.split('.')]
        
        # Pad versions to equal length
        while len(v1) < len(v2):
            v1.append(0)
        while len(v2) < len(v1):
            v2.append(0)
            
        # Compare each component
        for i in range(len(v1)):
            if v1[i] < v2[i]:
                return -1
            elif v1[i] > v2[i]:
                return 1
                
        return 0  # Versions are equal

def main():
    """Main entry point for the migration manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Migration Manager for KPI System")
    parser.add_argument("--db", required=True, help="Path to the SQLite database file")
    parser.add_argument("--dir", required=True, help="Directory containing migration scripts")
    parser.add_argument("--target", help="Target version to migrate to (default: latest)")
    
    args = parser.parse_args()
    
    logger.info(f"Starting migration process for database: {args.db}")
    
    manager = MigrationManager(args.db, args.dir)
    success = manager.migrate(args.target)
    
    if success:
        logger.info("Migration completed successfully")
        return 0
    else:
        logger.error("Migration failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
