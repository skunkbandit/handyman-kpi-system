#!/usr/bin/env python
"""
Sample Data Generator for Handyman KPI System Demonstrations

This script creates a complete set of sample data for demonstration purposes, including:
- Employees at various tier levels
- Skill categories and skills from the original scorecard
- Tool categories and tools
- Historical evaluations
- User accounts for different roles

Usage:
    python generate_demo_data.py [--employees N] [--evaluations N] [--seed N]

Options:
    --employees N    Number of employees to generate (default: 20)
    --evaluations N  Average evaluations per employee (default: 5)
    --seed N         Random seed for reproducibility (default: 42)
"""

import os
import sys
import random
import datetime
import argparse
import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import timedelta, date

# Constants for data generation
FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"
]

TIERS = [
    "Apprentice", "Handyman", "Craftsman", "Master Craftsman", "Lead Craftsman"
]

AREAS = ["North", "South", "East", "West", "Central"]
TEAMS = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]

PHONE_PREFIXES = ["555-123-", "555-234-", "555-345-", "555-456-", "555-567-"]
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "example.com"]

# Import the skill categories, tool categories, and other constants from separate files
from skill_data import SKILL_CATEGORIES
from tool_data import TOOL_CATEGORIES

def create_employee_data(count):
    """Generate random employee data"""
    employees = []
    for i in range(count):
        tier_index = min(int(random.paretovariate(1.5) - 1), 4)  # Weighted toward lower tiers
        hire_date = date.today() - timedelta(days=random.randint(30, 3650))
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        phone = f"{random.choice(PHONE_PREFIXES)}{random.randint(1000, 9999)}"
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(EMAIL_DOMAINS)}"
        
        employee = {
            "id": i + 1,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "hire_date": hire_date.isoformat(),
            "tier": TIERS[tier_index],
            "area": random.choice(AREAS),
            "team": random.choice(TEAMS),
            "active": True
        }
        employees.append(employee)
    return employees

def create_skill_data():
    """Create skill categories and skills from predefine lists"""
    categories = []
    skills = []
    
    skill_id = 1
    for i, category in enumerate(SKILL_CATEGORIES):
        category_id = i + 1
        categories.append({
            "id": category_id,
            "name": category["name"],
            "description": f"Skills related to {category['name']} work"
        })
        
        for skill_name in category["skills"]:
            skills.append({
                "id": skill_id,
                "category_id": category_id,
                "name": skill_name,
                "description": f"Ability to {skill_name.lower()}"
            })
            skill_id += 1
    
    return categories, skills

def create_tool_data():
    """Create tool categories and tools from predefined lists"""
    categories = []
    tools = []
    
    tool_id = 1
    for i, category in enumerate(TOOL_CATEGORIES):
        category_id = i + 1
        categories.append({
            "id": category_id,
            "name": category["name"],
            "description": f"{category['name']} for various tasks"
        })
        
        for tool_name in category["tools"]:
            tools.append({
                "id": tool_id,
                "category_id": category_id,
                "name": tool_name,
                "description": f"Standard {tool_name.lower()} for professional use"
            })
            tool_id += 1
    
    return categories, tools

def create_evaluations(employees, skills, tools, avg_evals_per_employee):
    """Create random evaluation data for employees"""
    evaluations = []
    eval_skills = []
    eval_tools = []
    
    eval_id = 1
    eval_skill_id = 1
    eval_tool_id = 1
    
    for employee in employees:
        # Tier determines skill level probability distribution
        tier_index = TIERS.index(employee["tier"])
        tier_skill_factor = (tier_index + 1) / 5  # 0.2 to 1.0
        
        # Number of evaluations increases with tier and randomness
        num_evals = max(1, int(avg_evals_per_employee * (0.5 + tier_skill_factor) * random.uniform(0.7, 1.3)))
        
        # Space evaluations over employee's tenure
        hire_date = datetime.date.fromisoformat(employee["hire_date"])
        days_employed = (datetime.date.today() - hire_date).days
        if days_employed < 30:
            days_employed = 30  # Ensure minimum for spacing
        
        for j in range(num_evals):
            # Create evaluation
            eval_date = hire_date + timedelta(days=int(j * days_employed / num_evals))
            
            evaluator_id = random.randint(1, min(5, len(employees)))  # Assuming first few employees are managers
            while evaluator_id == employee["id"]:  # Avoid self-evaluation
                evaluator_id = random.randint(1, min(5, len(employees)))
            
            evaluation = {
                "id": eval_id,
                "employee_id": employee["id"],
                "evaluator_id": evaluator_id,
                "evaluation_date": eval_date.isoformat(),
                "tier": employee["tier"],  # Tier at time of evaluation
                "notes": f"Regular evaluation for {employee['first_name']} {employee['last_name']}"
            }
            evaluations.append(evaluation)
            
            # Create skill evaluations
            skill_subset = random.sample(skills, min(30, len(skills)))  # Evaluate a subset of skills
            for skill in skill_subset:
                # Higher probability of higher scores for higher tiers
                base_probability = tier_skill_factor
                # Category expertise varies by employee
                category_expertise = random.uniform(-0.2, 0.2)
                # Skill improves over time
                time_factor = j / max(1, num_evals - 1) * 0.3
                
                # Calculate probability for each score level
                p = base_probability + category_expertise + time_factor
                p = max(0.1, min(0.9, p))  # Keep between 0.1 and 0.9
                
                # Generate a score with appropriate distribution
                if random.random() < p:
                    # Higher scores more likely
                    score = random.choices([3, 4, 5], weights=[0.3, 0.4, 0.3])[0]
                else:
                    # Lower scores more likely
                    score = random.choices([1, 2, 3], weights=[0.2, 0.5, 0.3])[0]
                
                eval_skills.append({
                    "id": eval_skill_id,
                    "evaluation_id": eval_id,
                    "skill_id": skill["id"],
                    "rating": score,
                    "notes": ""
                })
                eval_skill_id += 1
            
            # Create tool evaluations
            tool_subset = random.sample(tools, min(15, len(tools)))  # Evaluate a subset of tools
            for tool in tool_subset:
                # Higher tier = more likely to use and own tools
                can_use = random.random() < (0.5 + tier_skill_factor * 0.5)
                # More selective about what they own
                owns = can_use and random.random() < (0.3 + tier_skill_factor * 0.4)
                # Even more selective about truck stock
                truck_stock = owns and random.random() < (0.2 + tier_skill_factor * 0.6)
                
                eval_tools.append({
                    "id": eval_tool_id,
                    "evaluation_id": eval_id,
                    "tool_id": tool["id"],
                    "can_use": can_use,
                    "owns": owns,
                    "truck_stock": truck_stock,
                    "notes": ""
                })
                eval_tool_id += 1
            
            eval_id += 1
    
    return evaluations, eval_skills, eval_tools
