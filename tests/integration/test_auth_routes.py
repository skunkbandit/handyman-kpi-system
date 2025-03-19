"""
Integration tests for authentication routes.
"""
import pytest
from flask import session
from kpi_system.backend.app.models.user import User

def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data
    assert b'Remember Me' in response.data

def test_successful_login(client, db_session):
    """Test successful login with valid credentials."""
    # Ensure we have a test user
    user = db_session.query(User).filter_by(username='admin').first()
    assert user is not None
    
    # Attempt login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'adminpass',
        'remember_me': False
    }, follow_redirects=True)
    
    # Check redirect to dashboard after login
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    # Check for success message
    assert b'Logged in successfully' in response.data
    
    # Check session contains user_id
    with client.session_transaction() as sess:
        assert 'user_id' in sess
        assert sess['user_id'] == user.id

def test_failed_login_invalid_username(client):
    """Test login failure with invalid username."""
    response = client.post('/auth/login', data={
        'username': 'nonexistentuser',
        'password': 'password',
        'remember_me': False
    }, follow_redirects=True)
    
    # Should stay on login page
    assert response.status_code == 200
    assert b'Login' in response.data
    # Check for error message
    assert b'Invalid username or password' in response.data
    
    # Check session does not contain user_id
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_failed_login_invalid_password(client, db_session):
    """Test login failure with invalid password."""
    # Ensure we have a test user
    user = db_session.query(User).filter_by(username='admin').first()
    assert user is not None
    
    # Attempt login with wrong password
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'wrongpassword',
        'remember_me': False
    }, follow_redirects=True)
    
    # Should stay on login page
    assert response.status_code == 200
    assert b'Login' in response.data
    # Check for error message
    assert b'Invalid username or password' in response.data
    
    # Check session does not contain user_id
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_logout(client, db_session):
    """Test logout functionality."""
    # First login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'adminpass',
        'remember_me': False
    }, follow_redirects=True)
    
    # Verify login was successful
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    
    # Now logout
    response = client.get('/auth/logout', follow_redirects=True)
    
    # Should redirect to login page
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'You have been logged out' in response.data
    
    # Check session no longer contains user_id
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_login_required_protection(client):
    """Test that protected routes redirect to login when not authenticated."""
    # Try to access the dashboard without logging in
    response = client.get('/dashboard', follow_redirects=True)
    
    # Should redirect to login page
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Please log in to access this page' in response.data

def test_password_change(client, db_session):
    """Test password change functionality."""
    # First login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'adminpass',
        'remember_me': False
    }, follow_redirects=True)
    
    # Verify login was successful
    assert response.status_code == 200
    
    # Now try to change password
    response = client.post('/auth/change_password', data={
        'current_password': 'adminpass',
        'new_password': 'newadminpass',
        'confirm_password': 'newadminpass'
    }, follow_redirects=True)
    
    # Should show success message
    assert response.status_code == 200
    assert b'Password changed successfully' in response.data
    
    # Logout
    response = client.get('/auth/logout', follow_redirects=True)
    
    # Try logging in with the new password
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'newadminpass',
        'remember_me': False
    }, follow_redirects=True)
    
    # Verify login with new password works
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    
    # Reset the password for other tests
    user = db_session.query(User).filter_by(username='admin').first()
    user.set_password('adminpass')
    db_session.commit()

def test_password_change_wrong_current_password(client):
    """Test password change fails with wrong current password."""
    # First login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'adminpass',
        'remember_me': False
    }, follow_redirects=True)
    
    # Verify login was successful
    assert response.status_code == 200
    
    # Now try to change password with wrong current password
    response = client.post('/auth/change_password', data={
        'current_password': 'wrongpassword',
        'new_password': 'newadminpass',
        'confirm_password': 'newadminpass'
    }, follow_redirects=True)
    
    # Should show error message
    assert response.status_code == 200
    assert b'Current password is incorrect' in response.data

def test_password_change_password_mismatch(client):
    """Test password change fails when new password and confirmation don't match."""
    # First login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'adminpass',
        'remember_me': False
    }, follow_redirects=True)
    
    # Verify login was successful
    assert response.status_code == 200
    
    # Now try to change password with mismatched new passwords
    response = client.post('/auth/change_password', data={
        'current_password': 'adminpass',
        'new_password': 'newadminpass',
        'confirm_password': 'differentpassword'
    }, follow_redirects=True)
    
    # Should show error message
    assert response.status_code == 200
    assert b'New password and confirmation must match' in response.data

def test_forgot_password_page(client):
    """Test that the forgot password page loads correctly."""
    response = client.get('/auth/forgot_password')
    assert response.status_code == 200
    assert b'Forgot Password' in response.data
    assert b'Email' in response.data

def test_forgot_password_submission(client, db_session):
    """Test forgot password functionality."""
    # Submit forgot password request
    response = client.post('/auth/forgot_password', data={
        'email': 'admin@example.com'
    }, follow_redirects=True)
    
    # Should show success message even if email doesn't exist (security)
    assert response.status_code == 200
    assert b'Password reset instructions have been sent' in response.data

def test_role_based_access_admin_only(client):
    """Test that admin-only routes are protected."""
    # First login as a regular employee
    response = client.post('/auth/login', data={
        'username': 'employee',
        'password': 'employeepass',
        'remember_me': False
    }, follow_redirects=True)
    
    # Verify login was successful
    assert response.status_code == 200
    
    # Try to access admin-only route
    response = client.get('/admin/dashboard', follow_redirects=True)
    
    # Should show access denied
    assert response.status_code == 403
    assert b'Access Denied' in response.data
    assert b'You do not have permission to access this page' in response.data