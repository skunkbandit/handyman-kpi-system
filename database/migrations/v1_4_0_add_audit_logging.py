"""
Migration script v1.4.0 - Add audit logging tables for system changes
"""

def upgrade(connection):
    """
    Create audit logging tables for tracking system changes
    """
    cursor = connection.cursor()
    
    # Create audit_log table to track all system changes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            action TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id INTEGER,
            details TEXT,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        );
    ''')
    
    # Create index for querying audit logs
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp 
        ON audit_log(timestamp);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_log_user_id 
        ON audit_log(user_id);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_log_action 
        ON audit_log(action);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_audit_log_table_record 
        ON audit_log(table_name, record_id);
    ''')
    
    # Create login_history table to track authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,  -- 'LOGIN', 'LOGOUT', 'FAILED_LOGIN'
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        );
    ''')
    
    # Create index for login history
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_login_history_user_id 
        ON login_history(user_id);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_login_history_timestamp 
        ON login_history(timestamp);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_login_history_action 
        ON login_history(action);
    ''')
    
    # Add role column to users table if not exists
    cursor.execute('''
        PRAGMA table_info(users);
    ''')
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'last_login' not in column_names:
        cursor.execute('''
            ALTER TABLE users ADD COLUMN last_login DATETIME;
        ''')
    
    if 'login_count' not in column_names:
        cursor.execute('''
            ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0;
        ''')
    
    # Update schema version
    cursor.execute('''
        INSERT OR REPLACE INTO schema_version (version, updated_at)
        VALUES ('1.4.0', datetime('now'));
    ''')
    
    connection.commit()
    
    return True


def downgrade(connection):
    """
    Remove audit logging tables
    """
    cursor = connection.cursor()
    
    # Drop tables and indexes
    cursor.execute('DROP TABLE IF EXISTS audit_log;')
    cursor.execute('DROP TABLE IF EXISTS login_history;')
    
    # Update schema version back to previous version
    cursor.execute('''
        INSERT OR REPLACE INTO schema_version (version, updated_at)
        VALUES ('1.3.0', datetime('now'));
    ''')
    
    connection.commit()
    
    return True
