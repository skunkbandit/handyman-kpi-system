"""
Access control middleware for the KPI system
"""
from functools import wraps
from flask import current_app, flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict access to admin users
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.role == 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """
    Decorator to restrict access to manager users
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.role in ['admin', 'manager']:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def employee_owner_required(f):
    """
    Decorator to restrict access to the owner of the employee record or managers/admins
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check if user is admin or manager
        if current_user.role in ['admin', 'manager']:
            return f(*args, **kwargs)
        
        # Employee can only access their own data
        employee_id = kwargs.get('employee_id')
        if employee_id and current_user.employee_id == employee_id:
            return f(*args, **kwargs)
        
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return decorated_function
