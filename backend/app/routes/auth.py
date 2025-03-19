"""
Authentication Routes
-------------------
Routes for user authentication and authorization with Flask-Login integration.
"""

from datetime import datetime
import uuid
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from app import db
from app.models.user import User
from app.models.employee import Employee
from app.utils.email import send_password_reset_email

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Create CSRF protection
csrf = CSRFProtect()

# Custom decorators for role-based access control
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied: Administrator privileges required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_manager():
            flash('Access denied: Manager privileges required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Rate limiting dictionary for login attempts
login_attempts = {}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with rate limiting and remember me functionality."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Check rate limiting
        ip = request.remote_addr
        current_time = datetime.utcnow()
        if ip in login_attempts:
            attempts, first_attempt_time = login_attempts[ip]
            # Reset counter after 30 minutes
            if (current_time - first_attempt_time).total_seconds() > 1800:  
                login_attempts[ip] = (1, current_time)
            elif attempts >= 5:
                flash('Too many login attempts. Please try again later.', 'danger')
                return render_template('auth/login.html')
            else:
                login_attempts[ip] = (attempts + 1, first_attempt_time)
        else:
            login_attempts[ip] = (1, current_time)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.verify_password(password):
            if not user.active:
                flash('This account has been deactivated. Please contact an administrator.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            user.update_last_login()
            
            # Clear login attempts on successful login
            if ip in login_attempts:
                del login_attempts[ip]
            
            # Check if user needs to change password
            if user.force_password_change:
                flash('You must change your password before continuing.', 'warning')
                return redirect(url_for('auth.change_password'))
            
            # Get next page or default to dashboard
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard.index')
                
            flash('Login successful!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Show user profile."""
    return render_template('auth/profile.html', current_user=current_user)

@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile."""
    username = request.form.get('username')
    
    if User.query.filter_by(username=username).first() and username != current_user.username:
        flash('Username already exists', 'danger')
        return redirect(url_for('auth.profile'))
    
    current_user.username = username
    
    # Only allow admins to change employee link
    if current_user.is_admin() and 'employee_id' in request.form:
        employee_id = request.form.get('employee_id')
        if employee_id:
            current_user.employee_id = int(employee_id)
        else:
            current_user.employee_id = None
    
    db.session.commit()
    flash('Profile updated successfully', 'success')
    return redirect(url_for('auth.profile'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Handle password change."""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.verify_password(current_password):
            flash('Current password is incorrect', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match', 'danger')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
        else:
            # Check password complexity
            has_upper = any(c.isupper() for c in new_password)
            has_lower = any(c.islower() for c in new_password)
            has_digit = any(c.isdigit() for c in new_password)
            
            if not (has_upper and has_lower and has_digit):
                flash('Password must contain at least one uppercase letter, one lowercase letter, and one number', 'danger')
                return render_template('auth/change_password.html')
            
            current_user.password = new_password
            current_user.force_password_change = False
            db.session.commit()
            flash('Password updated successfully', 'success')
            return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        
        if user:
            token = user.generate_reset_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            # In a real app, we would send an email with the reset link
            # For now, we'll just flash the link (for development only)
            try:
                send_password_reset_email(user, reset_url)
                flash('Password reset instructions have been sent to your email.', 'success')
            except Exception as e:
                current_app.logger.error(f"Email sending error: {str(e)}")
                # Development fallback - DO NOT use in production
                flash(f'For development - Reset URL: {reset_url}', 'info')
        else:
            # Don't reveal that the user doesn't exist
            flash('Password reset instructions have been sent if the username exists.', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset token', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
        else:
            # Check password complexity
            has_upper = any(c.isupper() for c in new_password)
            has_lower = any(c.islower() for c in new_password)
            has_digit = any(c.isdigit() for c in new_password)
            
            if not (has_upper and has_lower and has_digit):
                flash('Password must contain at least one uppercase letter, one lowercase letter, and one number', 'danger')
                return render_template('auth/reset_password.html', token=token)
            
            user.password = new_password
            user.force_password_change = False
            user.clear_reset_token()
            db.session.commit()
            flash('Your password has been reset. You can now login with your new password.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)

# User management routes (admin only)
@auth_bp.route('/users')
@login_required
@admin_required
def user_management():
    """List all users for management (admin only)."""
    users = User.query.all()
    return render_template('auth/user_management.html', users=users)

@auth_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create a new user (admin only)."""
    employees = Employee.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        employee_id = request.form.get('employee_id')
        
        # Check password complexity
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
            return render_template('auth/create_user.html', employees=employees)
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            flash('Password must contain at least one uppercase letter, one lowercase letter, and one number', 'danger')
            return render_template('auth/create_user.html', employees=employees)
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('auth/create_user.html', employees=employees)
        
        # Create new user
        user = User(
            username=username,
            password=password,
            role=role,
            employee_id=int(employee_id) if employee_id else None,
            active=True
        )
        
        db.session.add(user)
        db.session.commit()
        flash(f'User {username} created successfully', 'success')
        return redirect(url_for('auth.user_management'))
    
    return render_template('auth/create_user.html', employees=employees)

@auth_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """Edit a user (admin only)."""
    user = User.query.get_or_404(id)
    employees = Employee.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        employee_id = request.form.get('employee_id')
        active = request.form.get('active') == '1'
        
        # Check if username already exists and is not the current user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            flash('Username already exists', 'danger')
            return render_template('auth/edit_user.html', user=user, employees=employees)
        
        user.username = username
        user.role = role
        user.employee_id = int(employee_id) if employee_id else None
        user.active = active
        
        db.session.commit()
        flash(f'User {username} updated successfully', 'success')
        return redirect(url_for('auth.user_management'))
    
    return render_template('auth/edit_user.html', user=user, employees=employees)

@auth_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """Delete a user (admin only)."""
    user = User.query.get_or_404(id)
    
    # Prevent deleting your own account
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('auth.user_management'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User {username} deleted successfully', 'success')
    return redirect(url_for('auth.user_management'))

@auth_bp.route('/users/reset-password/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_user_password(id):
    """Reset a user's password (admin only)."""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        force_change = request.form.get('force_change') == '1'
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
        elif len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'danger')
        else:
            # Check password complexity
            has_upper = any(c.isupper() for c in new_password)
            has_lower = any(c.islower() for c in new_password)
            has_digit = any(c.isdigit() for c in new_password)
            
            if not (has_upper and has_lower and has_digit):
                flash('Password must contain at least one uppercase letter, one lowercase letter, and one number', 'danger')
                return render_template('auth/reset_user_password.html', user=user)
            
            user.password = new_password
            user.force_password_change = force_change
            db.session.commit()
            flash(f'Password for {user.username} has been reset', 'success')
            return redirect(url_for('auth.user_management'))
    
    return render_template('auth/reset_user_password.html', user=user)