import unittest
from datetime import datetime, date
from app import create_app, db
from app.models.user import User
from app.models.employee import Employee

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        # Create a test app with in-memory SQLite database
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_model(self):
        # Create a test user
        user = User(username='testuser', password='password123', role='admin')
        db.session.add(user)
        db.session.commit()
        
        # Test retrieval
        retrieved_user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, 'testuser')
        self.assertEqual(retrieved_user.role, 'admin')
        
        # Test password hashing
        self.assertTrue(retrieved_user.verify_password('password123'))
        self.assertFalse(retrieved_user.verify_password('wrongpassword'))
        
        # Test role checking
        self.assertTrue(retrieved_user.is_admin())
        self.assertTrue(retrieved_user.is_manager())
        self.assertFalse(retrieved_user.is_employee())
    
    def test_employee_model(self):
        # Create a test employee
        employee = Employee(
            name='John Doe',
            phone='555-1234',
            tier='craftsman',
            hire_date=date(2023, 1, 15),
            active=True
        )
        db.session.add(employee)
        db.session.commit()
        
        # Test retrieval
        retrieved_employee = Employee.query.filter_by(name='John Doe').first()
        self.assertIsNotNone(retrieved_employee)
        self.assertEqual(retrieved_employee.name, 'John Doe')
        self.assertEqual(retrieved_employee.tier, 'craftsman')
        self.assertEqual(retrieved_employee.phone, '555-1234')
        self.assertEqual(retrieved_employee.hire_date, date(2023, 1, 15))
        self.assertTrue(retrieved_employee.active)
        
        # Test to_dict method
        employee_dict = retrieved_employee.to_dict()
        self.assertEqual(employee_dict['name'], 'John Doe')
        self.assertEqual(employee_dict['tier'], 'craftsman')
        self.assertEqual(employee_dict['phone'], '555-1234')
        self.assertEqual(employee_dict['hire_date'], '2023-01-15')
        self.assertTrue(employee_dict['active'])
    
    def test_user_employee_relationship(self):
        # Create an employee
        employee = Employee(
            name='Jane Smith',
            phone='555-5678',
            tier='master craftsman',
            hire_date=date(2022, 3, 10),
            active=True
        )
        db.session.add(employee)
        db.session.commit()
        
        # Create a user linked to the employee
        user = User(
            username='janesmith',
            password='securepass',
            role='employee',
            employee_id=employee.employee_id
        )
        db.session.add(user)
        db.session.commit()
        
        # Test the relationship from user to employee
        retrieved_user = User.query.filter_by(username='janesmith').first()
        self.assertIsNotNone(retrieved_user.employee)
        self.assertEqual(retrieved_user.employee.name, 'Jane Smith')
        
        # Test the relationship from employee to user
        retrieved_employee = Employee.query.filter_by(name='Jane Smith').first()
        self.assertIsNotNone(retrieved_employee.user)
        self.assertEqual(retrieved_employee.user.username, 'janesmith')

if __name__ == '__main__':
    unittest.main()