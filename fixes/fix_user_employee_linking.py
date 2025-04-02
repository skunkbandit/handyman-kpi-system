"""
Script to fix the user-employee linking issue in the KPI system.

The issue: When creating or editing a user, the employee dropdown shows blank values instead of employee names.
The cause: Templates are using 'first_name' and 'last_name' fields, but the Employee model only has a 'name' field.
          Additionally, templates are using 'employee.id' instead of 'employee.employee_id' for the value attribute.

This script:
1. Makes backups of the original templates
2. Updates the templates to use the correct field names
3. Reports on the changes made
"""

import os
import shutil
import re
import sys

def fix_user_employee_linking():
    print("=" * 60)
    print("FIXING USER-EMPLOYEE LINKING ISSUE")
    print("=" * 60)
    
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, '..', 'kpi-system', 'backend', 'app', 'templates', 'auth')
    backup_dir = os.path.join(base_dir, '..', 'backups', 'templates', 'auth')
    
    create_user_template = os.path.join(templates_dir, 'create_user.html')
    edit_user_template = os.path.join(templates_dir, 'edit_user.html')
    
    # Make sure template files exist
    if not os.path.exists(create_user_template):
        print(f"ERROR: Create user template not found at {create_user_template}")
        return False
        
    if not os.path.exists(edit_user_template):
        print(f"ERROR: Edit user template not found at {edit_user_template}")
        return False
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backups of original files
    create_user_backup = os.path.join(backup_dir, 'create_user.html.bak')
    edit_user_backup = os.path.join(backup_dir, 'edit_user.html.bak')
    
    print(f"Creating backup of {create_user_template} to {create_user_backup}")
    shutil.copy2(create_user_template, create_user_backup)
    
    print(f"Creating backup of {edit_user_template} to {edit_user_backup}")
    shutil.copy2(edit_user_template, edit_user_backup)
    
    # Fix create_user.html
    print("\nUpdating create_user.html...")
    with open(create_user_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the employee dropdown options
    original_pattern = r'{{ employee\.first_name }} {{ employee\.last_name }}'
    replace_with = '{{ employee.name }}'
    content = re.sub(original_pattern, replace_with, content)
    
    # Fix the value attribute
    value_pattern = r'value="{{ employee\.id }}"'
    replace_with = 'value="{{ employee.employee_id }}"'
    content = re.sub(value_pattern, replace_with, content)
    
    # Write the updated content back to the file
    with open(create_user_template, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  - Fixed employee name display in create_user.html")
    print("  - Fixed employee ID value in create_user.html")
    
    # Fix edit_user.html
    print("\nUpdating edit_user.html...")
    with open(edit_user_template, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the employee dropdown options
    original_pattern = r'{{ employee\.first_name }} {{ employee\.last_name }}'
    replace_with = '{{ employee.name }}'
    content = re.sub(original_pattern, replace_with, content)
    
    # Fix the value attribute
    value_pattern = r'value="{{ employee\.id }}"'
    replace_with = 'value="{{ employee.employee_id }}"'
    content = re.sub(value_pattern, replace_with, content)
    
    # Fix the selected attribute comparison
    selected_pattern = r'{{ \'selected\' if user\.employee_id == employee\.id else \'\' }}'
    replace_with = '{{ \'selected\' if user.employee_id == employee.employee_id else \'\' }}'
    content = re.sub(selected_pattern, replace_with, content)
    
    # Write the updated content back to the file
    with open(edit_user_template, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  - Fixed employee name display in edit_user.html")
    print("  - Fixed employee ID value in edit_user.html")
    print("  - Fixed selected attribute comparison in edit_user.html")
    
    print("\n" + "=" * 60)
    print("FIX COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nBackups of the original files are stored at:")
    print(f"  - {create_user_backup}")
    print(f"  - {edit_user_backup}")
    
    return True

if __name__ == "__main__":
    fix_user_employee_linking()
