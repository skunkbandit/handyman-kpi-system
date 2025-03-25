"""
Access Control Middleware
----------------------
Middleware for role-based access control.
"""

from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    
    Args:
        f: The function to be decorated
        
    Returns:
        The decorated function with admin access check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied: Administrator privileges required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """
    Decorator to restrict access to manager users or above.
    
    Args:
        f: The function to be decorated
        
    Returns:
        The decorated function with manager access check
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_manager():
            flash('Access denied: Manager privileges required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    """
    Decorator to restrict access to users with specific roles.
    
    Args:
        *roles: Roles that are allowed to access the decorated function
        
    Returns:
        The decorated function with role check
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('Access denied: Insufficient privileges', 'danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def employee_owner_or_manager_required(employee_id_param='id'):
    """
    Decorator to restrict access to the employee owner or managers.
    The employee_id_param is the name of the route parameter that contains the employee ID.
    
    Args:
        employee_id_param: The name of the route parameter that contains the employee ID
        
    Returns:
        The decorated function with ownership or manager check
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Access denied: Please login', 'danger')
                return redirect(url_for('auth.login'))
            
            # Check if the user is the owner or a manager
            employee_id = kwargs.get(employee_id_param)
            if employee_id:
                is_owner = current_user.employee_id == int(employee_id)
                if not (is_owner or current_user.is_manager()):
                    flash('Access denied: You can only view your own profile or you need manager privileges', 'danger')
                    return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def audit_log(action):
    """
    Decorator to log user actions.
    
    Args:
        action: Description of the action being performed
        
    Returns:
        The decorated function with audit logging
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # We'd implement actual audit logging here
            # For now, let's just print to console as an example
            if current_user.is_authenticated:
                print(f"AUDIT: User {current_user.username} performed action: {action}")
            result = f(*args, **kwargs)
            return result
        return decorated_function
    return decorator