#!/usr/bin/env python
"""
Database Seeding Utility

This script populates the database with initial data required for the application.
It seeds essential reference data including skill categories, tool categories, 
user roles, and an admin user.

Usage:
    python -m scripts.seed_database [--reset] [--sample-data] [--admin-password PASSWORD]
    
Options:
    --reset                 : Reset existing data before seeding
    --sample-data           : Include sample employees and evaluations
    --admin-password PASS   : Set a specific admin password (default: from environment or 'admin')
    --verbose               : Show detailed output
"""

import os
import sys
import argparse
import sqlite3
import logging
import datetime
import json
import uuid
import random
from pathlib import Path
from werkzeug.security import generate_password_hash

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Database Seeding Utility')
    parser.add_argument('--reset', action='store_true', help='Reset existing data before seeding')
    parser.add_argument('--sample-data', action='store_true', help='Include sample employees and evaluations')
    parser.add_argument('--admin-password', help='Set admin password (default: from env or "admin")')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    return parser.parse_args()


def setup_logging(verbose=False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger('database_seeding')


def reset_tables(conn, logger, tables):
    """Reset specified tables by deleting all data"""
    cursor = conn.cursor()
    
    # Temporarily disable foreign key constraints
    cursor.execute('PRAGMA foreign_keys = OFF;')
    
    for table in tables:
        try:
            logger.info(f"Resetting table: {table}")
            cursor.execute(f"DELETE FROM {table};")
            # Reset autoincrement counter
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
        except Exception as e:
            logger.error(f"Error resetting table {table}: {str(e)}")
    
    # Re-enable foreign key constraints
    cursor.execute('PRAGMA foreign_keys = ON;')
    conn.commit()


def seed_skill_categories(conn, logger):
    """Seed skill categories based on the Excel template"""
    cursor = conn.cursor()
    
    # Check if categories already exist
    cursor.execute("SELECT COUNT(*) FROM skill_categories;")
    count = cursor.fetchone()[0]
    if count > 0:
        logger.info(f"Found {count} existing skill categories, skipping seed")
        return
    
    # Skill categories from the Excel template
    categories = [
        {'name': 'Crawl space/Skirting', 'description': 'Skills related to crawl spaces and skirting work'},
        {'name': 'Bathroom/Kitchen/Plumbing', 'description': 'Plumbing skills and fixture installation'},
        {'name': 'Carpentry (Exterior/Deck)', 'description': 'External carpentry and deck construction skills'},
        {'name': 'Carpentry (Interior)', 'description': 'Interior carpentry and finishing work'},
        {'name': 'Closets', 'description': 'Custom closet design and installation'},
        {'name': 'Concrete', 'description': 'Concrete mixing, pouring, and finishing'},
        {'name': 'Doors/Windows', 'description': 'Door and window installation and repair'},
        {'name': 'Drywall', 'description': 'Drywall installation, finishing, and repair'},
        {'name': 'Electrical', 'description': 'Electrical installation and repair skills'},
        {'name': 'Fencing', 'description': 'Fence installation and repair'},
        {'name': 'Flooring', 'description': 'Installation and repair of various flooring types'},
        {'name': 'Garage/Sheds', 'description': 'Construction and repair of garages and sheds'},
        {'name': 'Hauling/Moving', 'description': 'Materials handling and transportation'},
        {'name': 'Heating/Cooling', 'description': 'HVAC repair and maintenance'},
        {'name': 'Landscaping', 'description': 'Landscape design and maintenance'},
        {'name': 'Maintenance (Inside)', 'description': 'General interior maintenance skills'},
        {'name': 'Maintenance (Outside)', 'description': 'General exterior maintenance skills'},
        {'name': 'Painting/Staining', 'description': 'Surface preparation, painting, and staining'},
        {'name': 'Roofing/Gutters', 'description': 'Roof repair and gutter installation'},
        {'name': 'Commercial Work', 'description': 'Skills specific to commercial properties'}
    ]
    
    logger.info(f"Seeding {len(categories)} skill categories")
    for category in categories:
        cursor.execute(
            "INSERT INTO skill_categories (name, description) VALUES (?, ?);",
            (category['name'], category['description'])
        )
    
    conn.commit()
    logger.info("Skill categories seeded successfully")


def seed_skills(conn, logger):
    """Seed skills for each category based on the Excel template"""
    cursor = conn.cursor()
    
    # Check if skills already exist
    cursor.execute("SELECT COUNT(*) FROM skills;")
    count = cursor.fetchone()[0]
    if count > 0:
        logger.info(f"Found {count} existing skills, skipping seed")
        return
    
    # Get the categories
    cursor.execute("SELECT id, name FROM skill_categories;")
    categories = cursor.fetchall()
    
    skills_by_category = {
        'Crawl space/Skirting': [
            'Skirting/siding', 'Wall Framing', 'Joist Framing', 'Insulating', 'Underpinning'
        ],
        'Bathroom/Kitchen/Plumbing': [
            'Remove/Replace Faucet Assembly', 'Remove/Replace Faucet Washers',
            'Remove/Replace Faucet Seat', 'Remove/Replace Shower Faucet Cartridge',
            'Install Supply Lines', 'Install Pex B pipe with crimp rings',
            'Install Pex A pipe with expansion fittings', 'Install/Replace Supply Valves',
            'Install/Replace Bath Sink', 'Remove/Replace Drain P-Trap',
            'Install/Replace Vanity top', 'Install/Replace Vanity', 
            'Seal Vanity corners', 'Adjust Toilet', 'Remove/Replace Toilet Fill Valve',
            'Remove/Replace Toilet Flush Valve', 'Install/Replace Toilet',
            'Remove/Replace Tub/Shower Valve', 'Install/Replace Towel Bar Kits',
            'Install/Replace Tub/Shower pan concrete', 'Install/Replace Tub/Shower pan Fiberglass',
            'Install Tile Backer Board', 'Install/Replace Wall Tile', 'Grout Wall Tile',
            'Install Shower Door', 'Install/Replace Disposal', 'Install/Replace Kitchen Sink',
            'Install/Replace Hose Bibb', 'Hookup Dishwasher', 'Sweat Copper',
            'Run Gas Line', 'Troubleshoot Leaks', 'D.W.V. Assembly',
            'Install/Replace Kitchen Cabinets', 'Install/Replace/Build Countertops', 
            'Install/Replace Cabinet Trim'
        ],
        # Add skills for other categories here...
    }
    
    # Add some skills for each category
    total_skills = 0
    for category_id, category_name in categories:
        skills = skills_by_category.get(category_name, [])
        if not skills:
            # Generate placeholder skills if not defined
            skills = [f"{category_name} Skill {i+1}" for i in range(5)]
            
        logger.info(f"Seeding {len(skills)} skills for category '{category_name}'")
        for skill in skills:
            cursor.execute(
                "INSERT INTO skills (category_id, name, description) VALUES (?, ?, ?);",
                (category_id, skill, f"Proficiency in {skill}")
            )
            total_skills += 1
    
    conn.commit()
    logger.info(f"Successfully seeded {total_skills} skills across all categories")


def seed_tool_categories(conn, logger):
    """Seed tool categories"""
    cursor = conn.cursor()
    
    # Check if categories already exist
    cursor.execute("SELECT COUNT(*) FROM tool_categories;")
    count = cursor.fetchone()[0]
    if count > 0:
        logger.info(f"Found {count} existing tool categories, skipping seed")
        return
    
    # Tool categories
    categories = [
        {'name': 'Hand Tools', 'description': 'Non-powered manual tools'},
        {'name': 'Power Tools', 'description': 'Electric and battery-powered tools'},
        {'name': 'Measuring Tools', 'description': 'Tools for measuring and layout'},
        {'name': 'Plumbing Tools', 'description': 'Specialized tools for plumbing work'},
        {'name': 'Electrical Tools', 'description': 'Specialized tools for electrical work'},
        {'name': 'Painting Tools', 'description': 'Tools for painting and finishing'},
        {'name': 'Safety Equipment', 'description': 'Personal protective equipment'},
        {'name': 'Ladders & Staging', 'description': 'Equipment for working at height'},
        {'name': 'Specialty Tools', 'description': 'Tools for specialized applications'}
    ]
    
    logger.info(f"Seeding {len(categories)} tool categories")
    for category in categories:
        cursor.execute(
            "INSERT INTO tool_categories (name, description) VALUES (?, ?);",
            (category['name'], category['description'])
        )
    
    conn.commit()
    logger.info("Tool categories seeded successfully")


def seed_tools(conn, logger):
    """Seed tools for each category"""
    cursor = conn.cursor()
    
    # Check if tools already exist
    cursor.execute("SELECT COUNT(*) FROM tools;")
    count = cursor.fetchone()[0]
    if count > 0:
        logger.info(f"Found {count} existing tools, skipping seed")
        return
    
    # Get the categories
    cursor.execute("SELECT id, name FROM tool_categories;")
    categories = cursor.fetchall()
    
    tools_by_category = {
        'Hand Tools': [
            'Hammer', 'Screwdriver Set', 'Pliers', 'Wrench Set', 'Utility Knife',
            'Chisels', 'Hand Saw', 'Putty Knife', 'Crow Bar', 'Allen Wrench Set'
        ],
        'Power Tools': [
            'Drill', 'Circular Saw', 'Jigsaw', 'Reciprocating Saw', 'Angle Grinder',
            'Router', 'Power Planer', 'Belt Sander', 'Oscillating Tool', 'Heat Gun'
        ],
        'Measuring Tools': [
            'Tape Measure', 'Level', 'Speed Square', 'Framing Square', 'Chalk Line',
            'Laser Level', 'Stud Finder', 'Plumb Bob', 'Calipers', 'Protractor'
        ],
        'Plumbing Tools': [
            'Pipe Wrench', 'Tubing Cutter', 'Pipe Cutter', 'Plunger', 'Drain Snake',
            'Pipe Threader', 'Basin Wrench', 'Toilet Auger', 'Crimping Tool', 'PEX Expander'
        ],
        'Electrical Tools': [
            'Wire Strippers', 'Voltage Tester', 'Multimeter', 'Fish Tape', 'Cable Cutter',
            'Wire Crimper', 'Circuit Finder', 'Outlet Tester', 'Conduit Bender', 'Insulated Screwdrivers'
        ],
        'Painting Tools': [
            'Paint Brushes', 'Paint Rollers', 'Paint Sprayer', 'Drop Cloths', 'Paint Trays',
            'Extension Pole', 'Paint Scrapers', 'Sanding Block', 'Caulking Gun', 'Masking Tools'
        ],
        'Safety Equipment': [
            'Safety Glasses', 'Ear Protection', 'Dust Mask', 'Respirator', 'Work Gloves',
            'Hard Hat', 'Safety Harness', 'Knee Pads', 'Safety Vest', 'Steel Toe Boots'
        ],
        'Ladders & Staging': [
            'Step Ladder', 'Extension Ladder', 'Platform Ladder', 'Multi-Purpose Ladder', 'Scaffold',
            'Ladder Stabilizer', 'Ladder Hook', 'Work Platform', 'Ladder Leveler', 'Ladder Jacks'
        ],
        'Specialty Tools': [
            'Tile Cutter', 'Flooring Nailer', 'Laminate Cutter', 'Texture Sprayer', 'Drywall Lift',
            'Concrete Mixer', 'Post Hole Digger', 'Air Compressor', 'Pressure Washer', 'Nail Gun'
        ]
    }
    
    # Add tools for each category
    total_tools = 0
    for category_id, category_name in categories:
        tools = tools_by_category.get(category_name, [])
        if not tools:
            # Generate placeholder tools if not defined
            tools = [f"{category_name} Tool {i+1}" for i in range(5)]
            
        logger.info(f"Seeding {len(tools)} tools for category '{category_name}'")
        for tool in tools:
            cursor.execute(
                "INSERT INTO tools (category_id, name, description) VALUES (?, ?, ?);",
                (category_id, tool, f"Tool for {tool.lower()} tasks")
            )
            total_tools += 1
    
    conn.commit()
    logger.info(f"Successfully seeded {total_tools} tools across all categories")


def seed_users(conn, logger, admin_password=None):
    """Seed user roles and admin user"""
    cursor = conn.cursor()
    
    # Check if users already exist
    cursor.execute("SELECT COUNT(*) FROM users;")
    count = cursor.fetchone()[0]
    if count > 0:
        logger.info(f"Found {count} existing users, skipping seed")
        return
    
    # Get admin password from arguments, environment, or default
    if not admin_password:
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
    
    # Create admin user
    hashed_password = generate_password_hash(admin_password)
    
    logger.info("Creating admin user")
    cursor.execute(
        """
        INSERT INTO users (
            username, email, password_hash, first_name, last_name, 
            role, is_active, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        ('admin', 'admin@example.com', hashed_password, 'System', 'Administrator',
         'admin', 1, datetime.datetime.now())
    )
    
    # Create a manager user
    manager_password = generate_password_hash('manager')
    cursor.execute(
        """
        INSERT INTO users (
            username, email, password_hash, first_name, last_name, 
            role, is_active, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        ('manager', 'manager@example.com', manager_password, 'Team', 'Manager',
         'manager', 1, datetime.datetime.now())
    )
    
    conn.commit()
    logger.info("Users seeded successfully")


def seed_sample_employees(conn, logger):
    """Seed sample employees for testing"""
    cursor = conn.cursor()
    
    # Check if employees already exist
    cursor.execute("SELECT COUNT(*) FROM employees;")
    count = cursor.fetchone()[0]
    if count > 0:
        logger.info(f"Found {count} existing employees, skipping sample data")
        return
    
    # Sample employee data
    employees = [
        {
            'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@example.com',
            'phone': '555-123-4567', 'hire_date': '2022-01-15', 'tier': 'Craftsman',
            'address': '123 Main St', 'city': 'Anytown', 'state': 'CA', 'zip': '90210'
        },
        {
            'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.j@example.com',
            'phone': '555-234-5678', 'hire_date': '2021-08-22', 'tier': 'Master Craftsman',
            'address': '456 Oak Ave', 'city': 'Springfield', 'state': 'IL', 'zip': '62704'
        },
        {
            'first_name': 'Michael', 'last_name': 'Williams', 'email': 'mike.w@example.com',
            'phone': '555-345-6789', 'hire_date': '2023-03-10', 'tier': 'Apprentice',
            'address': '789 Pine St', 'city': 'Riverside', 'state': 'CA', 'zip': '92501'
        },
        {
            'first_name': 'Jessica', 'last_name': 'Brown', 'email': 'jess.brown@example.com',
            'phone': '555-456-7890', 'hire_date': '2022-11-05', 'tier': 'Handyman',
            'address': '321 Elm St', 'city': 'Lakeside', 'state': 'MI', 'zip': '49116'
        },
        {
            'first_name': 'David', 'last_name': 'Miller', 'email': 'david.m@example.com',
            'phone': '555-567-8901', 'hire_date': '2020-06-18', 'tier': 'Lead Craftsman',
            'address': '654 Maple Dr', 'city': 'Mountainview', 'state': 'CO', 'zip': '80014'
        }
    ]
    
    logger.info(f"Seeding {len(employees)} sample employees")
    for employee in employees:
        cursor.execute(
            """
            INSERT INTO employees (
                first_name, last_name, email, phone, hire_date, tier,
                address, city, state, zip
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                employee['first_name'], employee['last_name'], employee['email'],
                employee['phone'], employee['hire_date'], employee['tier'],
                employee['address'], employee['city'], employee['state'], employee['zip']
            )
        )
    
    conn.commit()
    logger.info("Sample employees seeded successfully")


def seed_sample_evaluations(conn, logger):
    """Seed sample evaluations for testing"""
    cursor = conn.cursor()
    
    # Check if evaluations already exist
    cursor.execute("SELECT COUNT(*) FROM evaluations;")
    count = cursor.fetchone()[0]
    if count > 0:
        logger.info(f"Found {count} existing evaluations, skipping sample data")
        return
    
    # Get employees and user ids
    cursor.execute("SELECT id FROM employees;")
    employee_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM users WHERE role='manager';")
    manager_id = cursor.fetchone()[0]
    
    # Get skills and tools
    cursor.execute("SELECT id FROM skills;")
    skill_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM tools;")
    tool_ids = [row[0] for row in cursor.fetchall()]
    
    # Sample date range (past 6 months)
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=180)
    
    # Create sample evaluations
    logger.info("Seeding sample evaluations")
    total_evaluations = 0
    
    for employee_id in employee_ids:
        # Create 2-4 evaluations per employee
        num_evaluations = random.randint(2, 4)
        
        for i in range(num_evaluations):
            # Random date in the past 6 months
            days_ago = random.randint(0, 180)
            eval_date = end_date - datetime.timedelta(days=days_ago)
            
            # Create evaluation
            cursor.execute(
                """
                INSERT INTO evaluations (
                    employee_id, evaluator_id, evaluation_date, notes, overall_rating
                ) VALUES (?, ?, ?, ?, ?);
                """,
                (
                    employee_id, 
                    manager_id,
                    eval_date.strftime('%Y-%m-%d'),
                    f"Evaluation #{i+1} for employee {employee_id}",
                    random.randint(3, 5)  # Overall rating between 3-5
                )
            )
            
            evaluation_id = cursor.lastrowid
            
            # Add skill ratings (10-15 random skills)
            num_skills = random.randint(10, 15)
            selected_skill_ids = random.sample(skill_ids, min(num_skills, len(skill_ids)))
            
            for skill_id in selected_skill_ids:
                cursor.execute(
                    """
                    INSERT INTO eval_skills (
                        evaluation_id, skill_id, rating, notes
                    ) VALUES (?, ?, ?, ?);
                    """,
                    (
                        evaluation_id,
                        skill_id,
                        random.randint(1, 5),  # Rating between 1-5
                        "Skill evaluation notes"
                    )
                )
            
            # Add tool proficiencies (5-10 random tools)
            num_tools = random.randint(5, 10)
            selected_tool_ids = random.sample(tool_ids, min(num_tools, len(tool_ids)))
            
            for tool_id in selected_tool_ids:
                can_operate = random.choice([True, True, True, False])  # More likely to be able to operate
                owns_tool = can_operate and random.choice([True, False])  # Can only own if can operate
                
                cursor.execute(
                    """
                    INSERT INTO eval_tools (
                        evaluation_id, tool_id, can_operate, owns_tool
                    ) VALUES (?, ?, ?, ?);
                    """,
                    (
                        evaluation_id,
                        tool_id,
                        1 if can_operate else 0,
                        1 if owns_tool else 0
                    )
                )
            
            total_evaluations += 1
    
    conn.commit()
    logger.info(f"Successfully seeded {total_evaluations} sample evaluations")


def main():
    """Main function"""
    args = parse_args()
    logger = setup_logging(args.verbose)
    
    # Get database path
    db_path = os.environ.get(
        'DATABASE_PATH', 
        os.path.join('instance', 'database', 'kpi.db')
    )
    
    logger.info(f"Using database at {db_path}")
    
    # Connect to the database
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {str(e)}")
        sys.exit(1)
    
    # Reset tables if requested
    if args.reset:
        tables_to_reset = [
            'eval_tools', 'eval_skills', 'evaluations', 
            'special_skills', 'employees', 'tools', 'tool_categories',
            'skills', 'skill_categories', 'users'
        ]
        reset_tables(conn, logger, tables_to_reset)
    
    # Seed reference data
    try:
        seed_skill_categories(conn, logger)
        seed_skills(conn, logger)
        seed_tool_categories(conn, logger)
        seed_tools(conn, logger)
        seed_users(conn, logger, args.admin_password)
        
        # Seed sample data if requested
        if args.sample_data:
            seed_sample_employees(conn, logger)
            seed_sample_evaluations(conn, logger)
        
        logger.info("Database seeding completed successfully")
    
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()
