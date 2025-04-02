"""
Fix CSRF Token Missing Error in Employee Forms

This script adds CSRF token fields to all employee form templates
to resolve the "400 Bad Request: The CSRF token is missing" error.

Usage:
    python fix_csrf_token.py

Author: Claude
Date: April 2, 2025
"""

import os
import re
import shutil
from pathlib import Path

def add_csrf_token(content):
    """Add CSRF token to form if missing"""
    if 'csrf_token' not in content:
        # This regex looks for forms that use method="post"
        pattern = r'<form\s+method="post"[^>]*>'
        replacement = r'\g<0>\n                    <!-- CSRF Token -->\n                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">'
        
        # Apply the replacement
        modified_content = re.sub(pattern, replacement, content)
        
        return modified_content
    else:
        # CSRF token already exists
        return content

def fix_template(file_path):
    """Add CSRF token to a template file if missing"""
    print(f"Processing {file_path}...")
    
    # Read the current content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a backup
    backup_path = str(file_path) + ".bak"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Add CSRF token if needed
    modified_content = add_csrf_token(content)
    
    # Write the modified content back
    if content != modified_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"✅ Added CSRF token to {file_path}")
    else:
        print(f"ℹ️ No changes needed for {file_path}")

def main():
    """Main function to fix all templates"""
    print("Starting CSRF token fix...")
    
    # Determine the base directory
    # This will work whether we're in the scripts directory or the project root
    script_dir = Path(__file__).parent.resolve()
    
    # Try to locate the templates directory
    if (script_dir / ".." / "kpi-system" / "backend" / "app" / "templates").exists():
        base_dir = script_dir / ".."
    elif (script_dir / "kpi-system" / "backend" / "app" / "templates").exists():
        base_dir = script_dir
    else:
        print("Error: Cannot find templates directory. Please run this script from the project root or scripts directory.")
        return
    
    # Define template paths
    templates_dir = base_dir / "kpi-system" / "backend" / "app" / "templates" / "employees"
    
    templates_to_fix = [
        templates_dir / "create.html",
        templates_dir / "edit.html",
        templates_dir / "index.html"
    ]
    
    for template in templates_to_fix:
        if template.exists():
            fix_template(template)
        else:
            print(f"⚠️ Template not found: {template}")
    
    print("\nSearching for other forms that might need CSRF tokens...")
    all_templates_dir = base_dir / "kpi-system" / "backend" / "app" / "templates"
    for root, _, files in os.walk(all_templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = Path(root) / file
                if file_path not in templates_to_fix:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if 'method="post"' in content and 'csrf_token' not in content:
                        print(f"⚠️ Form without CSRF token found in: {file_path}")
    
    print("\nCSRF token fix complete!")
    print("You should now be able to add employees without the CSRF token error.")

if __name__ == '__main__':
    main()
