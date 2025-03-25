-- PostgreSQL schema for Handyman KPI System

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employee tiers
CREATE TABLE IF NOT EXISTS employee_tiers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    rank INTEGER NOT NULL
);

-- Insert default employee tiers
INSERT INTO employee_tiers (name, description, rank)
VALUES
    ('Apprentice', 'Entry-level handyman in training', 1),
    ('Handyman', 'Basic handyman with core skills', 2),
    ('Craftsman', 'Skilled handyman with specialized expertise', 3),
    ('Master Craftsman', 'Expert handyman with advanced skills', 4),
    ('Lead Craftsman', 'Senior handyman who can lead teams', 5)
ON CONFLICT (name) DO NOTHING;

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    employee_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    hire_date DATE NOT NULL,
    tier_id INTEGER NOT NULL REFERENCES employee_tiers(id) ON DELETE RESTRICT,
    manager_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

-- KPI Categories table
CREATE TABLE IF NOT EXISTS kpi_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT
);

-- Insert default KPI categories
INSERT INTO kpi_categories (name, description)
VALUES
    ('Quality', 'Quality of work performed'),
    ('Efficiency', 'Efficiency and speed of work'),
    ('Customer Satisfaction', 'Feedback from customers'),
    ('Safety', 'Adherence to safety protocols'),
    ('Teamwork', 'Collaboration with other employees')
ON CONFLICT (name) DO NOTHING;

-- KPI Metrics table
CREATE TABLE IF NOT EXISTS kpi_metrics (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES kpi_categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    unit VARCHAR(50),
    target_value REAL,
    min_value REAL,
    max_value REAL,
    weight INTEGER DEFAULT 1,
    tier_specific BOOLEAN DEFAULT FALSE,
    UNIQUE (category_id, name)
);

-- Insert default KPI metrics
INSERT INTO kpi_metrics (category_id, name, description, unit, target_value, min_value, max_value, weight)
VALUES
    (1, 'Rework Rate', 'Percentage of jobs requiring rework', '%', 5, 0, 100, 2),
    (1, 'Inspection Pass Rate', 'Percentage of inspections passed on first attempt', '%', 95, 0, 100, 2),
    (2, 'Jobs Completed', 'Number of jobs completed per month', 'jobs', 20, 0, 100, 1),
    (2, 'Average Completion Time', 'Average time to complete standard jobs', 'hours', 4, 0, 24, 1),
    (3, 'Customer Rating', 'Average customer satisfaction rating', 'rating', 4.5, 1, 5, 3),
    (3, 'Complaint Rate', 'Percentage of jobs with customer complaints', '%', 2, 0, 100, 2),
    (4, 'Safety Incidents', 'Number of safety incidents', 'incidents', 0, 0, 10, 3),
    (4, 'Safety Compliance', 'Compliance with safety protocols', '%', 100, 0, 100, 2),
    (5, 'Team Contribution', 'Contribution to team goals', 'rating', 4, 1, 5, 1),
    (5, 'Knowledge Sharing', 'Sharing of knowledge with team members', 'rating', 4, 1, 5, 1)
ON CONFLICT (category_id, name) DO NOTHING;

-- Tier-specific KPI metrics (requirements vary by tier)
CREATE TABLE IF NOT EXISTS tier_metrics (
    id SERIAL PRIMARY KEY,
    tier_id INTEGER NOT NULL REFERENCES employee_tiers(id) ON DELETE CASCADE,
    metric_id INTEGER NOT NULL REFERENCES kpi_metrics(id) ON DELETE CASCADE,
    target_value REAL,
    weight INTEGER DEFAULT 1,
    UNIQUE (tier_id, metric_id)
);

-- Insert tier-specific metrics
INSERT INTO tier_metrics (tier_id, metric_id, target_value, weight)
VALUES
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
    (5, 4, 2, 1)   -- Average Completion Time: 2 hours for Lead Craftsman
ON CONFLICT (tier_id, metric_id) DO NOTHING;

-- Employee KPI Entries
CREATE TABLE IF NOT EXISTS employee_kpi_entries (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    metric_id INTEGER NOT NULL REFERENCES kpi_metrics(id) ON DELETE CASCADE,
    entry_date DATE NOT NULL,
    value REAL NOT NULL,
    notes TEXT,
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employee Performance Reviews
CREATE TABLE IF NOT EXISTS performance_reviews (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    review_date DATE NOT NULL,
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    overall_rating REAL NOT NULL,
    strengths TEXT,
    areas_for_improvement TEXT,
    goals TEXT,
    reviewer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status VARCHAR(50) NOT NULL, -- 'draft', 'submitted', 'approved', 'acknowledged'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Review KPI Scores
CREATE TABLE IF NOT EXISTS review_kpi_scores (
    id SERIAL PRIMARY KEY,
    review_id INTEGER NOT NULL REFERENCES performance_reviews(id) ON DELETE CASCADE,
    metric_id INTEGER NOT NULL REFERENCES kpi_metrics(id) ON DELETE CASCADE,
    score REAL NOT NULL,
    weight REAL NOT NULL,
    weighted_score REAL NOT NULL,
    comments TEXT,
    UNIQUE (review_id, metric_id)
);

-- System Settings
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT INTO settings (key, value, description)
VALUES
    ('company_name', 'Handyman Service Company', 'Company name'),
    ('review_period', 'quarterly', 'Performance review frequency'),
    ('kpi_entry_frequency', 'monthly', 'Frequency of KPI data entry'),
    ('enable_employee_login', 'true', 'Allow employees to log in and view their KPIs'),
    ('enable_manager_review', 'true', 'Require manager review of KPI entries')
ON CONFLICT (key) DO NOTHING;

-- Activity Log
CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(255),
    entity_id INTEGER,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

-- Function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Triggers for updating timestamps
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_performance_reviews_updated_at
BEFORE UPDATE ON performance_reviews
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_settings_updated_at
BEFORE UPDATE ON settings
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();
