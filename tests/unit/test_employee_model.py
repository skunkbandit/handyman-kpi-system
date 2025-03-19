"""
Unit tests for the Employee model.
"""
import pytest
from datetime import datetime, timedelta
from kpi_system.backend.app.models.employee import Employee

def test_employee_creation(db_session):
    """Test creating a new employee."""
    employee = Employee(
        first_name="Test",
        last_name="Employee",
        tier="Handyman",
        hire_date=datetime.now().date(),
        active=True
    )
    
    db_session.add(employee)
    db_session.commit()
    
    # Retrieve the employee from the database
    saved_employee = db_session.query(Employee).filter_by(id=employee.id).first()
    
    # Verify the employee data was saved correctly
    assert saved_employee is not None
    assert saved_employee.first_name == "Test"
    assert saved_employee.last_name == "Employee"
    assert saved_employee.tier == "Handyman"
    assert saved_employee.active is True
    assert saved_employee.full_name == "Test Employee"

def test_employee_tier_validation(db_session):
    """Test that employee tier must be a valid tier."""
    # Create an employee with an invalid tier
    employee = Employee(
        first_name="Invalid",
        last_name="Tier",
        tier="Not A Tier",
        hire_date=datetime.now().date(),
        active=True
    )
    
    # Add the employee to the session
    db_session.add(employee)
    
    # Committing should raise an exception because of the validation
    with pytest.raises(ValueError):
        db_session.commit()
        
    # Rollback the session to clean up
    db_session.rollback()

def test_employee_full_name_property(db_session):
    """Test the full_name property returns the correct value."""
    employee = Employee(
        first_name="John",
        last_name="Doe",
        tier="Craftsman",
        hire_date=datetime.now().date(),
        active=True
    )
    
    assert employee.full_name == "John Doe"
    
    # Change the name and ensure the property updates
    employee.first_name = "Jane"
    assert employee.full_name == "Jane Doe"

def test_employee_experience_calculation(db_session):
    """Test that employee experience is calculated correctly."""
    # Create an employee with a hire date one year ago
    hire_date = (datetime.now() - timedelta(days=365)).date()
    employee = Employee(
        first_name="Experienced",
        last_name="Employee",
        tier="Apprentice",
        hire_date=hire_date,
        active=True
    )
    
    # The experience should be approximately 1 year
    experience = employee.experience
    assert experience >= 0.9 and experience <= 1.1
    
    # Create a new employee with a recent hire date
    new_hire_date = datetime.now().date()
    new_employee = Employee(
        first_name="New",
        last_name="Employee",
        tier="Apprentice",
        hire_date=new_hire_date,
        active=True
    )
    
    # A new employee should have close to 0 years of experience
    assert new_employee.experience < 0.1

def test_employee_deactivation(db_session):
    """Test deactivating an employee."""
    employee = Employee(
        first_name="Active",
        last_name="Employee",
        tier="Master Craftsman",
        hire_date=datetime.now().date(),
        active=True
    )
    
    db_session.add(employee)
    db_session.commit()
    
    # Verify the employee is active
    assert employee.active is True
    
    # Deactivate the employee
    employee.active = False
    db_session.commit()
    
    # Retrieve the employee from the database and verify
    saved_employee = db_session.query(Employee).filter_by(id=employee.id).first()
    assert saved_employee.active is False

def test_employee_tier_advancement(db_session):
    """Test advancing an employee's tier."""
    employee = Employee(
        first_name="Career",
        last_name="Growth",
        tier="Apprentice",
        hire_date=datetime.now().date(),
        active=True
    )
    
    db_session.add(employee)
    db_session.commit()
    
    # Verify the initial tier
    assert employee.tier == "Apprentice"
    
    # Advance the tier
    employee.tier = "Handyman"
    db_session.commit()
    
    # Retrieve the employee from the database and verify
    saved_employee = db_session.query(Employee).filter_by(id=employee.id).first()
    assert saved_employee.tier == "Handyman"