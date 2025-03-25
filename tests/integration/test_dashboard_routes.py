"""
Integration tests for dashboard and reporting routes.
"""
import pytest
from kpi_system.backend.app.models.employee import Employee
from kpi_system.backend.app.models.evaluation import Evaluation

def login(client, username, password):
    """Helper function to login a user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password,
        'remember_me': False
    }, follow_redirects=True)

def test_dashboard_access(client):
    """Test that authenticated users can access the dashboard."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    assert b'Recent Evaluations' in response.data

def test_dashboard_content(client, db_session):
    """Test that the dashboard contains expected KPI content."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200
    
    # Check for dashboard components
    assert b'Performance Overview' in response.data
    assert b'Skill Distribution' in response.data
    assert b'Progress Over Time' in response.data
    assert b'Top Skills' in response.data
    assert b'Improvement Areas' in response.data

def test_dashboard_filtering(client, db_session):
    """Test dashboard filtering by employee, category, and date range."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an employee to filter by
    employee = db_session.query(Employee).first()
    
    # Access dashboard with employee filter
    response = client.get(f'/dashboard?employee_id={employee.id}')
    assert response.status_code == 200
    assert employee.full_name.encode() in response.data
    
    # Filter by category
    response = client.get('/dashboard?category=Carpentry')
    assert response.status_code == 200
    assert b'Carpentry' in response.data
    
    # Filter by tier
    response = client.get('/dashboard?tier=Craftsman')
    assert response.status_code == 200
    assert b'Craftsman' in response.data
    
    # Filter by date range
    response = client.get('/dashboard?start_date=2025-01-01&end_date=2025-12-31')
    assert response.status_code == 200

def test_dashboard_charts(client):
    """Test that dashboard charts load correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200
    
    # Check for chart elements
    assert b'chart-skill-distribution' in response.data
    assert b'chart-progress' in response.data
    
    # Check for chart initialization JavaScript
    assert b'new Chart(' in response.data

def test_employee_dashboard(client, db_session):
    """Test that employees see a personalized dashboard."""
    # Login as employee
    response = login(client, 'employee', 'employeepass')
    assert response.status_code == 200
    
    # Access dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200
    
    # Get the employee linked to this user
    employee = db_session.query(Employee).filter_by(user_id=3).first()  # ID 3 is for 'employee' user
    
    # Check for personalized content
    assert employee.full_name.encode() in response.data
    assert b'Your Performance' in response.data
    assert b'Skill Progress' in response.data

def test_reports_index_page(client):
    """Test that the reports index page loads correctly."""
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

def test_employee_performance_report(client, db_session):
    """Test generating an employee performance report."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an employee
    employee = db_session.query(Employee).first()
    
    # Generate report
    response = client.get(f'/reports/employee/{employee.id}')
    assert response.status_code == 200
    assert employee.full_name.encode() in response.data
    assert b'Performance Report' in response.data
    assert b'Skill Ratings' in response.data
    assert b'Tool Proficiency' in response.data
    assert b'Progress Over Time' in response.data

def test_team_performance_report(client):
    """Test generating a team performance report."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Generate report
    response = client.get('/reports/team')
    assert response.status_code == 200
    assert b'Team Performance Report' in response.data
    assert b'Comparative Analysis' in response.data
    assert b'Team Averages' in response.data
    assert b'Performance by Tier' in response.data

def test_skills_analysis_report(client):
    """Test generating a skills analysis report."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Generate report
    response = client.get('/reports/skills')
    assert response.status_code == 200
    assert b'Skills Analysis Report' in response.data
    assert b'Skill Distribution' in response.data
    assert b'Skill Gaps' in response.data
    assert b'Training Recommendations' in response.data

def test_tool_inventory_report(client):
    """Test generating a tool inventory report."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Generate report
    response = client.get('/reports/tools')
    assert response.status_code == 200
    assert b'Tool Inventory Report' in response.data
    assert b'Tool Proficiency' in response.data
    assert b'Tool Ownership' in response.data
    assert b'Training Needs' in response.data

def test_pdf_export(client, db_session):
    """Test exporting a report as PDF."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an employee
    employee = db_session.query(Employee).first()
    
    # Export as PDF
    response = client.get(f'/reports/employee/{employee.id}/export?format=pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=')

def test_excel_export(client, db_session):
    """Test exporting a report as Excel."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an employee
    employee = db_session.query(Employee).first()
    
    # Export as Excel
    response = client.get(f'/reports/employee/{employee.id}/export?format=excel')
    assert response.status_code == 200
    assert response.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=')

def test_manager_can_access_reports(client):
    """Test that managers can access reports."""
    # Login as manager
    response = login(client, 'manager', 'managerpass')
    assert response.status_code == 200
    
    # Access reports index
    response = client.get('/reports')
    assert response.status_code == 200
    assert b'Reports' in response.data

def test_employee_cannot_access_reports(client):
    """Test that regular employees cannot access reports."""
    # Login as employee
    response = login(client, 'employee', 'employeepass')
    assert response.status_code == 200
    
    # Try to access reports index
    response = client.get('/reports', follow_redirects=True)
    assert response.status_code == 403
    assert b'Access Denied' in response.data
