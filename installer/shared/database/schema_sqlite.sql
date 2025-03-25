-- SQLite schema for Handyman KPI System

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    email TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employee tiers
CREATE TABLE IF NOT EXISTS employee_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    rank INTEGER NOT NULL
);

-- Insert default employee tiers
INSERT OR IGNORE INTO employee_tiers (name, description, rank) VALUES
    ('Apprentice', 'Entry-level handyman in training', 1),
    ('Handyman', 'Basic handyman with core skills', 2),
    ('Craftsman', 'Skilled handyman with specialized expertise', 3),
    ('Master Craftsman', 'Expert handyman with advanced skills', 4),
    ('Lead Craftsman', 'Senior handyman who can lead teams', 5);

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    employee_number TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    hire_date DATE NOT NULL,
    tier_id INTEGER NOT NULL,
    manager_id INTEGER,
    active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (tier_id) REFERENCES employee_tiers (id),
    FOREIGN KEY (manager_id) REFERENCES employees (id)
);

-- KPI Categories table
CREATE TABLE IF NOT EXISTS kpi_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Insert default KPI categories
INSERT OR IGNORE INTO kpi_categories (name, description) VALUES
    ('Quality', 'Quality of work performed'),
    ('Efficiency', 'Efficiency and speed of work'),
    ('Customer Satisfaction', 'Feedback from customers'),
    ('Safety', 'Adherence to safety protocols'),
    ('Teamwork', 'Collaboration with other employees');

-- KPI Metrics table
CREATE TABLE IF NOT EXISTS kpi_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    unit TEXT,
    target_value REAL,
    min_value REAL,
    max_value REAL,
    weight INTEGER DEFAULT 1,
    tier_specific BOOLEAN DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES kpi_categories (id),
    UNIQUE (category_id, name)
);

-- Insert default KPI metrics
INSERT OR IGNORE INTO kpi_metrics (category_id, name, description, unit, target_value, min_value, max_value, weight) VALUES
    (1, 'Rework Rate', 'Percentage of jobs requiring rework', '%', 5, 0, 100, 2),
    (1, 'Inspection Pass Rate', 'Percentage of inspections passed on first attempt', '%', 95, 0, 100, 2),
    (2, 'Jobs Completed', 'Number of jobs completed per month', 'jobs', 20, 0, 100, 1),
    (2, 'Average Completion Time', 'Average time to complete standard jobs', 'hours', 4, 0, 24, 1),
    (3, 'Customer Rating', 'Average customer satisfaction rating', 'rating', 4.5, 1, 5, 3),
    (3, 'Complaint Rate', 'Percentage of jobs with customer complaints', '%', 2, 0, 100, 2),
    (4, 'Safety Incidents', 'Number of safety incidents', 'incidents', 0, 0, 10, 3),
    (4, 'Safety Compliance', 'Compliance with safety protocols', '%', 100, 0, 100, 2),
    (5, 'Team Contribution', 'Contribution to team goals', 'rating', 4, 1, 5, 1),
    (5, 'Knowledge Sharing', 'Sharing of knowledge with team members', 'rating', 4, 1, 5, 1);

-- Tier-specific KPI metrics (requirements vary by tier)
CREATE TABLE IF NOT EXISTS tier_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tier_id INTEGER NOT NULL,
    metric_id INTEGER NOT NULL,
    target_value REAL,
    weight INTEGER DEFAULT 1,
    FOREIGN KEY (tier_id) REFERENCES employee_tiers (id),
    FOREIGN KEY (metric_id) REFERENCES kpi_metrics (id),
    UNIQUE (tier_id, metric_id)
);

