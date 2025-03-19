from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
import os
import json
import datetime
import sqlite3
import shutil
import re
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

from app.models.user import User
from app.middleware.access_control import admin_required
from app.utils.db_maintenance import optimize_database, get_database_stats

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Register template context processor for admin blueprint
@admin.app_context_processor
def inject_admin_utilities():
    """Inject utility functions into template context"""
    return {
        'parse_log_line': parse_log_line
    }

# Admin Dashboard
@admin.route('/')
@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    # Get system health data
    health_data = get_system_health()
    
    # Get database stats
    stats = get_database_stats()
    
    # Get performance metrics (placeholder data for now)
    performance_metrics = {
        'avg_response_time': 145,
        'requests_last_hour': 278,
        'errors_last_day': 12,
        'peak_load_time': '14:30',
        'memory_usage': 45
    }
    
    # Get recent evaluations
    # In a real implementation, this would query the database
    recent_evaluations = [
        {
            'employee_name': 'John Doe',
            'date': '2025-03-18',
            'score': 4.2,
            'score_percent': 84,
            'score_class': 'success'
        },
        {
            'employee_name': 'Jane Smith',
            'date': '2025-03-17',
            'score': 3.8,
            'score_percent': 76,
            'score_class': 'info'
        },
        {
            'employee_name': 'Bob Johnson',
            'date': '2025-03-16',
            'score': 2.9,
            'score_percent': 58,
            'score_class': 'warning'
        }
    ]
    
    # Get recent logs (placeholder data for now)
    recent_logs = [
        {
            'message': 'User admin logged in',
            'timestamp': '2025-03-19 09:45:12',
            'level': 'INFO',
            'level_class': 'info',
            'user': 'admin'
        },
        {
            'message': 'Database backup created',
            'timestamp': '2025-03-19 09:30:05',
            'level': 'INFO',
            'level_class': 'info',
            'user': 'admin'
        },
        {
            'message': 'Failed login attempt',
            'timestamp': '2025-03-19 08:15:23',
            'level': 'WARNING',
            'level_class': 'warning',
            'user': 'unknown'
        },
        {
            'message': 'System started',
            'timestamp': '2025-03-19 08:00:00',
            'level': 'INFO',
            'level_class': 'info',
            'user': 'system'
        }
    ]
    
    # Get current time for 'last updated' display
    now = datetime.datetime.now()
    
    return render_template('admin/dashboard.html', 
                           health_data=health_data, 
                           stats=stats,
                           performance_metrics=performance_metrics,
                           recent_evaluations=recent_evaluations,
                           recent_logs=recent_logs,
                           now=now)

# System Settings
@admin.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """System settings management page"""
    settings = get_system_settings()
    
    if request.method == 'POST':
        # Update settings
        updated_settings = {
            'company_name': request.form.get('company_name', ''),
            'email_notifications': request.form.get('email_notifications') == 'on',
            'session_timeout': int(request.form.get('session_timeout', 30)),
            'password_policy': {
                'min_length': int(request.form.get('min_length', 8)),
                'require_uppercase': request.form.get('require_uppercase') == 'on',
                'require_lowercase': request.form.get('require_lowercase') == 'on',
                'require_numbers': request.form.get('require_numbers') == 'on',
                'require_special': request.form.get('require_special') == 'on'
            },
            'ui_theme': request.form.get('ui_theme', 'light')
        }
        
        # Save updated settings
        save_system_settings(updated_settings)
        flash('System settings updated successfully', 'success')
        return redirect(url_for('admin.settings'))
        
    return render_template('admin/settings.html', settings=settings)

# Backup & Restore
@admin.route('/backups', methods=['GET'])
@login_required
@admin_required
def backups():
    """Backup management page"""
    backup_list = get_backups()
    return render_template('admin/backups.html', backups=backup_list)

@admin.route('/backups/create', methods=['POST'])
@login_required
@admin_required
def create_backup():
    """Create a new database backup"""
    backup_name = request.form.get('backup_name', '')
    description = request.form.get('description', '')
    
    if not backup_name:
        backup_name = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    success, message = create_database_backup(backup_name, description)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
        
    return redirect(url_for('admin.backups'))

@admin.route('/backups/restore/<backup_id>', methods=['POST'])
@login_required
@admin_required
def restore_backup(backup_id):
    """Restore database from backup"""
    success, message = restore_database_backup(backup_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
        
    return redirect(url_for('admin.backups'))

@admin.route('/backups/delete/<backup_id>', methods=['POST'])
@login_required
@admin_required
def delete_backup(backup_id):
    """Delete a backup file"""
    success, message = delete_database_backup(backup_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
        
    return redirect(url_for('admin.backups'))

@admin.route('/backups/download/<backup_id>', methods=['GET'])
@login_required
@admin_required
def download_backup(backup_id):
    """Download a backup file"""
    from flask import send_file
    
    backup_dir = os.path.join(current_app.instance_path, 'backups')
    backup_file = os.path.join(backup_dir, f"{backup_id}.sqlite")
    
    if not os.path.exists(backup_file):
        flash('Backup file not found', 'danger')
        return redirect(url_for('admin.backups'))
    
    return send_file(
        backup_file,
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=f"kpi_system_backup_{backup_id}.sqlite"
    )

# Helper function imports from part 3 - added here to make the file work independently
from app.utils.admin_helpers import (
    get_system_settings, save_system_settings, get_backups,
    create_database_backup, restore_database_backup, delete_database_backup,
    cleanup_old_data, get_system_health, get_system_logs, format_size, parse_log_line
)