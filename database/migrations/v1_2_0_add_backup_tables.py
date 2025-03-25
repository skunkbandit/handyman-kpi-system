"""
Add database backup management tables.

This migration adds tables for tracking database backups and restores.
"""

version = "1.2.0"
description = "Add backup management tables"

def upgrade(conn):
    """
    Upgrade the database to this version.
    
    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()
    
    # Create backups table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL UNIQUE,
        description TEXT,
        size_bytes INTEGER,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        db_version TEXT,  -- Database schema version at backup time
        is_automatic BOOLEAN DEFAULT 0,
        checksum TEXT,   -- For integrity verification
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Create restore_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restore_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        backup_id INTEGER,
        performed_by INTEGER,
        performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL,  -- 'success', 'failed'
        error_message TEXT,
        pre_restore_backup TEXT,  -- Filename of automatic backup before restore
        FOREIGN KEY (backup_id) REFERENCES backups(id) ON DELETE SET NULL,
        FOREIGN KEY (performed_by) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Create backup_schedule table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backup_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_type TEXT NOT NULL,  -- 'daily', 'weekly', 'monthly'
        day_of_week INTEGER,  -- 0=Sunday, 6=Saturday (for weekly)
        day_of_month INTEGER,  -- 1-31 (for monthly)
        time_of_day TEXT,  -- HH:MM format
        retention_count INTEGER DEFAULT 5,  -- Number of backups to keep
        is_active BOOLEAN DEFAULT 1,
        last_run TIMESTAMP,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Insert default backup schedule
    cursor.execute('''
    INSERT OR IGNORE INTO backup_schedule 
    (schedule_type, day_of_week, day_of_month, time_of_day, retention_count, is_active)
    VALUES ('daily', NULL, NULL, '00:00', 7, 1)
    ''')
    
    # Insert default system settings for backup location
    cursor.execute('''
    INSERT OR IGNORE INTO system_settings (key, value, data_type, description)
    VALUES ('backup_directory', './backups', 'string', 'Directory where database backups are stored')
    ''')
