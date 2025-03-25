"""
Migration script v1.5.0 - Add report and data export settings
"""

def upgrade(connection):
    """
    Create tables for configuring reports and data exports
    """
    cursor = connection.cursor()
    
    # Create report_templates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            template_type TEXT NOT NULL,
            config JSON NOT NULL,
            is_system BOOLEAN NOT NULL DEFAULT 0,
            created_by INTEGER,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
        );
    ''')
    
    # Create scheduled_exports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_exports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            report_template_id INTEGER NOT NULL,
            schedule TEXT NOT NULL,  -- cron expression
            file_format TEXT NOT NULL,  -- 'PDF', 'EXCEL', 'CSV'
            parameters JSON,
            last_run DATETIME,
            next_run DATETIME,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_by INTEGER,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_template_id) REFERENCES report_templates (id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
        );
    ''')
    
    # Create export_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS export_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scheduled_export_id INTEGER,
            report_template_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            export_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,  -- 'SUCCESS', 'FAILED'
            error_message TEXT,
            user_id INTEGER,
            FOREIGN KEY (scheduled_export_id) REFERENCES scheduled_exports (id) ON DELETE SET NULL,
            FOREIGN KEY (report_template_id) REFERENCES report_templates (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        );
    ''')
    
    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_report_templates_type 
        ON report_templates(template_type);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_scheduled_exports_active 
        ON scheduled_exports(is_active);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_scheduled_exports_next_run 
        ON scheduled_exports(next_run);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_export_history_time 
        ON export_history(export_time);
    ''')
    
    # Insert default system report templates
    cursor.execute('''
        INSERT INTO report_templates (name, description, template_type, config, is_system)
        VALUES 
        ('Employee Performance', 'Standard employee performance report', 'EMPLOYEE', 
         '{"sections": ["personal_info", "skill_ratings", "tool_proficiency", "progress_chart", "goals"], "chart_types": ["radar", "line"]}', 1),
        ('Team Performance', 'Team-wide performance metrics', 'TEAM', 
         '{"sections": ["team_overview", "skill_distribution", "improvement_areas", "top_performers"], "chart_types": ["bar", "radar", "heatmap"]}', 1),
        ('Skill Analysis', 'Detailed skill distribution analysis', 'SKILL', 
         '{"sections": ["skill_overview", "category_breakdown", "tier_comparison", "training_needs"], "chart_types": ["bar", "pie", "line"]}', 1),
        ('Tool Inventory', 'Tool proficiency and ownership report', 'TOOL', 
         '{"sections": ["tool_overview", "category_breakdown", "ownership_stats", "training_needs"], "chart_types": ["bar", "pie"]}', 1);
    ''')
    
    # Update schema version
    cursor.execute('''
        INSERT OR REPLACE INTO schema_version (version, updated_at)
        VALUES ('1.5.0', datetime('now'));
    ''')
    
    connection.commit()
    
    return True


def downgrade(connection):
    """
    Remove report and data export settings tables
    """
    cursor = connection.cursor()
    
    # Drop tables
    cursor.execute('DROP TABLE IF EXISTS export_history;')
    cursor.execute('DROP TABLE IF EXISTS scheduled_exports;')
    cursor.execute('DROP TABLE IF EXISTS report_templates;')
    
    # Update schema version back to previous version
    cursor.execute('''
        INSERT OR REPLACE INTO schema_version (version, updated_at)
        VALUES ('1.4.0', datetime('now'));
    ''')
    
    connection.commit()
    
    return True
