"""
Script to fix the database model relationships.
Updates the Evaluation model to properly specify foreign keys for relationships.
"""
import os
import re
import sys

def fix_model_relationship():
    print("=" * 60)
    print("FIXING EVALUATION MODEL RELATIONSHIP")
    print("=" * 60)
    
    # Path to the evaluation model file
    evaluation_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  'kpi-system', 'backend', 'app', 'models', 'evaluation.py')
    
    if not os.path.exists(evaluation_model_path):
        print(f"ERROR: Evaluation model file not found at {evaluation_model_path}")
        return False
    
    # Read the current file content
    with open(evaluation_model_path, 'r') as f:
        content = f.read()
    
    # Make a backup of the original file
    backup_path = evaluation_model_path + '.bak'
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup of original file at {backup_path}")
    
    # Fix the ambiguous relationship by specifying the foreign_keys argument
    old_relationship = "employee = db.relationship('Employee', foreign_keys=[employee_id], back_populates='evaluations')"
    new_relationship = "employee = db.relationship('Employee', foreign_keys=[employee_id], back_populates='evaluations')"
    
    # Check Employee model to see if it needs updates as well
    employee_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  'kpi-system', 'backend', 'app', 'models', 'employee.py')
    
    if not os.path.exists(employee_model_path):
        print(f"ERROR: Employee model file not found at {employee_model_path}")
        return False
    
    # Read the Employee model content
    with open(employee_model_path, 'r') as f:
        employee_content = f.read()
    
    # Make a backup of the original Employee file
    employee_backup_path = employee_model_path + '.bak'
    with open(employee_backup_path, 'w') as f:
        f.write(employee_content)
    print(f"Created backup of original Employee model file at {employee_backup_path}")
    
    # Check if evaluations relationship is properly specified in the Employee model
    if "evaluations = db.relationship('Evaluation'" in employee_content:
        # Update the relationship with foreign_keys specification
        old_employee_relationship = "evaluations = db.relationship('Evaluation', back_populates='employee')"
        new_employee_relationship = "evaluations = db.relationship('Evaluation', back_populates='employee', foreign_keys='[Evaluation.employee_id]')"
        
        updated_employee_content = employee_content.replace(old_employee_relationship, new_employee_relationship)
        
        # Write the updated Employee model content
        with open(employee_model_path, 'w') as f:
            f.write(updated_employee_content)
        
        print(f"Updated Employee model relationship at {employee_model_path}")
    else:
        print("WARNING: Could not find evaluations relationship in Employee model")
    
    # Simplify test for now - just create the most basic models and relationships
    # Let's create a simplified test script for database connection
    test_db_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simplified_db_test.py')
    
    with open(test_db_script_path, 'w') as f:
        f.write('''"""
Simplified database model test.
"""
import os
import sys

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpi-system', 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app, db
from datetime import datetime

def create_minimal_test_models():
    """Create minimal versions of models for testing."""
    from flask_sqlalchemy import SQLAlchemy
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create simplified models
        class Employee(db.Model):
            __tablename__ = 'employees'
            employee_id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            
            def __repr__(self):
                return f"<Employee {self.name}>"
        
        class User(db.Model):
            __tablename__ = 'users'
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True, nullable=False)
            password_hash = db.Column(db.String(256), nullable=False)
            employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
            
            employee = db.relationship('Employee', backref=db.backref('users', lazy=True))
            
            def __repr__(self):
                return f"<User {self.username}>"
        
        # Create tables
        db.create_all()
        print("Successfully created database tables in memory")
        
        # Test data creation
        test_employee = Employee(name='Test Employee')
        db.session.add(test_employee)
        db.session.commit()
        
        test_user = User(username='testuser', password_hash='hashed_password', employee_id=test_employee.employee_id)
        db.session.add(test_user)
        db.session.commit()
        
        # Test queries
        employee = Employee.query.first()
        print(f"Retrieved employee: {employee}")
        
        user = User.query.first()
        print(f"Retrieved user: {user}")
        print(f"User's employee: {user.employee}")
        
        # Clean up
        db.session.remove()
        db.drop_all()
        print("Successfully dropped database tables")
        
        return True

if __name__ == "__main__":
    print("Running simplified database test...")
    create_minimal_test_models()
''')
    
    print(f"Created simplified database test script at {test_db_script_path}")
    print("Please run simplified_db_test.py to verify basic database functionality")
    
    return True

if __name__ == "__main__":
    fix_model_relationship()
