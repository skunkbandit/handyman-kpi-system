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