#!/usr/bin/env python
"""
Main demo data generator script - runs the data generation functions
from generate_demo_data.py and outputs the result to files and/or the database.
"""

import os
import sys
import random
import argparse
import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime

from generate_demo_data import (
    create_employee_data,
    create_skill_data,
    create_tool_data,
    create_evaluations,
    create_special_skills
)

def write_json_files(data, output_dir):
    """Write generated data to JSON files"""
    os.makedirs(output_dir, exist_ok=True)
    
    for name, items in data.items():
        file_path = os.path.join(output_dir, f"{name}.json")
        with open(file_path, 'w') as f:
            json.dump(items, f, indent=2)
        print(f"Created {file_path} with {len(items)} items")

def insert_into_db(data, db_path):
    """Insert generated data into SQLite database"""
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create schema first
    schema_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    if os.path.exists(schema_file):
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)
    else:
        print(f"Warning: Schema file not found at {schema_file}")
        # Create basic tables instead
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            hire_date TEXT NOT NULL,
            tier TEXT NOT NULL,
            area TEXT,
            team TEXT,
            active INTEGER NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS skill_categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        );
        
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES skill_categories (id)
        );
        
        CREATE TABLE IF NOT EXISTS tool_categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        );
        
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES tool_categories (id)
        );
        
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER NOT NULL,
            evaluator_id INTEGER NOT NULL,
            evaluation_date TEXT NOT NULL,
            tier TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (evaluator_id) REFERENCES employees (id)
        );
        
        CREATE TABLE IF NOT EXISTS eval_skills (
            id INTEGER PRIMARY KEY,
            evaluation_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations (id),
            FOREIGN KEY (skill_id) REFERENCES skills (id)
        );
        
        CREATE TABLE IF NOT EXISTS eval_tools (
            id INTEGER PRIMARY KEY,
            evaluation_id INTEGER NOT NULL,
            tool_id INTEGER NOT NULL,
            can_use INTEGER NOT NULL,
            owns INTEGER NOT NULL,
            truck_stock INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (evaluation_id) REFERENCES evaluations (id),
            FOREIGN KEY (tool_id) REFERENCES tools (id)
        );
        
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active INTEGER NOT NULL,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        );
        
        CREATE TABLE IF NOT EXISTS special_skills (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            proficiency INTEGER NOT NULL,
            verified_by INTEGER,
            verification_date TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (verified_by) REFERENCES users (id)
        );
        """)
    
    # Insert data
    for employee in data["employees"]:
        cursor.execute(
            "INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                employee["id"], 
                employee["first_name"], 
                employee["last_name"], 
                employee["email"], 
                employee["phone"], 
                employee["hire_date"], 
                employee["tier"], 
                employee["area"], 
                employee["team"], 
                1 if employee["active"] else 0
            )
        )
    
    for category in data["skill_categories"]:
        cursor.execute(
            "INSERT INTO skill_categories VALUES (?, ?, ?)",
            (category["id"], category["name"], category["description"])
        )
    
    for skill in data["skills"]:
        cursor.execute(
            "INSERT INTO skills VALUES (?, ?, ?, ?)",
            (skill["id"], skill["category_id"], skill["name"], skill["description"])
        )
    
    for category in data["tool_categories"]:
        cursor.execute(
            "INSERT INTO tool_categories VALUES (?, ?, ?)",
            (category["id"], category["name"], category["description"])
        )
    
    for tool in data["tools"]:
        cursor.execute(
            "INSERT INTO tools VALUES (?, ?, ?, ?)",
            (tool["id"], tool["category_id"], tool["name"], tool["description"])
        )
    
    for evaluation in data["evaluations"]:
        cursor.execute(
            "INSERT INTO evaluations VALUES (?, ?, ?, ?, ?, ?)",
            (
                evaluation["id"], 
                evaluation["employee_id"], 
                evaluation["evaluator_id"], 
                evaluation["evaluation_date"], 
                evaluation["tier"], 
                evaluation["notes"]
            )
        )
    
    for eval_skill in data["eval_skills"]:
        cursor.execute(
            "INSERT INTO eval_skills VALUES (?, ?, ?, ?, ?)",
            (
                eval_skill["id"], 
                eval_skill["evaluation_id"], 
                eval_skill["skill_id"], 
                eval_skill["rating"], 
                eval_skill["notes"]
            )
        )
    
    for eval_tool in data["eval_tools"]:
        cursor.execute(
            "INSERT INTO eval_tools VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                eval_tool["id"], 
                eval_tool["evaluation_id"], 
                eval_tool["tool_id"], 
                1 if eval_tool["can_use"] else 0, 
                1 if eval_tool["owns"] else 0, 
                1 if eval_tool["truck_stock"] else 0, 
                eval_tool["notes"]
            )
        )
    
    for user in data["users"]:
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                user["id"], 
                user["username"], 
                user["password_hash"], 
                user["email"], 
                user["first_name"], 
                user["last_name"], 
                user["role"], 
                1 if user["is_active"] else 0,
                user["employee_id"]
            )
        )
    
    for skill in data["special_skills"]:
        cursor.execute(
            "INSERT INTO special_skills VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                skill["id"],
                skill["employee_id"],
                skill["name"],
                skill["description"],
                skill["proficiency"],
                skill["verified_by"],
                skill["verification_date"]
            )
        )
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Data inserted into database: {db_path}")

def create_users_data(employees):
    """Create user accounts for the system"""
    # Hash function for passwords
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    users = [
        # Admin user
        {
            "id": 1,
            "username": "admin",
            "password_hash": hash_password("Admin123!"),
            "email": "admin@example.com",
            "first_name": "System",
            "last_name": "Administrator",
            "role": "admin",
            "is_active": True,
            "employee_id": None
        },
        # Demo users for different roles
        {
            "id": 2,
            "username": "manager",
            "password_hash": hash_password("Manager123!"),
            "email": "manager@example.com",
            "first_name": employees[0]["first_name"],
            "last_name": employees[0]["last_name"],
            "role": "manager",
            "is_active": True,
            "employee_id": 1
        },
        {
            "id": 3,
            "username": "employee",
            "password_hash": hash_password("Employee123!"),
            "email": "employee@example.com",
            "first_name": employees[1]["first_name"],
            "last_name": employees[1]["last_name"],
            "role": "employee",
            "is_active": True,
            "employee_id": 2
        }
    ]
    
    # Create additional users for employees
    next_id = 4
    for i, employee in enumerate(employees[2:], start=3):
        if i % 3 == 0:  # Make some employees into managers
            role = "manager"
        else:
            role = "employee"
            
        users.append({
            "id": next_id,
            "username": f"{employee['first_name'].lower()}{employee['id']}",
            "password_hash": hash_password("Password123!"),
            "email": employee["email"],
            "first_name": employee["first_name"],
            "last_name": employee["last_name"],
            "role": role,
            "is_active": True,
            "employee_id": employee["id"]
        })
        next_id += 1
    
    return users

def main():
    parser = argparse.ArgumentParser(description="Generate sample data for Handyman KPI System demonstrations")
    parser.add_argument("--employees", type=int, default=20, help="Number of employees to generate")
    parser.add_argument("--evaluations", type=int, default=5, help="Average evaluations per employee")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output-dir", type=str, default="demo_data", help="Directory for JSON output")
    parser.add_argument("--db-path", type=str, default="instance/database/demo.db", help="Path for SQLite database")
    parser.add_argument("--json-only", action="store_true", help="Only output JSON, skip database")
    parser.add_argument("--db-only", action="store_true", help="Only output to database, skip JSON")
    
    args = parser.parse_args()
    
    # Set random seed for reproducibility
    random.seed(args.seed)
    
    # Generate all data
    print(f"Generating sample data with {args.employees} employees and ~{args.evaluations} evaluations each...")
    
    # Create employees
    employees = create_employee_data(args.employees)
    print(f"Created {len(employees)} employees")
    
    # Create skills
    skill_categories, skills = create_skill_data()
    print(f"Created {len(skill_categories)} skill categories with {len(skills)} skills")
    
    # Create tools
    tool_categories, tools = create_tool_data()
    print(f"Created {len(tool_categories)} tool categories with {len(tools)} tools")
    
    # Create evaluations
    evaluations, eval_skills, eval_tools = create_evaluations(
        employees, skills, tools, args.evaluations
    )
    print(f"Created {len(evaluations)} evaluations with {len(eval_skills)} skill ratings and {len(eval_tools)} tool ratings")
    
    # Create users
    users = create_users_data(employees)
    print(f"Created {len(users)} user accounts")
    
    # Create special skills
    special_skills = create_special_skills(employees)
    print(f"Created {len(special_skills)} special skills")
    
    # Compile all data
    data = {
        "employees": employees,
        "skill_categories": skill_categories,
        "skills": skills,
        "tool_categories": tool_categories,
        "tools": tools,
        "evaluations": evaluations,
        "eval_skills": eval_skills,
        "eval_tools": eval_tools,
        "users": users,
        "special_skills": special_skills
    }
    
    # Output to JSON files
    if not args.db_only:
        output_dir = os.path.join(os.path.dirname(__file__), args.output_dir)
        write_json_files(data, output_dir)
    
    # Insert into database
    if not args.json_only:
        # Make db_path relative to script directory if not absolute
        if not os.path.isabs(args.db_path):
            db_path = os.path.join(os.path.dirname(__file__), '..', args.db_path)
        else:
            db_path = args.db_path
        
        insert_into_db(data, db_path)
    
    print("Sample data generation complete!")

if __name__ == "__main__":
    main()
