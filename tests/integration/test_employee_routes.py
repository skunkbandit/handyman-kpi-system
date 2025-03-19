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