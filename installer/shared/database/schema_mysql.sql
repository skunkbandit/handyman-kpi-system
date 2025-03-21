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