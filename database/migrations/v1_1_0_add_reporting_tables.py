"""
Add reporting tables to support the reporting module.

This migration adds tables for storing report templates and generated reports.
"""

version = "1.1.0"
description = "Add reporting tables"

def upgrade(conn):
    """
    Upgrade the database to this version.
    
    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()
    
    # Create report_templates table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS report_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        template_type TEXT NOT NULL,  -- e.g., 'employee_performance', 'team_performance', 'skills_analysis'
        config TEXT NOT NULL,  -- JSON configuration for the report
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_system BOOLEAN DEFAULT 0,  -- Is this a system template or user-created
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Create saved_reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS saved_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        report_type TEXT NOT NULL,
        parameters TEXT,  -- JSON parameters used to generate the report
        data TEXT,  -- JSON data for the report
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        file_path TEXT,  -- Path to saved PDF/Excel file if applicable
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Create report_access table to track who has access to specific reports
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS report_access (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        access_type TEXT DEFAULT 'read',  -- 'read' or 'edit'
        granted_by INTEGER,
        granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES saved_reports(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL,
        UNIQUE (report_id, user_id)
    )
    ''')
    
    # Create scheduled_reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scheduled_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        parameters TEXT,  -- JSON parameters for the report
        schedule TEXT NOT NULL,  -- Cron-style schedule string
        recipients TEXT,  -- JSON array of email addresses
        last_run TIMESTAMP,
        created_by INTEGER,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (template_id) REFERENCES report_templates(id) ON DELETE CASCADE,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Insert default report templates
    default_templates = [
        (
            'Employee Performance', 
            'Individual employee performance report with skill ratings and progress over time',
            'employee_performance',
            '{"sections": ["profile", "skill_ratings", "tool_ratings", "progress_chart", "recommendations"], "charts": true}'
        ),
        (
            'Team Performance', 
            'Comparative analysis of team members with skill distribution',
            'team_performance',
            '{"sections": ["team_summary", "tier_distribution", "skill_comparison", "improvement_areas"], "charts": true}'
        ),
        (
            'Skills Analysis', 
            'Deep dive into skill distribution across the organization',
            'skills_analysis',
            '{"sections": ["skill_summary", "category_breakdown", "tier_analysis", "training_needs"], "charts": true}'
        ),
        (
            'Tool Inventory', 
            'Tool proficiency tracking across employees',
            'tool_inventory',
            '{"sections": ["tool_summary", "proficiency_levels", "acquisition_needs"], "charts": true}'
        )
    ]
    
    for name, description, template_type, config in default_templates:
        cursor.execute(
            '''
            INSERT OR IGNORE INTO report_templates 
            (name, description, template_type, config, is_system)
            VALUES (?, ?, ?, ?, 1)
            ''',
            (name, description, template_type, config)
        )
