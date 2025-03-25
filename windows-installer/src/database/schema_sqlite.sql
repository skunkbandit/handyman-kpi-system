-- SQLite schema for Handyman KPI System

-- Schema version tracking
CREATE TABLE schema_version (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial schema version
INSERT INTO schema_version (version) VALUES ('1.0.0');

-- Users table for authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager', 'employee')),
    active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Employees table
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('apprentice', 'handyman', 'craftsman', 'master_craftsman', 'lead_craftsman')),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    hire_date DATE,
    notes TEXT,
    user_id INTEGER,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Skill categories
CREATE TABLE skill_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER NOT NULL DEFAULT 0
);

-- Individual skills within categories
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES skill_categories(id) ON DELETE CASCADE,
    UNIQUE (category_id, name)
);

-- Tool categories
CREATE TABLE tool_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER NOT NULL DEFAULT 0
);

-- Individual tools within categories
CREATE TABLE tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES tool_categories(id) ON DELETE CASCADE,
    UNIQUE (category_id, name)
);

-- Evaluation record
CREATE TABLE evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    evaluator_id INTEGER,
    evaluation_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    FOREIGN KEY (evaluator_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Skill ratings for evaluations
CREATE TABLE eval_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    notes TEXT,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE (evaluation_id, skill_id)
);

-- Tool ratings for evaluations (can operate, has as truck stock)
CREATE TABLE eval_tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    tool_id INTEGER NOT NULL,
    can_operate INTEGER NOT NULL DEFAULT 0,
    has_tool INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE,
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE,
    UNIQUE (evaluation_id, tool_id)
);

-- Special skills (not in standard categories)
CREATE TABLE special_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_employee_tier ON employees(tier);
CREATE INDEX idx_employee_active ON employees(active);
CREATE INDEX idx_evaluations_date ON evaluations(evaluation_date);
CREATE INDEX idx_evaluations_employee ON evaluations(employee_id);
CREATE INDEX idx_eval_skills_rating ON eval_skills(rating);
CREATE INDEX idx_skills_category ON skills(category_id);
CREATE INDEX idx_tools_category ON tools(category_id);
