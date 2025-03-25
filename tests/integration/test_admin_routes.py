"""
Integration tests for admin routes.
"""
import pytest
import json
import os
from datetime import datetime
from kpi_system.backend.app.models.user import User

def login(client, username, password):
    """Helper function to login a user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password,
        'remember_me': False
    }, follow_redirects=True)

def test_admin_dashboard_access(client):
    """Test that only admins can access the admin dashboard."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access admin dashboard
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Administration' in response.data
    assert b'System Status' in response.data
    
    # Logout and login as manager
    client.get('/auth/logout')
    login(client, 'manager', 'managerpass')
    
    # Try to access admin dashboard as manager
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert response.status_code == 403
    assert b'Access Denied' in response.data
    
    # Logout and login as employee
    client.get('/auth/logout')
    login(client, 'employee', 'employeepass')
    
    # Try to access admin dashboard as employee
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert response.status_code == 403
    assert b'Access Denied' in response.data

def test_admin_dashboard_content(client):
    """Test that the admin dashboard contains expected content."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access admin dashboard
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    
    # Check for dashboard components
    assert b'System Status' in response.data
    assert b'User Statistics' in response.data
    assert b'Database Metrics' in response.data
    assert b'Storage Usage' in response.data
    assert b'Recent Activity' in response.data

def test_system_settings_page(client):
    """Test that the system settings page loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access system settings
    response = client.get('/admin/settings')
    assert response.status_code == 200
    assert b'System Settings' in response.data
    assert b'Company Information' in response.data
    assert b'Email Settings' in response.data
    assert b'Security Settings' in response.data

def test_update_system_settings(client, monkeypatch):
    """Test updating system settings."""
    # Mock the settings file path for testing
    test_settings_file = 'test_settings.json'
    monkeypatch.setattr('kpi_system.backend.app.routes.admin.SETTINGS_FILE', test_settings_file)
    
    # Create an initial settings file
    initial_settings = {
        'company_name': 'Test Company',
        'email': {
            'sender': 'test@example.com',
            'smtp_server': 'smtp.example.com'
        },
        'security': {
            'session_timeout': 30,
            'password_complexity': 'medium'
        }
    }
    
    with open(test_settings_file, 'w') as f:
        json.dump(initial_settings, f)
    
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Update settings
    response = client.post('/admin/settings', data={
        'company_name': 'Updated Company',
        'email_sender': 'updated@example.com',
        'smtp_server': 'smtp.updated.com',
        'session_timeout': '60',
        'password_complexity': 'high'
    }, follow_redirects=True)
    
    # Should show success message
    assert response.status_code == 200
    assert b'Settings updated successfully' in response.data
    
    # Verify settings were updated in the file
    with open(test_settings_file, 'r') as f:
        updated_settings = json.load(f)
    
    assert updated_settings['company_name'] == 'Updated Company'
    assert updated_settings['email']['sender'] == 'updated@example.com'
    assert updated_settings['email']['smtp_server'] == 'smtp.updated.com'
    assert updated_settings['security']['session_timeout'] == 60
    assert updated_settings['security']['password_complexity'] == 'high'
    
    # Clean up
    os.remove(test_settings_file)

def test_backup_page(client):
    """Test that the backup page loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access backup page
    response = client.get('/admin/backups')
    assert response.status_code == 200
    assert b'Database Backups' in response.data
    assert b'Create Backup' in response.data
    assert b'Restore Backup' in response.data

def test_create_backup(client, monkeypatch, tmp_path):
    """Test creating a database backup."""
    # Mock the backup directory for testing
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setattr('kpi_system.backend.app.routes.admin.BACKUP_DIR', str(backup_dir))
    
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Create a backup
    response = client.post('/admin/backups/create', data={
        'name': 'Test Backup',
        'description': 'Backup for testing'
    }, follow_redirects=True)
    
    # Should show success message
    assert response.status_code == 200
    assert b'Backup created successfully' in response.data
    
    # Verify backup was created
    backup_files = list(backup_dir.glob('*.sqlite'))
    assert len(backup_files) > 0

def test_user_management_page(client):
    """Test that the user management page loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access user management page
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b'User Management' in response.data
    assert b'Add User' in response.data
    assert b'admin' in response.data
    assert b'manager' in response.data
    assert b'employee' in response.data

def test_create_user(client, db_session):
    """Test creating a new user."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Create a new user
    response = client.post('/admin/users/create', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword',
        'role': 'manager'
    }, follow_redirects=True)
    
    # Should show success message
    assert response.status_code == 200
    assert b'User created successfully' in response.data
    
    # Verify user was created
    user = db_session.query(User).filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'new@example.com'
    assert user.role == 'manager'
    
    # Clean up
    db_session.delete(user)
    db_session.commit()

def test_edit_user(client, db_session):
    """Test editing an existing user."""
    # Create a test user
    test_user = User(
        username='testuser',
        email='test@example.com',
        role='employee'
    )
    test_user.set_password('testpass')
    db_session.add(test_user)
    db_session.commit()
    
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Edit the user
    response = client.post(f'/admin/users/{test_user.id}/edit', data={
        'username': 'testuser',  # Keep the same
        'email': 'updated@example.com',
        'role': 'manager'
    }, follow_redirects=True)
    
    # Should show success message
    assert response.status_code == 200
    assert b'User updated successfully' in response.data
    
    # Verify user was updated
    user = db_session.query(User).filter_by(id=test_user.id).first()
    assert user.email == 'updated@example.com'
    assert user.role == 'manager'
    
    # Clean up
    db_session.delete(user)
    db_session.commit()

def test_reset_user_password(client, db_session):
    """Test resetting a user's password."""
    # Create a test user
    test_user = User(
        username='resetuser',
        email='reset@example.com',
        role='employee'
    )
    test_user.set_password('oldpassword')
    db_session.add(test_user)
    db_session.commit()
    
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Reset the password
    response = client.post(f'/admin/users/{test_user.id}/reset_password', data={
        'new_password': 'newpassword',
        'confirm_password': 'newpassword'
    }, follow_redirects=True)
    
    # Should show success message
    assert response.status_code == 200
    assert b'Password reset successfully' in response.data
    
    # Verify password was reset
    user = db_session.query(User).filter_by(id=test_user.id).first()
    assert user.check_password('newpassword')
    assert not user.check_password('oldpassword')
    
    # Clean up
    db_session.delete(user)
    db_session.commit()

def test_database_maintenance_page(client):
    """Test that the database maintenance page loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access database maintenance page
    response = client.get('/admin/maintenance')
    assert response.status_code == 200
    assert b'Database Maintenance' in response.data
    assert b'Optimize Database' in response.data
    assert b'Clean Old Data' in response.data
    assert b'Check Database Integrity' in response.data
    assert b'Import/Export Data' in response.data

def test_system_logs_page(client):
    """Test that the system logs page loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access system logs page
    response = client.get('/admin/logs')
    assert response.status_code == 200
    assert b'System Logs' in response.data
    assert b'Log Viewer' in response.data
    assert b'Log Management' in response.data

def test_system_health_page(client):
    """Test that the system health page loads correctly."""
    # Login as admin
    response = login(client, 'admin', 'adminpass')
    assert response.status_code == 200
    
    # Access system health page
    response = client.get('/admin/health')
    assert response.status_code == 200
    assert b'System Health' in response.data
    assert b'System Status' in response.data
    assert b'Disk Usage' in response.data
    assert b'Database Health' in response.data
    assert b'User Activity' in response.data
