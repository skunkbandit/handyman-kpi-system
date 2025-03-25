-- KPI System Database Schema

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    tier TEXT CHECK (tier IN ('Apprentice', 'Handyman', 'Craftsman', 'Master Craftsman', 'Lead Craftsman')),
    hire_date DATE,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skill categories table
CREATE TABLE IF NOT EXISTS skill_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skills table
CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES skill_categories(category_id)
);

-- Tool categories table
CREATE TABLE IF NOT EXISTS tool_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tools table
CREATE TABLE IF NOT EXISTS tools (
    tool_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES tool_categories(category_id)
);

-- Evaluations table (to store each evaluation instance)
CREATE TABLE IF NOT EXISTS evaluations (
    evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    evaluator_id INTEGER,
    evaluation_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (evaluator_id) REFERENCES employees(employee_id)
);

-- Skill evaluations table (to store ratings for each skill)
CREATE TABLE IF NOT EXISTS skill_evaluations (
    skill_evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER,
    skill_id INTEGER,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);

-- Tool evaluations table (to store tool proficiency and ownership)
CREATE TABLE IF NOT EXISTS tool_evaluations (
    tool_evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER,
    tool_id INTEGER,
    can_operate BOOLEAN DEFAULT 0,
    owns_tool BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id),
    FOREIGN KEY (tool_id) REFERENCES tools(tool_id)
);

-- Special skills table (for additional skills not in predefined list)
CREATE TABLE IF NOT EXISTS special_skills (
    special_skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER,
    skill_name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(evaluation_id)
);

-- Users table (for authentication and authorization)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    employee_id INTEGER,
    role TEXT NOT NULL CHECK (role IN ('admin', 'manager', 'employee')),
    active BOOLEAN DEFAULT 1,
    force_password_change BOOLEAN DEFAULT 0,
    reset_token TEXT UNIQUE,
    reset_token_expiry TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_skill_evaluations_evaluation_id ON skill_evaluations(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_skill_evaluations_skill_id ON skill_evaluations(skill_id);
CREATE INDEX IF NOT EXISTS idx_tool_evaluations_evaluation_id ON tool_evaluations(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_tool_evaluations_tool_id ON tool_evaluations(tool_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_employee_id ON evaluations(employee_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_date ON evaluations(evaluation_date);
CREATE INDEX IF NOT EXISTS idx_skills_category_id ON skills(category_id);
CREATE INDEX IF NOT EXISTS idx_tools_category_id ON tools(category_id);
CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users(employee_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert initial schema version
INSERT INTO schema_version (version, description) VALUES ('1.1', 'Added enhanced users table for authentication');

-- Initial data for skill categories based on spreadsheet
INSERT OR IGNORE INTO skill_categories (name, display_order) VALUES
('Crawl Space', 1),
('Bathroom/Kitchen/Plumbing', 2),
('Carpentry Exterior/Deck', 3),
('Carpentry Interior', 4),
('Closets', 5),
('Concrete', 6),
('Doors/Windows', 7),
('Drywall', 8),
('Electrical', 9),
('Fencing', 10),
('Flooring', 11),
('Garage/Sheds', 12),
('Hauling/Moving', 13),
('Heating/Cooling', 14),
('Landscaping', 15),
('Maintenance Inside', 16),
('Maintenance Outside', 17),
('Painting/Staining', 18),
('Roofing/Gutters', 19),
('Commercial', 20);

-- Create default admin user if not exists
-- Password: Admin123 (for development only, change in production)
INSERT OR IGNORE INTO users (username, password_hash, role, active) 
VALUES (
    'admin', 
    'pbkdf2:sha256:150000$WEYs6Nq5$ddaf44a07b7f4905d36693aed33c56ca697e2225fbd4a27db779d6188ab18cad', 
    'admin', 
    1
);
