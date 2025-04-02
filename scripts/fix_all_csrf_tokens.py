"""
Fix CSRF Token Missing Error in All Forms

This script adds CSRF token fields to all forms in the application that use the POST method
to resolve the "400 Bad Request: The CSRF token is missing" error.

Usage:
    python fix_all_csrf_tokens.py

Author: Claude
Date: April 2, 2025
"""

import os
import re
import shutil
from pathlib import Path
import glob

def add_csrf_token(content):
    """Add CSRF token to form if missing"""
    if 'csrf_token' not in content:
        # This regex looks for forms that use method="post"
        pattern = r'<form\s+[^>]*method="post"[^>]*>'
        replacement = r'\g<0>\n    <!-- CSRF Token -->\n    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">'
        
        # Apply the replacement
        modified_content = re.sub(pattern, replacement, content)
        
        # Check if we actually made a change
        if modified_content != content:
            return modified_content, True
        else:
            return content, False
    else:
        # CSRF token already exists
        return content, False

def fix_template(file_path):
    """Add CSRF token to a template file if missing"""
    print(f"Processing {file_path}...")
    
    # Read the current content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if this file has a form with method="post"
    if 'method="post"' in content.lower():
        # Create a backup
        backup_path = str(file_path) + ".bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Add CSRF token if needed
        modified_content, changed = add_csrf_token(content)
        
        # Write the modified content back
        if changed:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            print(f"✅ Added CSRF token to {file_path}")
            return True
        else:
            print(f"ℹ️ Form found but no changes needed for {file_path}")
            return False
    else:
        print(f"ℹ️ No POST forms found in {file_path}")
        return False

def find_all_templates(templates_dir):
    """Find all HTML template files in the application"""
    return list(Path(templates_dir).glob('**/*.html'))

def main():
    """Main function to fix all templates"""
    print("Starting CSRF token fix for all templates...")
    
    # Determine the base directory
    # This will work whether we're in the scripts directory or the project root
    script_dir = Path(__file__).parent.resolve()
    
    # Try to locate the templates directory
    if (script_dir / ".." / "backend" / "app" / "templates").exists():
        templates_dir = script_dir / ".." / "backend" / "app" / "templates"
    elif (script_dir / "backend" / "app" / "templates").exists():
        templates_dir = script_dir / "backend" / "app" / "templates"
    else:
        print("Error: Cannot find templates directory. Please run this script from the project root or scripts directory.")
        return
    
    # Find all template files
    templates = find_all_templates(templates_dir)
    print(f"Found {len(templates)} template files to check")
    
    # Initialize counters
    fixed_count = 0
    total_forms = 0
    
    # Process each template
    for template in templates:
        if template.exists():
            was_fixed = fix_template(template)
            if was_fixed:
                fixed_count += 1
            if 'method="post"' in open(template, 'r', encoding='utf-8').read().lower():
                total_forms += 1
        else:
            print(f"⚠️ Template not found: {template}")
    
    print("\nCSRF token fix complete!")
    print(f"Fixed {fixed_count} forms out of {total_forms} total POST forms")
    print("You should now be able to submit forms without the CSRF token error.")

if __name__ == '__main__':
    main()
