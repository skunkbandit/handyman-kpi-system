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