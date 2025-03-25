-- MySQL schema for Handyman KPI System

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Employee tiers
CREATE TABLE IF NOT EXISTS employee_tiers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    rank INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default employee tiers
INSERT IGNORE INTO employee_tiers (name, description, rank) VALUES
    ('Apprentice', 'Entry-level handyman in training', 1),
    ('Handyman', 'Basic handyman with core skills', 2),
    ('Craftsman', 'Skilled handyman with specialized expertise', 3),
    ('Master Craftsman', 'Expert handyman with advanced skills', 4),
    ('Lead Craftsman', 'Senior handyman who can lead teams', 5);

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    employee_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    hire_date DATE NOT NULL,
    tier_id INT NOT NULL,
    manager_id INT,
    active BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
    FOREIGN KEY (tier_id) REFERENCES employee_tiers (id) ON DELETE RESTRICT,
    FOREIGN KEY (manager_id) REFERENCES employees (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- KPI Categories table
CREATE TABLE IF NOT EXISTS kpi_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default KPI categories
INSERT IGNORE INTO kpi_categories (name, description) VALUES
    ('Quality', 'Quality of work performed'),
    ('Efficiency', 'Efficiency and speed of work'),
    ('Customer Satisfaction', 'Feedback from customers'),
    ('Safety', 'Adherence to safety protocols'),
    ('Teamwork', 'Collaboration with other employees');

-- KPI Metrics table
CREATE TABLE IF NOT EXISTS kpi_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    unit VARCHAR(50),
    target_value FLOAT,
    min_value FLOAT,
    max_value FLOAT,
    weight INT DEFAULT 1,
    tier_specific BOOLEAN DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES kpi_categories (id) ON DELETE CASCADE,
    UNIQUE KEY (category_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default KPI metrics
INSERT IGNORE INTO kpi_metrics (category_id, name, description, unit, target_value, min_value, max_value, weight) VALUES
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
    id INT AUTO_INCREMENT PRIMARY KEY,
    tier_id INT NOT NULL,
    metric_id INT NOT NULL,
    target_value FLOAT,
    weight INT DEFAULT 1,
    FOREIGN KEY (tier_id) REFERENCES employee_tiers (id) ON DELETE CASCADE,
    FOREIGN KEY (metric_id) REFERENCES kpi_metrics (id) ON DELETE CASCADE,
    UNIQUE KEY (tier_id, metric_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert tier-specific metrics
INSERT IGNORE INTO tier_metrics (tier_id, metric_id, target_value, weight) VALUES
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
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    metric_id INT NOT NULL,
    entry_date DATE NOT NULL,
    value FLOAT NOT NULL,
    notes TEXT,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE,
    FOREIGN KEY (metric_id) REFERENCES kpi_metrics (id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Employee Performance Reviews
CREATE TABLE IF NOT EXISTS performance_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    review_date DATE NOT NULL,
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    overall_rating FLOAT NOT NULL,
    strengths TEXT,
    areas_for_improvement TEXT,
    goals TEXT,
    reviewer_id INT NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'draft', 'submitted', 'approved', 'acknowledged'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Review KPI Scores
CREATE TABLE IF NOT EXISTS review_kpi_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    metric_id INT NOT NULL,
    score FLOAT NOT NULL,
    weight FLOAT NOT NULL,
    weighted_score FLOAT NOT NULL,
    comments TEXT,
    FOREIGN KEY (review_id) REFERENCES performance_reviews (id) ON DELETE CASCADE,
    FOREIGN KEY (metric_id) REFERENCES kpi_metrics (id) ON DELETE CASCADE,
    UNIQUE KEY (review_id, metric_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- System Settings
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default settings
INSERT IGNORE INTO settings (`key`, value, description) VALUES
    ('company_name', 'Handyman Service Company', 'Company name'),
    ('review_period', 'quarterly', 'Performance review frequency'),
    ('kpi_entry_frequency', 'monthly', 'Frequency of KPI data entry'),
    ('enable_employee_login', 'true', 'Allow employees to log in and view their KPIs'),
    ('enable_manager_review', 'true', 'Require manager review of KPI entries');

-- Activity Log
CREATE TABLE IF NOT EXISTS activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(255),
    entity_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create indexes for performance
CREATE INDEX idx_employee_tier ON employees (tier_id);
CREATE INDEX idx_employee_manager ON employees (manager_id);
CREATE INDEX idx_kpi_metric_category ON kpi_metrics (category_id);
CREATE INDEX idx_tier_metric_tier ON tier_metrics (tier_id);
CREATE INDEX idx_tier_metric_metric ON tier_metrics (metric_id);
CREATE INDEX idx_employee_kpi_entry_employee ON employee_kpi_entries (employee_id);
CREATE INDEX idx_employee_kpi_entry_metric ON employee_kpi_entries (metric_id);
CREATE INDEX idx_employee_kpi_entry_date ON employee_kpi_entries (entry_date);
CREATE INDEX idx_performance_review_employee ON performance_reviews (employee_id);
CREATE INDEX idx_performance_review_date ON performance_reviews (review_date);
CREATE INDEX idx_review_kpi_score_review ON review_kpi_scores (review_id);
CREATE INDEX idx_review_kpi_score_metric ON review_kpi_scores (metric_id);
CREATE INDEX idx_activity_log_user ON activity_log (user_id);
CREATE INDEX idx_activity_log_action ON activity_log (action);
