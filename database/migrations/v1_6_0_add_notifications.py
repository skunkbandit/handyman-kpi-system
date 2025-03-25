"""
Migration script v1.6.0 - Add notification system
"""

def upgrade(connection):
    """
    Create tables for notification system
    """
    cursor = connection.cursor()
    
    # Create notification_types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            template TEXT NOT NULL,
            icon TEXT,
            color TEXT,
            is_system BOOLEAN NOT NULL DEFAULT 1
        );
    ''')
    
    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            data JSON,
            is_read BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            read_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (type_id) REFERENCES notification_types (id) ON DELETE CASCADE
        );
    ''')
    
    # Create notification_settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            email_enabled BOOLEAN NOT NULL DEFAULT 1,
            app_enabled BOOLEAN NOT NULL DEFAULT 1,
            UNIQUE(user_id, type_id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (type_id) REFERENCES notification_types (id) ON DELETE CASCADE
        );
    ''')
    
    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
        ON notifications(user_id);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_notifications_type_id 
        ON notifications(type_id);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_notifications_is_read 
        ON notifications(is_read);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_notifications_created_at 
        ON notifications(created_at);
    ''')
    
    # Insert default notification types
    cursor.execute('''
        INSERT INTO notification_types (name, description, template, icon, color)
        VALUES 
        ('evaluation_due', 'Evaluation Due Reminder', 'Evaluation for {{employee_name}} is due on {{due_date}}', 'calendar-check', 'blue'),
        ('evaluation_completed', 'Evaluation Completed', 'Evaluation for {{employee_name}} has been completed', 'file-check', 'green'),
        ('skill_improvement', 'Skill Improvement', '{{employee_name}} has improved in {{skill_name}}', 'trending-up', 'green'),
        ('employee_tier_change', 'Employee Tier Change', '{{employee_name}} has been promoted to {{tier}}', 'award', 'purple'),
        ('report_generated', 'Report Generated', 'Your report "{{report_name}}" has been generated', 'file-text', 'blue'),
        ('account_action', 'Account Action', '{{action}} on your account', 'user', 'orange'),
        ('system_backup', 'System Backup', 'System backup {{status}}', 'database', 'blue'),
        ('system_update', 'System Update', 'System update available: {{version}}', 'refresh-cw', 'orange');
    ''')
    
    # Update schema version
    cursor.execute('''
        INSERT OR REPLACE INTO schema_version (version, updated_at)
        VALUES ('1.6.0', datetime('now'));
    ''')
    
    connection.commit()
    
    return True


def downgrade(connection):
    """
    Remove notification system tables
    """
    cursor = connection.cursor()
    
    # Drop tables
    cursor.execute('DROP TABLE IF EXISTS notification_settings;')
    cursor.execute('DROP TABLE IF EXISTS notifications;')
    cursor.execute('DROP TABLE IF EXISTS notification_types;')
    
    # Update schema version back to previous version
    cursor.execute('''
        INSERT OR REPLACE INTO schema_version (version, updated_at)
        VALUES ('1.5.0', datetime('now'));
    ''')
    
    connection.commit()
    
    return True
