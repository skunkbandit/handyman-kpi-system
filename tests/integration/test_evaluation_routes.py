"""
Integration tests for evaluation management routes.
"""
import pytest
from datetime import datetime
from kpi_system.backend.app.models.employee import Employee
from kpi_system.backend.app.models.evaluation import Evaluation, EvalSkill, EvalTool
from kpi_system.backend.app.models.skill import Skill
from kpi_system.backend.app.models.tool import Tool

def login(client, username, password):
    """Helper function to login a user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password,
        'remember_me': False
    }, follow_redirects=True)

def test_evaluation_list_page(client):
    """Test that the evaluation list page loads correctly for authenticated users."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access evaluation list
    response = client.get('/evaluations')
    assert response.status_code == 200
    assert b'Evaluations' in response.data
    assert b'Add Evaluation' in response.data

def test_evaluation_detail_page(client, db_session):
    """Test that an evaluation detail page loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an employee
    employee = db_session.query(Employee).first()
    
    # Create a test evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=1,  # Admin user ID
        evaluation_date=datetime.now().date(),
        notes="Test evaluation"
    )
    db_session.add(evaluation)
    db_session.commit()
    
    # Access evaluation detail page
    response = client.get(f'/evaluations/{evaluation.id}')
    assert response.status_code == 200
    assert b'Evaluation Details' in response.data
    assert employee.full_name.encode() in response.data
    assert b'Test evaluation' in response.data

def test_create_evaluation_form(client):
    """Test that the create evaluation form loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access create evaluation page
    response = client.get('/evaluations/create')
    assert response.status_code == 200
    assert b'New Evaluation' in response.data
    assert b'Employee' in response.data
    assert b'Evaluation Date' in response.data
    assert b'Notes' in response.data
    assert b'Skills' in response.data
    assert b'Tools' in response.data

def test_create_evaluation_submission(client, db_session):
    """Test creating a new evaluation with skills and tools."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an employee, skills, and tools
    employee = db_session.query(Employee).first()
    skills = db_session.query(Skill).limit(3).all()
    tools = db_session.query(Tool).limit(2).all()
    
    # Prepare form data
    data = {
        'employee_id': employee.id,
        'evaluation_date': datetime.now().strftime('%Y-%m-%d'),
        'notes': 'Test evaluation submission',
        'special_skills': 'Special test skill'
    }
    
    # Add skill ratings
    for skill in skills:
        data[f'skill_{skill.id}'] = 4  # Rating 4 for each skill
    
    # Add tool proficiencies
    for tool in tools:
        data[f'tool_{tool.id}_operate'] = 'on'  # Can operate
        if tool.id % 2 == 0:  # Even IDs will own the tool
            data[f'tool_{tool.id}_own'] = 'on'  # Owns tool
    
    # Submit the form
    response = client.post('/evaluations/create', data=data, follow_redirects=True)
    
    # Should redirect to evaluation list with success message
    assert response.status_code == 200
    assert b'Evaluation created successfully' in response.data
    assert employee.full_name.encode() in response.data
    
    # Verify the evaluation was created with skills and tools
    evaluation = db_session.query(Evaluation).order_by(Evaluation.id.desc()).first()
    assert evaluation is not None
    assert evaluation.employee_id == employee.id
    assert evaluation.notes == 'Test evaluation submission'
    assert evaluation.special_skills == 'Special test skill'
    assert len(evaluation.eval_skills) == 3  # 3 skills were rated
    assert len(evaluation.eval_tools) == 2  # 2 tools were evaluated

def test_edit_evaluation_form(client, db_session):
    """Test that the edit evaluation form loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an evaluation to edit
    evaluation = db_session.query(Evaluation).first()
    
    # Access edit evaluation page
    response = client.get(f'/evaluations/{evaluation.id}/edit')
    assert response.status_code == 200
    assert b'Edit Evaluation' in response.data
    assert evaluation.notes.encode() in response.data

