"""\nMigration script v1.4.0 - Add audit logging tables for system changes\n"""\n\ndef upgrade(connection):\n    """\n    Create audit logging tables for tracking system changes\n    """\n    cursor = connection.cursor()\n    \n    # Create audit_log table to track all system changes\n    cursor.execute('''\n        CREATE TABLE IF NOT EXISTS audit_log (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\n            user_id INTEGER,\n            action TEXT NOT NULL,\n            table_name TEXT NOT NULL,\n            record_id INTEGER,\n            details TEXT,\n            ip_address TEXT,\n            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL\n        );\n    ''')\n    \n    # Create index for querying audit logs\n    cursor.execute('''\n        CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp \n        ON audit_log(timestamp);\n    ''')\n    \n    cursor.execute('''\n        CREATE INDEX IF NOT EXISTS idx_audit_log_user_id \n        ON audit_log(user_id);\n    ''')\n    \n    cursor.execute('''\n        CREATE INDEX IF NOT EXISTS idx_audit_log_action \n        ON audit_log(action);\n    ''')\n    \n    cursor.execute('''\n        CREATE INDEX IF NOT EXISTS idx_audit_log_table_record \n        ON audit_log(table_name, record_id);\n    ''')\n    \n    # Create login_history table to track authentication\n    cursor.execute('''\n        CREATE TABLE IF NOT EXISTS login_history (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            user_id INTEGER,\n            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\n            action TEXT NOT NULL,  -- 'LOGIN', 'LOGOUT', 'FAILED_LOGIN'\n            ip_address TEXT,\n            user_agent TEXT,\n            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL\n        );\n    ''')\n    \n    # Create index for login history\n    cursor.execute('''\n        CREATE INDEX IF NOT EXISTS idx_login_history_user_id \n        ON login_history(user_id);\n    ''')\n    \n    cursor.execute('''\n        CREATE INDEX IF NOT EXISTS idx_login_history_timestamp \n        ON login_history(timestamp);\n    ''')\n    \n    cursor.execute('''\n        CREATE INDEX IF NOT EXISTS idx_login_history_action \n        ON login_history(action);\n    ''')\n    \n    # Add role column to users table if not exists\n    cursor.execute('''\n        PRAGMA table_info(users);\n    ''')\n    columns = cursor.fetchall()\n    column_names = [column[1] for column in columns]\n    \n    if 'last_login' not in column_names:\n        cursor.execute('''\n            ALTER TABLE users ADD COLUMN last_login DATETIME;\n        ''')\n    \n    if 'login_count' not in column_names:\n        cursor.execute('''\n            ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0;\n        ''')\n    \n    # Update schema version\n    cursor.execute('''\n        INSERT OR REPLACE INTO schema_version (version, updated_at)\n        VALUES ('1.4.0', datetime('now'));\n    ''')\n    \n    connection.commit()\n    \n    return True\n\n\ndef downgrade(connection):\n    """\n    Remove audit logging tables\n    """\n    cursor = connection.cursor()\n    \n    # Drop tables and indexes\n    cursor.execute('DROP TABLE IF EXISTS audit_log;')\n    cursor.execute('DROP TABLE IF EXISTS login_history;')\n    \n    # Update schema version back to previous version\n    cursor.execute('''\n        INSERT OR REPLACE INTO schema_version (version, updated_at)\n        VALUES ('1.3.0', datetime('now'));\n    ''')\n    \n    connection.commit()\n    \n    return True