"""
Initial database schema for KPI System.

This migration creates all the tables needed for the KPI system based on the
handyman business requirements and the grading schema from the spreadsheet.
"""

version = "1.0.0"
description = "Initial database schema"

def upgrade(conn):
    """
    Upgrade the database to this version.
    
    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE,
        full_name TEXT,
        role TEXT DEFAULT 'employee',
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        password_reset_token TEXT,
        password_reset_expires TIMESTAMP
    )
    ''')
    
    # Create employees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        hire_date DATE,
        tier TEXT CHECK (tier IN ('apprentice', 'handyman', 'craftsman', 'master_craftsman', 'lead_craftsman')),
        status TEXT DEFAULT 'active',
        user_id INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Create skill_categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skill_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        weight REAL DEFAULT 1.0,
        tier_requirement TEXT,
        display_order INTEGER
    )
    ''')
    
    # Create skills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        weight REAL DEFAULT 1.0,
        tier_requirement TEXT,
        display_order INTEGER,
        FOREIGN KEY (category_id) REFERENCES skill_categories(id) ON DELETE CASCADE,
        UNIQUE (category_id, name)
    )
    ''')
    
    # Create tool_categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tool_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        weight REAL DEFAULT 1.0,
        tier_requirement TEXT,
        display_order INTEGER
    )
    ''')
    
    # Create tools table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        weight REAL DEFAULT 1.0,
        tier_requirement TEXT,
        display_order INTEGER,
        FOREIGN KEY (category_id) REFERENCES tool_categories(id) ON DELETE CASCADE,
        UNIQUE (category_id, name)
    )
    ''')
    
    # Create evaluations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        evaluator_id INTEGER NOT NULL,
        evaluation_date DATE NOT NULL,
        tier_at_evaluation TEXT NOT NULL,
        comments TEXT,
        overall_score REAL,
        status TEXT DEFAULT 'draft',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
        FOREIGN KEY (evaluator_id) REFERENCES users(id) ON DELETE RESTRICT
    )
    ''')
    
    # Create eval_skills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS eval_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER NOT NULL,
        skill_id INTEGER NOT NULL,
        rating INTEGER CHECK (rating >= 0 AND rating <= 5),
        comments TEXT,
        FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
        UNIQUE (evaluation_id, skill_id)
    )
    ''')
    
    # Create eval_tools table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS eval_tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER NOT NULL,
        tool_id INTEGER NOT NULL,
        rating INTEGER CHECK (rating >= 0 AND rating <= 5),
        comments TEXT,
        FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE,
        FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE,
        UNIQUE (evaluation_id, tool_id)
    )
    ''')
    
    # Create special_skills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS special_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        acquired_date DATE,
        certification TEXT,
        expires_date DATE,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    )
    ''')
    
    # Create system_settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL UNIQUE,
        value TEXT,
        data_type TEXT DEFAULT 'string',
        description TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create system_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        level TEXT NOT NULL,
        message TEXT NOT NULL,
        user_id INTEGER,
        ip_address TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Create needed indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_tier ON employees(tier)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_evaluations_employee ON evaluations(employee_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_evaluations_date ON evaluations(evaluation_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_eval_skills_evaluation ON eval_skills(evaluation_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_eval_tools_evaluation ON eval_tools(evaluation_id)')
    
    # Insert default admin user (password: admin123)
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password_hash, email, full_name, role)
    VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'pbkdf2:sha256:150000$vqH9RQIL$90ed91f399000f10815c198b92057e851dc90cbdee35b3f74dfe38b46c145971', 
          'admin@example.com', 'System Administrator', 'admin'))