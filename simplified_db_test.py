"""
Simplified database model test.
"""
import os
import sys

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpi-system', 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def create_minimal_test_models():
    """Create minimal versions of models for testing."""
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    import datetime
    
    # Create a brand new Flask app and SQLAlchemy instance
    # This avoids conflicts with existing models
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    db = SQLAlchemy(app)
    
    # Define minimal versions of our models
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
    
    with app.app_context():
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

def test_actual_models():
    """Test our actual models with simplified relationships."""
    from app import create_app, db
    from sqlalchemy import MetaData
    
    # Create a test app with in-memory database
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    with app.app_context():
        # Import actual models
        from app.models.user import User
        from app.models.employee import Employee
        
        try:
            # Create tables
            db.create_all()
            print("Successfully created actual database tables in memory")
            
            # Test data creation
            test_employee = Employee(
                name='Test Employee',
                tier='apprentice',
                phone='555-1234'
            )
            db.session.add(test_employee)
            db.session.commit()
            print(f"Created employee: {test_employee}")
            
            test_user = User(
                username='testuser', 
                password='password123', 
                role='admin',
                employee_id=test_employee.employee_id
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"Created user: {test_user}")
            
            # Test queries
            employee = Employee.query.first()
            print(f"Retrieved employee: {employee}")
            
            user = User.query.filter_by(username='testuser').first()
            print(f"Retrieved user: {user}")
            print(f"User's employee: {user.employee}")
            
            # Clean up
            db.session.remove()
            db.drop_all()
            print("Successfully dropped actual database tables")
            
            return True
        except Exception as e:
            print(f"ERROR testing actual models: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RUNNING SIMPLIFIED DATABASE TEST")
    print("=" * 60)
    
    if create_minimal_test_models():
        print("\nSimplified model test PASSED")
    else:
        print("\nSimplified model test FAILED")
    
    print("\n" + "=" * 60)
    print("TESTING ACTUAL APPLICATION MODELS")
    print("=" * 60)
    
    if test_actual_models():
        print("\nActual model test PASSED")
    else:
        print("\nActual model test FAILED")
