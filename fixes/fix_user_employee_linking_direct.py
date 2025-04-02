"""
Script to fix the user-employee linking issue in the KPI system by direct file replacement.

This script:
1. Backs up the original template files
2. Replaces them with fixed versions that use the correct field names
3. Fixes URL parameter names in the templates
"""

import os
import shutil
import sys
from datetime import datetime

def fix_user_employee_linking_direct():
    print("=" * 60)
    print("FIXING USER-EMPLOYEE LINKING ISSUE (DIRECT REPLACEMENT)")
    print("=" * 60)
    
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, '..', 'kpi-system', 'backend', 'app', 'templates', 'auth')
    backup_dir = os.path.join(base_dir, '..', 'backups', 'templates', 'auth')
    
    # Template files
    create_user_template = os.path.join(templates_dir, 'create_user.html')
    edit_user_template = os.path.join(templates_dir, 'edit_user.html')
    user_management_template = os.path.join(templates_dir, 'user_management.html')
    
    # Fixed template files
    fixed_create_user = os.path.join(base_dir, 'templates', 'auth', 'fixed_create_user.html')
    fixed_edit_user = os.path.join(base_dir, 'templates', 'auth', 'fixed_edit_user.html')
    fixed_user_management = os.path.join(base_dir, 'templates', 'auth', 'fixed_user_management.html')
    
    # Make sure original template files exist
    if not os.path.exists(create_user_template):
        print(f"ERROR: Create user template not found at {create_user_template}")
        return False
        
    if not os.path.exists(edit_user_template):
        print(f"ERROR: Edit user template not found at {edit_user_template}")
        return False
        
    if not os.path.exists(user_management_template):
        print(f"ERROR: User management template not found at {user_management_template}")
        return False
    
    # Make sure fixed template files exist
    if not os.path.exists(fixed_create_user):
        print(f"ERROR: Fixed create user template not found at {fixed_create_user}")
        return False
        
    if not os.path.exists(fixed_edit_user):
        print(f"ERROR: Fixed edit user template not found at {fixed_edit_user}")
        return False
        
    if not os.path.exists(fixed_user_management):
        print(f"ERROR: Fixed user management template not found at {fixed_user_management}")
        return False
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backups of original files with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    create_user_backup = os.path.join(backup_dir, f'create_user.html.{timestamp}.bak')
    edit_user_backup = os.path.join(backup_dir, f'edit_user.html.{timestamp}.bak')
    user_management_backup = os.path.join(backup_dir, f'user_management.html.{timestamp}.bak')
    
    print(f"Creating backup of {create_user_template} to {create_user_backup}")
    shutil.copy2(create_user_template, create_user_backup)
    
    print(f"Creating backup of {edit_user_template} to {edit_user_backup}")
    shutil.copy2(edit_user_template, edit_user_backup)
    
    print(f"Creating backup of {user_management_template} to {user_management_backup}")
    shutil.copy2(user_management_template, user_management_backup)
    
    # Replace files with fixed versions
    print(f"\nReplacing {create_user_template} with fixed version...")
    shutil.copy2(fixed_create_user, create_user_template)
    
    print(f"Replacing {edit_user_template} with fixed version...")
    shutil.copy2(fixed_edit_user, edit_user_template)
    
    print(f"Replacing {user_management_template} with fixed version...")
    shutil.copy2(fixed_user_management, user_management_template)
    
    print("\n" + "=" * 60)
    print("FIX COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nThe following issues have been fixed:")
    print("1. Employee dropdown now shows employee names correctly")
    print("2. Employee dropdown values match the employee_id field")
    print("3. Selected employee is properly highlighted when editing a user")
    print("4. User management page now uses correct URL parameter for viewing linked employees")
    print("\nBackups of the original files are stored at:")
    print(f"  - {create_user_backup}")
    print(f"  - {edit_user_backup}")
    print(f"  - {user_management_backup}")
    
    return True

if __name__ == "__main__":
    fix_user_employee_linking_direct()