def test_edit_evaluation_submission(client, db_session):
    """Test editing an existing evaluation."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Get an evaluation to edit
    evaluation = db_session.query(Evaluation).first()
    original_notes = evaluation.notes
    
    # Get skills and tools for the form
    skills = db_session.query(Skill).limit(3).all()
    tools = db_session.query(Tool).limit(2).all()
    
    # Prepare form data
    data = {
        'employee_id': evaluation.employee_id,
        'evaluation_date': evaluation.evaluation_date.strftime('%Y-%m-%d'),
        'notes': 'Updated evaluation notes',
        'special_skills': evaluation.special_skills or ''
    }
    
    # Add skill ratings
    for skill in skills:
        data[f'skill_{skill.id}'] = 5  # Updated rating to 5
    
    # Add tool proficiencies
    for tool in tools:
        data[f'tool_{tool.id}_operate'] = 'on'  # Can operate
        data[f'tool_{tool.id}_own'] = 'on'  # Owns tool
    
    # Submit the form
    response = client.post(f'/evaluations/{evaluation.id}/edit', data=data, follow_redirects=True)
    
    # Should redirect to evaluation detail with success message
    assert response.status_code == 200
    assert b'Evaluation updated successfully' in response.data
    assert b'Updated evaluation notes' in response.data
    
    # Reset the evaluation for other tests
    evaluation.notes = original_notes
    db_session.commit()

def test_delete_evaluation(client, db_session):
    """Test deleting an evaluation."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Create a test evaluation to delete
    employee = db_session.query(Employee).first()
    test_evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=1,  # Admin user ID
        evaluation_date=datetime.now().date(),
        notes="Delete this evaluation"
    )
    db_session.add(test_evaluation)
    db_session.commit()
    
    evaluation_id = test_evaluation.id
    
    # Delete the evaluation
    response = client.post(f'/evaluations/{evaluation_id}/delete', follow_redirects=True)
    
    # Should redirect to evaluation list with success message
    assert response.status_code == 200
    assert b'Evaluation deleted successfully' in response.data
    
    # Verify evaluation was deleted
    deleted_evaluation = db_session.query(Evaluation).filter_by(id=evaluation_id).first()
    assert deleted_evaluation is None

def test_evaluation_list_filtering(client, db_session):
    """Test filtering the evaluation list."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Filter by employee
    employee = db_session.query(Employee).first()
    response = client.get(f'/evaluations?employee_id={employee.id}')
    assert response.status_code == 200
    
    # Filter by date range
    response = client.get('/evaluations?start_date=2025-01-01&end_date=2025-12-31')
    assert response.status_code == 200

def test_manager_can_create_evaluations(client):
    """Test that managers can create evaluations."""
    # Login as manager
    response = login(client, 'manager', 'managerpass')
    assert response.status_code == 200
    
    # Access create evaluation page
    response = client.get('/evaluations/create')
    assert response.status_code == 200
    assert b'New Evaluation' in response.data

def test_employee_cannot_create_evaluations(client):
    """Test that regular employees cannot create evaluations."""
    # Login as employee
    response = login(client, 'employee', 'employeepass')
    assert response.status_code == 200
    
    # Try to access create evaluation page
    response = client.get('/evaluations/create', follow_redirects=True)
    assert response.status_code == 403
    assert b'Access Denied' in response.data

def test_employee_can_view_own_evaluations(client, db_session):
    """Test that employees can view their own evaluations but not others'."""
    # Login as employee
    response = login(client, 'employee', 'employeepass')
    assert response.status_code == 200
    
    # Get the employee linked to this user
    employee = db_session.query(Employee).filter_by(user_id=3).first()  # ID 3 is for 'employee' user
    
    # Create an evaluation for this employee
    own_evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=2,  # Manager user ID
        evaluation_date=datetime.now().date(),
        notes="Employee's own evaluation"
    )
    db_session.add(own_evaluation)
    
    # Create an evaluation for another employee
    other_employee = db_session.query(Employee).filter(Employee.id != employee.id).first()
    other_evaluation = Evaluation(
        employee_id=other_employee.id,
        evaluator_id=2,  # Manager user ID
        evaluation_date=datetime.now().date(),
        notes="Another employee's evaluation"
    )
    db_session.add(other_evaluation)
    db_session.commit()
    
    # Access own evaluation - should be allowed
    response = client.get(f'/evaluations/{own_evaluation.id}')
    assert response.status_code == 200
    assert b"Employee's own evaluation" in response.data
    
    # Access another employee's evaluation - should be restricted
    response = client.get(f'/evaluations/{other_evaluation.id}')
    assert response.status_code == 403
    assert b'Access Denied' in response.data
