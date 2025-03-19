"""
Integration tests for employee management routes.
"""
import pytest
from kpi_system.backend.app.models.employee import Employee

def login(client, username, password):
    """Helper function to login a user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password,
        'remember_me': False
    }, follow_redirects=True)

def test_employee_list_page(client):
    """Test that the employee list page loads correctly for authenticated users."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access employee list
    response = client.get('/employees')
    assert response.status_code == 200
    assert b'Employees' in response.data
    assert b'John Doe' in response.data
    assert b'Jane Smith' in response.data
    assert b'Add Employee' in response.data

def test_employee_detail_page(client, db_session):
    """Test that an employee detail page loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an employee
    employee = db_session.query(Employee).first()
    
    # Access employee detail page
    response = client.get(f'/employees/{employee.id}')
    assert response.status_code == 200
    assert employee.first_name.encode() in response.data
    assert employee.last_name.encode() in response.data
    assert employee.tier.encode() in response.data

def test_create_employee_form(client):
    """Test that the create employee form loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access create employee page
    response = client.get('/employees/create')
    assert response.status_code == 200
    assert b'Add New Employee' in response.data
    assert b'First Name' in response.data
    assert b'Last Name' in response.data
    assert b'Tier' in response.data
    assert b'Hire Date' in response.data

def test_create_employee_submission(client):
    """Test creating a new employee."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Submit new employee form
    response = client.post('/employees/create', data={
        'first_name': 'Test',
        'last_name': 'Employee',
        'tier': 'Apprentice',
        'hire_date': '2025-03-01',
        'active': True
    }, follow_redirects=True)
    
    # Should redirect to employee list with success message
    assert response.status_code == 200
    assert b'Employee created successfully' in response.data
    assert b'Test Employee' in response.data

def test_edit_employee_form(client, db_session):
    """Test that the edit employee form loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an employee
    employee = db_session.query(Employee).first()
    
    # Access edit employee page
    response = client.get(f'/employees/{employee.id}/edit')
    assert response.status_code == 200
    assert b'Edit Employee' in response.data
    assert employee.first_name.encode() in response.data
    assert employee.last_name.encode() in response.data

def test_edit_employee_submission(client, db_session):
    """Test editing an existing employee."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an employee
    employee = db_session.query(Employee).first()
    original_first_name = employee.first_name
    
    # Submit edit employee form
    response = client.post(f'/employees/{employee.id}/edit', data={
        'first_name': 'Updated',
        'last_name': employee.last_name,
        'tier': employee.tier,
        'hire_date': employee.hire_date,
        'active': employee.active
    }, follow_redirects=True)
    
    # Should redirect to employee detail with success message
    assert response.status_code == 200
    assert b'Employee updated successfully' in response.data
    assert b'Updated' in response.data
    
    # Reset the employee for other tests
    employee.first_name = original_first_name
    db_session.commit()

def test_delete_employee(client, db_session):
    """Test deleting an employee."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Create a test employee to delete
    test_employee = Employee(
        first_name="Delete",
        last_name="Me",
        tier="Apprentice",
        hire_date="2025-01-01",
        active=True
    )
    db_session.add(test_employee)
    db_session.commit()
    
    employee_id = test_employee.id
    
    # Delete the employee
    response = client.post(f'/employees/{employee_id}/delete', follow_redirects=True)
    
    # Should redirect to employee list with success message
    assert response.status_code == 200
    assert b'Employee deleted successfully' in response.data
    
    # Verify employee was deleted
    deleted_employee = db_session.query(Employee).filter_by(id=employee_id).first()
    assert deleted_employee is None

def test_employee_list_filtering(client, db_session):
    """Test filtering the employee list."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Filter by tier
    response = client.get('/employees?tier=Craftsman')
    assert response.status_code == 200
    assert b'Craftsman' in response.data
    
    # Filter by active status
    response = client.get('/employees?active=true')
    assert response.status_code == 200
    
    # Search by name
    response = client.get('/employees?search=John')
    assert response.status_code == 200
    assert b'John' in response.data

def test_manager_permissions(client):
    """Test that managers can view employees but not admin functions."""
    # Login as manager
    response = login(client, 'manager', 'managerpass')
    assert response.status_code == 200
    
    # Access employee list - should be allowed
    response = client.get('/employees')
    assert response.status_code == 200
    assert b'Employees' in response.data
    
    # Access admin dashboard - should be forbidden
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert response.status_code == 403
    assert b'Access Denied' in response.data

def test_employee_permissions(client, db_session):
    """Test that employees can only view their own profile."""
    # Login as regular employee
    response = login(client, 'employee', 'employeepass')
    assert response.status_code == 200
    
    # Get the employee linked to this user
    employee_user = db_session.query(Employee).filter_by(user_id=3).first()  # ID 3 is for 'employee' user
    
    # Access own employee profile - should be allowed
    response = client.get(f'/employees/{employee_user.id}')
    assert response.status_code == 200
    
    # Access employee list - should be restricted
    response = client.get('/employees')
    assert response.status_code == 403
    
    # Access another employee's profile - should be restricted
    other_employee = db_session.query(Employee).filter(Employee.id != employee_user.id).first()
    response = client.get(f'/employees/{other_employee.id}')
    assert response.status_code == 403