-- Insert tier-specific metrics
INSERT OR IGNORE INTO tier_metrics (tier_id, metric_id, target_value, weight) VALUES
    -- Apprentice
    (1, 3, 15, 1),  -- Jobs Completed: 15 for Apprentice
    (1, 4, 6, 1),   -- Average Completion Time: 6 hours for Apprentice
    
    -- Handyman
    (2, 3, 20, 1),  -- Jobs Completed: 20 for Handyman
    (2, 4, 4, 1),   -- Average Completion Time: 4 hours for Handyman
    
    -- Craftsman
    (3, 3, 25, 1),  -- Jobs Completed: 25 for Craftsman
    (3, 4, 3, 1),   -- Average Completion Time: 3 hours for Craftsman
    
    -- Master Craftsman
    (4, 3, 30, 1),  -- Jobs Completed: 30 for Master Craftsman
    (4, 4, 2.5, 1), -- Average Completion Time: 2.5 hours for Master Craftsman
    
    -- Lead Craftsman
    (5, 3, 20, 1),  -- Jobs Completed: 20 for Lead Craftsman (fewer due to leadership duties)
    (5, 4, 2, 1);   -- Average Completion Time: 2 hours for Lead Craftsman

-- Employee KPI Entries
CREATE TABLE IF NOT EXISTS employee_kpi_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    metric_id INTEGER NOT NULL,
    entry_date DATE NOT NULL,
    value REAL NOT NULL,
    notes TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees (id),
    FOREIGN KEY (metric_id) REFERENCES kpi_metrics (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- Employee Performance Reviews
CREATE TABLE IF NOT EXISTS performance_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    review_date DATE NOT NULL,
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    overall_rating REAL NOT NULL,
    strengths TEXT,
    areas_for_improvement TEXT,
    goals TEXT,
    reviewer_id INTEGER NOT NULL,
    status TEXT NOT NULL, -- 'draft', 'submitted', 'approved', 'acknowledged'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees (id),
    FOREIGN KEY (reviewer_id) REFERENCES users (id)
);

-- Review KPI Scores
CREATE TABLE IF NOT EXISTS review_kpi_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    metric_id INTEGER NOT NULL,
    score REAL NOT NULL,
    weight REAL NOT NULL,
    weighted_score REAL NOT NULL,
    comments TEXT,
    FOREIGN KEY (review_id) REFERENCES performance_reviews (id),
    FOREIGN KEY (metric_id) REFERENCES kpi_metrics (id),
    UNIQUE (review_id, metric_id)
);

-- System Settings
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT OR IGNORE INTO settings (key, value, description) VALUES
    ('company_name', 'Handyman Service Company', 'Company name'),
    ('review_period', 'quarterly', 'Performance review frequency'),
    ('kpi_entry_frequency', 'monthly', 'Frequency of KPI data entry'),
    ('enable_employee_login', 'true', 'Allow employees to log in and view their KPIs'),
    ('enable_manager_review', 'true', 'Require manager review of KPI entries');

-- Activity Log
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_employee_tier ON employees (tier_id);
CREATE INDEX IF NOT EXISTS idx_employee_manager ON employees (manager_id);
CREATE INDEX IF NOT EXISTS idx_kpi_metric_category ON kpi_metrics (category_id);
CREATE INDEX IF NOT EXISTS idx_tier_metric_tier ON tier_metrics (tier_id);
CREATE INDEX IF NOT EXISTS idx_tier_metric_metric ON tier_metrics (metric_id);
CREATE INDEX IF NOT EXISTS idx_employee_kpi_entry_employee ON employee_kpi_entries (employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_kpi_entry_metric ON employee_kpi_entries (metric_id);
CREATE INDEX IF NOT EXISTS idx_employee_kpi_entry_date ON employee_kpi_entries (entry_date);
CREATE INDEX IF NOT EXISTS idx_performance_review_employee ON performance_reviews (employee_id);
CREATE INDEX IF NOT EXISTS idx_performance_review_date ON performance_reviews (review_date);
CREATE INDEX IF NOT EXISTS idx_review_kpi_score_review ON review_kpi_scores (review_id);
CREATE INDEX IF NOT EXISTS idx_review_kpi_score_metric ON review_kpi_scores (metric_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log (user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_action ON activity_log (action);