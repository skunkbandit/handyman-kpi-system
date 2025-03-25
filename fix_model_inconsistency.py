"""
Script to fix the database model inconsistency.
Modifies the User model to correctly reference the Employee model.
"""
import os
import re
import sys

def fix_model_inconsistency():
    print("=" * 60)
    print("FIXING MODEL INCONSISTENCY")
    print("=" * 60)
    
    # Path to the user model file
    user_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  'kpi-system', 'backend', 'app', 'models', 'user.py')
    
    if not os.path.exists(user_model_path):
        print(f"ERROR: User model file not found at {user_model_path}")
        return False
    
    # Read the current file content
    with open(user_model_path, 'r') as f:
        content = f.read()
    
    # Make a backup of the original file
    backup_path = user_model_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup of original file at {backup_path}")
    
    # Fix the foreign key reference
    content_fixed = re.sub(
        r"employee_id = db\.Column\(db\.Integer, db\.ForeignKey\('employees\.id'\)\)",
        "employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))",
        content
    )
    
    # Check if the replacement was successful
    if content_fixed == content:
        print("WARNING: No changes were made. The pattern may not have matched.")
        return False
    
    # Write the fixed content back to the file
    with open(user_model_path, 'w') as f:
        f.write(content_fixed)
    
    print(f"Successfully updated {user_model_path}")
    print("Changed ForeignKey from 'employees.id' to 'employees.employee_id'")
    
    print("\nFix completed. Now run the model consistency check again to verify.")
    return True

if __name__ == "__main__":
    fix_model_inconsistency()
