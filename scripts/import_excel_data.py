#!/usr/bin/env python3
"""
Import data from the Craftman Development Score Card Excel spreadsheet into the KPI system database.

This script extracts skill categories, skills, tool categories, and tools from the provided Excel
spreadsheet and populates the SQLite database with the extracted data.
"""

import os
import sys
import sqlite3
import pandas as pd
import re
from datetime import datetime

# Path to the Excel file
EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          "Craftman Developement Score Card.xlsx")

# Path to the database file
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                        "kpi-system", "database", "kpi_system.db")

def create_connection():
    """Create a database connection to the SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        print(f"Connected to SQLite database: {DB_FILE}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def check_tables_exist(conn):
    """Check if the required tables exist in the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['skill_categories', 'skills', 'tool_categories', 'tools']
    
    for table in required_tables:
        if table not in tables:
            print(f"Error: Required table '{table}' does not exist in the database.")
            print("Please run database migrations first.")
            sys.exit(1)
    
    print("All required tables exist.")

def extract_categories_and_skills(df):
    """Extract skill categories and skills from the Excel spreadsheet"""
    categories = []
    skills = []
    
    current_category = None
    category_id = 1
    skill_id = 1
    
    # Iterate through rows in column A
    for idx, row in df.iterrows():
        cell_value = row.iloc[0]
        
        # Skip empty cells or non-string values
        if pd.isna(cell_value) or not isinstance(cell_value, str):
            continue
        
        # Check if this is a category header (no colon and not a sub-item)
        if ":" not in cell_value and cell_value.strip() and not cell_value.startswith("  "):
            current_category = {
                'category_id': category_id,
                'name': cell_value.strip(),
                'display_order': category_id
            }
            categories.append(current_category)
            category_id += 1
        # Check if this is a skill (has colon or is a standalone skill)
        elif current_category is not None and cell_value.strip() and "TOOL LIST" not in cell_value and "List any" not in cell_value:
            # Remove the colon if present
            skill_name = cell_value.split(':')[0].strip() if ':' in cell_value else cell_value.strip()
            
            # Skip if it's actually a header or note
            if skill_name in ["Rate yourself", "Tools", "Y or N", "TS", "Yes", "No"]:
                continue
                
            skills.append({
                'skill_id': skill_id,
                'category_id': current_category['category_id'],
                'name': skill_name,
                'display_order': skill_id
            })
            skill_id += 1
    
    return categories, skills

def extract_tool_categories_and_tools(df):
    """Extract tool categories and tools from the Excel spreadsheet"""
    tool_categories = []
    tools = []
    
    current_category = None
    category_id = 1
    tool_id = 1
    
    # First, extract all category names
    categories_map = {}
    for idx, row in df.iterrows():
        cell_value = row.iloc[0]
        if pd.notna(cell_value) and isinstance(cell_value, str) and ":" not in cell_value and cell_value.strip():
            if "TOOL LIST" not in cell_value and "List any" not in cell_value:
                categories_map[cell_value.strip()] = category_id
                tool_categories.append({
                    'category_id': category_id,
                    'name': cell_value.strip(),
                    'display_order': category_id
                })
                category_id += 1
    
    # Now extract tools from column H and associate them with the right category
    current_category_id = None
    for idx, row in df.iterrows():
        # Check if column A has a category name
        if pd.notna(row.iloc[0]) and isinstance(row.iloc[0], str) and row.iloc[0].strip() in categories_map:
            current_category_id = categories_map[row.iloc[0].strip()]
        
        # Skip rows without a category
        if current_category_id is None:
            continue
            
        # Check column H for tools
        tool_name = row.iloc[7] if len(row) > 7 and pd.notna(row.iloc[7]) else None
        
        if tool_name and isinstance(tool_name, str) and ":" in tool_name and "Additional tools needed" not in tool_name:
            # Extract the tool name (remove colon)
            tool_name = tool_name.split(':')[0].strip()
            
            # Skip empty or header rows
            if not tool_name or tool_name == "Tools" or tool_name == "TOOL LIST":
                continue
                
            tools.append({
                'tool_id': tool_id,
                'category_id': current_category_id,
                'name': tool_name,
                'display_order': tool_id
            })
            tool_id += 1
    
    return tool_categories, tools

def insert_data(conn, categories, skills, tool_categories, tools):
    """Insert extracted data into the database"""
    cursor = conn.cursor()
    
    # First, check if data already exists
    cursor.execute("SELECT COUNT(*) FROM skill_categories")
    if cursor.fetchone()[0] > 0:
        print("Data already exists in the database.")
        choice = input("Do you want to clear existing data and insert new data? (y/n): ")
        if choice.lower() != 'y':
            print("Import canceled.")
            return
        
        # Clear existing data
        cursor.execute("DELETE FROM skills")
        cursor.execute("DELETE FROM skill_categories")
        cursor.execute("DELETE FROM tools")
        cursor.execute("DELETE FROM tool_categories")
        print("Existing data cleared.")
    
    try:
        # Insert skill categories
        for category in categories:
            cursor.execute(
                "INSERT INTO skill_categories (category_id, name, display_order, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (category['category_id'], category['name'], category['display_order'], datetime.now(), datetime.now())
            )
        
        # Insert skills
        for skill in skills:
            cursor.execute(
                "INSERT INTO skills (skill_id, category_id, name, display_order, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (skill['skill_id'], skill['category_id'], skill['name'], skill['display_order'], datetime.now(), datetime.now())
            )
        
        # Insert tool categories
        for category in tool_categories:
            cursor.execute(
                "INSERT INTO tool_categories (category_id, name, display_order, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (category['category_id'], category['name'], category['display_order'], datetime.now(), datetime.now())
            )
        
        # Insert tools
        for tool in tools:
            cursor.execute(
                "INSERT INTO tools (tool_id, category_id, name, display_order, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (tool['tool_id'], tool['category_id'], tool['name'], tool['display_order'], datetime.now(), datetime.now())
            )
        
        conn.commit()
        print(f"Successfully inserted {len(categories)} skill categories, {len(skills)} skills, "
              f"{len(tool_categories)} tool categories, and {len(tools)} tools.")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error inserting data: {e}")

def main():
    """Main function to run the import process"""
    print(f"Importing data from: {EXCEL_FILE}")
    
    # Check if Excel file exists
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: Excel file not found: {EXCEL_FILE}")
        sys.exit(1)
    
    # Check if database file exists
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file not found: {DB_FILE}")
        sys.exit(1)
    
    # Create database connection
    conn = create_connection()
    
    # Check if required tables exist
    check_tables_exist(conn)
    
    try:
        # Read Excel file
        print("Reading Excel file...")
        df = pd.read_excel(EXCEL_FILE, sheet_name="Sheet1", header=None)
        
        # Extract data
        print("Extracting skill categories and skills...")
        categories, skills = extract_categories_and_skills(df)
        print(f"Extracted {len(categories)} skill categories and {len(skills)} skills.")
        
        print("Extracting tool categories and tools...")
        tool_categories, tools = extract_tool_categories_and_tools(df)
        print(f"Extracted {len(tool_categories)} tool categories and {len(tools)} tools.")
        
        # Insert data into database
        print("Inserting data into database...")
        insert_data(conn, categories, skills, tool_categories, tools)
        
    except Exception as e:
        print(f"Error processing data: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()