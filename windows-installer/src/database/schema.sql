-- KPI System Database Schema

-- Schema version tracking
CREATE TABLE schema_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert initial schema version
INSERT INTO schema_version (version, description) VALUES ('1.0.0', 'Initial schema creation');

-- Employee information
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone_number TEXT,
    tier_level INTEGER NOT NULL, -- 1: Apprentice, 2: Handyman, 3: Craftsman, 4: Master Craftsman, 5: Lead Craftsman
    hire_date DATE,
    active INTEGER NOT NULL DEFAULT 1, -- Boolean for active/inactive status
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skill categories
CREATE TABLE skill_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    display_order INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skills within categories
CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES skill_categories(id)
);

-- Tool categories
CREATE TABLE tool_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    display_order INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tools within categories
CREATE TABLE tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES tool_categories(id)
);

-- Evaluation records
CREATE TABLE evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    evaluation_date DATE NOT NULL,
    evaluator_id INTEGER, -- NULL if self-evaluation
    evaluation_type TEXT NOT NULL, -- 'self' or 'manager'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (evaluator_id) REFERENCES employees(id)
);

-- Skill ratings within evaluations
CREATE TABLE eval_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    rating INTEGER NOT NULL, -- 1-5 scale
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

-- Tool proficiency within evaluations
CREATE TABLE eval_tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id INTEGER NOT NULL,
    tool_id INTEGER NOT NULL,
    can_operate INTEGER NOT NULL DEFAULT 0, -- Boolean
    truck_stock INTEGER NOT NULL DEFAULT 0, -- Boolean
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id),
    FOREIGN KEY (tool_id) REFERENCES tools(id)
);

-- Special skills outside standard evaluation
CREATE TABLE special_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    description TEXT,
    acquired_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- System users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    employee_id INTEGER,
    role TEXT NOT NULL, -- 'admin', 'manager', 'employee'
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Create indexes for improved query performance
CREATE INDEX idx_evaluations_employee_id ON evaluations(employee_id);
CREATE INDEX idx_evaluations_date ON evaluations(evaluation_date);
CREATE INDEX idx_eval_skills_evaluation_id ON eval_skills(evaluation_id);
CREATE INDEX idx_eval_skills_skill_id ON eval_skills(skill_id);
CREATE INDEX idx_eval_tools_evaluation_id ON eval_tools(evaluation_id);
CREATE INDEX idx_eval_tools_tool_id ON eval_tools(tool_id);
CREATE INDEX idx_skills_category_id ON skills(category_id);
CREATE INDEX idx_tools_category_id ON tools(category_id);
