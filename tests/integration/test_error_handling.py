"""
Integration tests for error handling in the application.
"""
import pytest

def login(client, username, password):
    """Helper function to login a user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password,
        'remember_me': False
    }, follow_redirects=True)

def test_404_error_page(client):
    """Test that 404 errors show the custom error page."""
    # Login to access protected routes
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Request a non-existent page
    response = client.get('/non-existent-page')
    
    # Verify error page is shown
    assert response.status_code == 404
    assert b'Page Not Found' in response.data
    assert b'The page you requested could not be found' in response.data
    assert b'Return to Dashboard' in response.data

def test_403_error_page(client):
    """Test that 403 errors show the custom error page."""
    # Login as employee who has limited access
    response = login(client, 'employee', 'employeepass')
    assert response.status_code == 200
    
    # Try to access admin area
    response = client.get('/admin/dashboard')
    
    # Verify error page is shown
    assert response.status_code == 403
    assert b'Access Denied' in response.data
    assert b'You do not have permission to access this resource' in response.data
    assert b'Return to Dashboard' in response.data

def test_500_error_page(client, monkeypatch):
    """Test that 500 errors show the custom error page."""
    # Login to access protected routes
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Monkeypatch a view function to raise an exception
    from kpi_system.backend.app.routes.dashboard import index as dashboard_index
    
    def mock_index():
        raise Exception("Test server error")
    
    monkeypatch.setattr(dashboard_index, "__call__", mock_index)
    
    # Request the patched route
    response = client.get('/dashboard')
    
    # Verify error page is shown
    assert response.status_code == 500
    assert b'Server Error' in response.data
    assert b'Something went wrong' in response.data
    assert b'Return to Home' in response.data

def test_form_validation_error_handling(client):
    """Test that form validation errors are handled properly."""
    # Login to access protected routes
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Submit a form with invalid data
    response = client.post('/employees/create', data={
        # Missing required fields
        'first_name': '',
        'last_name': '',
        'tier': 'invalid_tier',  # Invalid tier
        'hire_date': 'not-a-date'  # Invalid date
    })
    
    # Should stay on the form page with validation errors
    assert response.status_code == 200
    assert b'This field is required' in response.data
    assert b'Invalid tier selected' in response.data
    assert b'Invalid date format' in response.data
    
    # Form should preserve the submitted values
    assert b'value="invalid_tier"' in response.data

def test_database_error_handling(client, monkeypatch):
    """Test that database errors are handled gracefully."""
    # Login to access protected routes
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Monkeypatch SQLAlchemy session commit to raise an exception
    from kpi_system.backend.app.models import db
    
    original_commit = db.session.commit
    
    def mock_commit():
        raise Exception("Database error")
    
    monkeypatch.setattr(db.session, "commit", mock_commit)
    
    # Try to create a new employee
    response = client.post('/employees/create', data={
        'first_name': 'Test',
        'last_name': 'Employee',
        'tier': 'Apprentice',
        'hire_date': '2025-01-01',
        'active': True
    }, follow_redirects=True)
    
    # Should show error message
    assert response.status_code == 200
    assert b'An error occurred' in response.data
    assert b'Database error' in response.data
    
    # Restore original commit function
    monkeypatch.setattr(db.session, "commit", original_commit)

def test_invalid_form_submission_handling(client):
    """Test handling of invalid form submissions with missing CSRF token."""
    # Login to access protected routes
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Disable CSRF for testing
    client.application.config['WTF_CSRF_ENABLED'] = False
    
    # Submit invalid form data type
    response = client.post('/employees/create', data="not-a-form-dict", follow_redirects=True)
    
    # Should return a 400 Bad Request
    assert response.status_code == 400
    assert b'Bad Request' in response.data
    
    # Re-enable CSRF
    client.application.config['WTF_CSRF_ENABLED'] = True

def test_unauthorized_api_access(client):
    """Test that unauthorized API access is properly handled."""
    # Don't login, try to access API
    response = client.get('/api/employees')
    
    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert b'Unauthorized' in response.data
    
    # Login as employee with limited access
    response = login(client, 'employee', 'employeepass')
    assert response.status_code == 200
    
    # Try to access admin API
    response = client.get('/api/admin/users')
    
    # Should return 403 Forbidden
    assert response.status_code == 403
    assert b'Access Denied' in response.data

def test_invalid_report_parameters(client):
    """Test that invalid report parameters are handled properly."""
    # Login to access reports
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Request a report with invalid parameters
    response = client.post('/reports/employee/generate', data={
        'employee_id': '999999',  # Non-existent employee
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        'format': 'pdf'
    }, follow_redirects=True)
    
    # Should show error message
    assert response.status_code == 200
    assert b'Invalid employee selected' in response.data or b'Employee not found' in response.data
    
    # Test invalid date range
    response = client.post('/reports/employee/generate', data={
        'employee_id': '1',
        'start_date': '2025-12-31',  # End date before start date
        'end_date': '2025-01-01',
        'format': 'pdf'
    }, follow_redirects=True)
    
    # Should show error message
    assert response.status_code == 200
    assert b'End date must be after start date' in response.data or b'Invalid date range' in response.data
