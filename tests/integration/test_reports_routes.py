"""
Integration tests for report generation routes.
"""
import pytest
import json
from io import BytesIO
from kpi_system.backend.app.models.evaluation import Evaluation

def login(client, username, password):
    """Helper function to login a user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password,
        'remember_me': False
    }, follow_redirects=True)

def test_reports_index_page(client):
    """Test that the reports index page loads correctly for authenticated users."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access reports index
    response = client.get('/reports')
    assert response.status_code == 200
    assert b'Reports' in response.data
    assert b'Employee Performance Report' in response.data
    assert b'Team Performance Report' in response.data
    assert b'Skills Analysis Report' in response.data
    assert b'Tool Inventory Report' in response.data

def test_employee_report_form(client, db_session):
    """Test that the employee report form loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access employee report form
    response = client.get('/reports/employee')
    assert response.status_code == 200
    assert b'Employee Performance Report' in response.data
    assert b'Select Employee' in response.data
    assert b'Date Range' in response.data
    assert b'Include Skills' in response.data
    assert b'Include Tools' in response.data

def test_employee_report_generation(client, db_session):
    """Test generating an employee performance report."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get the first employee from the database
    from kpi_system.backend.app.models.employee import Employee
    employee = db_session.query(Employee).first()
    
    # Generate PDF report
    response = client.post('/reports/employee/generate', data={
        'employee_id': employee.id,
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        'include_skills': True,
        'include_tools': True,
        'format': 'pdf'
    })
    
    # Check if response is a PDF file
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert b'%PDF' in response.data  # PDF file signature
    
    # Generate Excel report
    response = client.post('/reports/employee/generate', data={
        'employee_id': employee.id,
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        'include_skills': True,
        'include_tools': True,
        'format': 'excel'
    })
    
    # Check if response is an Excel file
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # Excel file signature bytes
    assert response.data[:4] == b'PK\x03\x04'  # ZIP file signature (XLSX is a ZIP file)

def test_team_report_form(client):
    """Test that the team report form loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access team report form
    response = client.get('/reports/team')
    assert response.status_code == 200
    assert b'Team Performance Report' in response.data
    assert b'Select Tier' in response.data
    assert b'Date Range' in response.data
    assert b'Group By' in response.data
    assert b'Include Inactive Employees' in response.data

def test_team_report_generation(client):
    """Test generating a team performance report."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Generate PDF report
    response = client.post('/reports/team/generate', data={
        'tier': 'all',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        'group_by': 'tier',
        'include_inactive': False,
        'format': 'pdf'
    })
    
    # Check if response is a PDF file
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert b'%PDF' in response.data
    
    # Generate Excel report
    response = client.post('/reports/team/generate', data={
        'tier': 'all',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        'group_by': 'tier',
        'include_inactive': False,
        'format': 'excel'
    })
    
    # Check if response is an Excel file
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.data[:4] == b'PK\x03\x04'

def test_skills_report_form(client):
    """Test that the skills report form loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access skills report form
    response = client.get('/reports/skills')
    assert response.status_code == 200
    assert b'Skills Analysis Report' in response.data
    assert b'Skill Category' in response.data
    assert b'Date Range' in response.data
    assert b'Minimum Rating' in response.data

def test_skills_report_generation(client, db_session):
    """Test generating a skills analysis report."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get the first skill category
    from kpi_system.backend.app.models.skill import SkillCategory
    category = db_session.query(SkillCategory).first()
    
    # Generate PDF report
    response = client.post('/reports/skills/generate', data={
        'category_id': category.id if category else 'all',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        'min_rating': 3,
        'format': 'pdf'
    })
    
    # Check if response is a PDF file
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert b'%PDF' in response.data
    
    # Generate Excel report
    response = client.post('/reports/skills/generate', data={
        'category_id': category.id if category else 'all',
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        'min_rating': 3,
        'format': 'excel'
    })
    
    # Check if response is an Excel file
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.data[:4] == b'PK\x03\x04'

def test_tools_report_form(client):
    """Test that the tools report form loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access tools report form
    response = client.get('/reports/tools')
    assert response.status_code == 200
    assert b'Tool Inventory Report' in response.data
    assert b'Tool Category' in response.data
    assert b'Show Can Operate' in response.data
    assert b'Show Owns Tool' in response.data

def test_tools_report_generation(client, db_session):
    """Test generating a tool inventory report."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get the first tool category
    from kpi_system.backend.app.models.tool import ToolCategory
    category = db_session.query(ToolCategory).first()
    
    # Generate PDF report
    response = client.post('/reports/tools/generate', data={
        'category_id': category.id if category else 'all',
        'show_can_operate': True,
        'show_has_tool': True,
        'tier': 'all',
        'format': 'pdf'
    })
    
    # Check if response is a PDF file
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert b'%PDF' in response.data
    
    # Generate Excel report
    response = client.post('/reports/tools/generate', data={
        'category_id': category.id if category else 'all',
        'show_can_operate': True,
        'show_has_tool': True,
        'tier': 'all',
        'format': 'excel'
    })
    
    # Check if response is an Excel file
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.data[:4] == b'PK\x03\x04'

def test_report_access_permissions(client):
    """Test that only authorized users can access reports."""
    # Test as employee (should not have access)
    response = login(client, 'employee', 'employeepass')
    assert response.status_code == 200
    
    response = client.get('/reports', follow_redirects=True)
    assert response.status_code == 403
    assert b'Access Denied' in response.data
    
    # Test as manager (should have access)
    response = login(client, 'manager', 'managerpass')
    assert response.status_code == 200
    
    response = client.get('/reports')
    assert response.status_code == 200
    assert b'Reports' in response.data
    
    # Test specific report pages
    assert client.get('/reports/employee').status_code == 200
    assert client.get('/reports/team').status_code == 200
    assert client.get('/reports/skills').status_code == 200
    assert client.get('/reports/tools').status_code == 200

def test_report_api_endpoints(client):
    """Test the report API endpoints for AJAX requests."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Test employee list endpoint
    response = client.get('/api/employees')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'id' in data[0]
    assert 'name' in data[0]
    
    # Test skill categories endpoint
    response = client.get('/api/skill-categories')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'id' in data[0]
    assert 'name' in data[0]
    
    # Test tool categories endpoint
    response = client.get('/api/tool-categories')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'id' in data[0]
    assert 'name' in data[0]
