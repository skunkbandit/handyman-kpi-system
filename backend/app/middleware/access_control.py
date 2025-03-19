"""
Access control middleware for the KPI system.
Provides decorators for role-based access control.
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """
    Decorator for routes that require admin privileges.
    Redirects to login or shows access denied message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """
    Decorator for routes that require manager privileges.
    Managers and admins can access these routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not (current_user.is_admin() or current_user.is_manager()):
            flash('Access denied. Manager privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def employee_owner_required(f):
    """
    Decorator for routes that require the user to be the owner of the employee resource.
    Admins and managers can access all employee resources.
    Regular users can only access resources for their linked employee.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Admins and managers can access all resources
        if current_user.is_admin() or current_user.is_manager():
            return f(*args, **kwargs)
        
        # Get employee_id from route parameters
        employee_id = kwargs.get('employee_id')
        
        # If no employee_id in parameters, or user is not linked to this employee
        if not employee_id or not current_user.employee_id or current_user.employee_id != employee_id:
            flash('Access denied. You can only access your own information.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function
