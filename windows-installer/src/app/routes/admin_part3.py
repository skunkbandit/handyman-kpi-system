"""
Admin routes for the KPI system - Part 3: User management
This file contains additional routes to be merged into admin.py
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
import datetime
from flask_login import login_required, current_user

from app.models.user import User
from app.middleware.access_control import admin_required

# User Management
@admin.route('/users', methods=['GET'])
@login_required
@admin_required
def users():
    """User management page"""
    users_list = User.query.all()
    
    # Count users by role
    admin_count = sum(1 for user in users_list if user.role == 'admin')
    manager_count = sum(1 for user in users_list if user.role == 'manager')
    employee_count = sum(1 for user in users_list if user.role == 'employee')
    
    # Count active users
    active_count = sum(1 for user in users_list if user.active)
    
    # Count users by login time
    today = datetime.datetime.now().date()
    week_ago = today - datetime.timedelta(days=7)
    month_ago = today - datetime.timedelta(days=30)
    
    today_login_count = sum(1 for user in users_list if user.last_login and user.last_login.date() == today)
    week_login_count = sum(1 for user in users_list if user.last_login and user.last_login.date() >= week_ago)
    month_login_count = sum(1 for user in users_list if user.last_login and user.last_login.date() >= month_ago)
    never_login_count = sum(1 for user in users_list if not user.last_login)
    
    return render_template('admin/users.html', 
                           users=users_list,
                           admin_count=admin_count,
                           manager_count=manager_count,
                           employee_count=employee_count,
                           active_count=active_count,
                           today_login_count=today_login_count,
                           week_login_count=week_login_count,
                           month_login_count=month_login_count,
                           never_login_count=never_login_count)

@admin.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create a new user"""
    from app import db
    from werkzeug.security import generate_password_hash
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        employee_id = request.form.get('employee_id') or None
        active = 'active' in request.form
        
        error = None
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not role:
            error = 'Role is required.'
        elif User.query.filter_by(username=username).first():
            error = f"Username '{username}' is already taken."
        elif User.query.filter_by(email=email).first():
            error = f"Email '{email}' is already registered."
        
        if error is None:
            # Create new user
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role=role,
                employee_id=employee_id,
                active=active,
                created_at=datetime.datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            
            flash(f"User '{username}' successfully created.", 'success')
            return redirect(url_for('admin.users'))
        
        flash(error, 'danger')
    
    # Get all employees for the dropdown
    from app.models.employee import Employee
    employees = Employee.query.filter_by(active=True).all()
    
    return render_template('admin/users_create.html', employees=employees)

@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit an existing user"""
    from app import db
    from werkzeug.security import generate_password_hash
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        employee_id = request.form.get('employee_id') or None
        active = 'active' in request.form
        
        error = None
        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not role:
            error = 'Role is required.'
        elif username != user.username and User.query.filter_by(username=username).first():
            error = f"Username '{username}' is already taken."
        elif email != user.email and User.query.filter_by(email=email).first():
            error = f"Email '{email}' is already registered."
        
        if error is None:
            # Update user
            user.username = username
            user.email = email
            user.role = role
            user.employee_id = employee_id
            user.active = active
            user.updated_at = datetime.datetime.now()
            
            # Update password if provided
            if password:
                user.password_hash = generate_password_hash(password)
            
            db.session.commit()
            
            flash(f"User '{username}' successfully updated.", 'success')
            return redirect(url_for('admin.users'))
        
        flash(error, 'danger')
    
    # Get all employees for the dropdown
    from app.models.employee import Employee
    employees = Employee.query.filter_by(active=True).all()
    
    return render_template('admin/users_edit.html', user=user, employees=employees)

@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    from app import db
    
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting your own account
    if user.user_id == current_user.user_id:
        flash("You cannot delete your own account.", 'danger')
        return redirect(url_for('admin.users'))
    
    # Don't delete the last admin
    if user.role == 'admin' and User.query.filter_by(role='admin').count() <= 1:
        flash("Cannot delete the last admin user.", 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{username}' successfully deleted.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", 'danger')
    
    return redirect(url_for('admin.users'))

@admin.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset a user's password"""
    from app import db
    from werkzeug.security import generate_password_hash
    import secrets
    import string
    
    user = User.query.get_or_404(user_id)
    
    # Generate a random password
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    # Update password
    user.password_hash = generate_password_hash(password)
    user.updated_at = datetime.datetime.now()
    db.session.commit()
    
    flash(f"Password for '{user.username}' has been reset to: {password}", 'success')
    return redirect(url_for('admin.users'))
