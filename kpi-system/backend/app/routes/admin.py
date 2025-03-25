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

# Database Maintenance
@admin.route('/maintenance', methods=['GET'])
@login_required
@admin_required
def maintenance():
    """Database maintenance page"""
    stats = get_database_stats()
    
    # Check if integrity check results should be displayed
    integrity_check = None
    if 'integrity_results' in request.args:
        integrity_check = request.args.get('integrity_results')
        try:
            integrity_check = json.loads(integrity_check)
        except:
            integrity_check = None
    
    return render_template('admin/maintenance.html', stats=stats, integrity_check=integrity_check)

@admin.route('/maintenance/optimize', methods=['POST'])
@login_required
@admin_required
def optimize():
    """Optimize database"""
    result = optimize_database()
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
        
    return redirect(url_for('admin.maintenance'))

@admin.route('/maintenance/cleanup', methods=['POST'])
@login_required
@admin_required
def cleanup():
    """Clean up old data"""
    days = int(request.form.get('days', 365))
    result = cleanup_old_data(days)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
        
    return redirect(url_for('admin.maintenance'))

@admin.route('/maintenance/integrity-check', methods=['POST'])
@login_required
@admin_required
def integrity_check():
    """Check database integrity"""
    from app.utils.db_maintenance import check_database_integrity
    
    result = check_database_integrity()
    
    # Add result to URL parameters to show in modal
    return redirect(url_for('admin.maintenance', integrity_results=json.dumps(result)))

@admin.route('/maintenance/integrity-check-ajax', methods=['POST'])
@login_required
@admin_required
def integrity_check_ajax():
    """AJAX endpoint for checking database integrity"""
    from app.utils.db_maintenance import check_database_integrity
    
    result = check_database_integrity()
    return jsonify(result)

@admin.route('/maintenance/export', methods=['POST'])
@login_required
@admin_required
def export():
    """Export database"""
    from app.utils.db_maintenance import export_database
    from flask import send_file
    
    format = request.form.get('format', 'sql')
    result = export_database(format)
    
    if result['success']:
        flash(result['message'], 'success')
        
        # Send the file to the user
        return send_file(
            result['path'],
            as_attachment=True,
            download_name=os.path.basename(result['path'])
        )
    else:
        flash(result['message'], 'danger')
        return redirect(url_for('admin.maintenance'))

@admin.route('/maintenance/import', methods=['POST'])
@login_required
@admin_required
def import_data():
    """Import data from CSV file"""
    from app.utils.db_maintenance import import_csv_data
    
    if 'csv_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('admin.maintenance'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('admin.maintenance'))
    
    if not file.filename.endswith('.csv'):
        flash('Only CSV files are supported', 'danger')
        return redirect(url_for('admin.maintenance'))
    
    table_name = request.form.get('table_name', '')
    if not table_name:
        flash('Please select a target table', 'danger')
        return redirect(url_for('admin.maintenance'))
    
    truncate = request.form.get('truncate') == 'on'
    
    # Save the file temporarily
    filename = secure_filename(file.filename)
    temp_path = os.path.join(current_app.instance_path, 'temp', filename)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    file.save(temp_path)
    
    # Import the data
    result = import_csv_data(table_name, temp_path, truncate)
    
    # Remove the temporary file
    os.remove(temp_path)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    
    return redirect(url_for('admin.maintenance'))

# System Health
@admin.route('/health', methods=['GET'])
@login_required
@admin_required
def health():
    """System health monitoring page"""
    health_data = get_system_health()
    
    # Mock data for performance metrics (in a real app, this would come from monitoring)
    performance_metrics = {
        'avg_response_time': 145, # milliseconds
        'requests_last_hour': 278,
        'errors_last_day': 12,
        'peak_load_time': '14:30',
        'memory_usage': 45 # percent
    }
    
    # Current timestamp for 'last updated'
    now = datetime.datetime.now()
    
    return render_template('admin/health.html', 
                           health_data=health_data, 
                           performance_metrics=performance_metrics,
                           now=now)

@admin.route('/logs', methods=['GET'])
@login_required
@admin_required
def logs():
    """System logs viewer"""
    log_type = request.args.get('type', 'application')
    page = int(request.args.get('page', 1))
    
    logs_data = get_system_logs(log_type, page)
    return render_template('admin/logs.html', logs=logs_data, log_type=log_type, page=page)

@admin.route('/logs/clear', methods=['POST'])
@login_required
@admin_required
def clear_logs():
    """Clear log files"""
    log_type = request.form.get('log_type', 'application')
    
    try:
        log_dir = os.path.join(current_app.instance_path, 'logs')
        
        # Determine log file path based on type
        if log_type == 'application':
            log_file = os.path.join(log_dir, 'app.log')
        elif log_type == 'access':
            log_file = os.path.join(log_dir, 'access.log')
        elif log_type == 'error':
            log_file = os.path.join(log_dir, 'error.log')
        else:
            log_file = os.path.join(log_dir, 'app.log')
        
        # Check if log file exists
        if os.path.exists(log_file):
            # Clear the file (open in write mode and close immediately)
            with open(log_file, 'w') as f:
                pass
            
            flash(f"{log_type.capitalize()} logs cleared successfully", 'success')
        else:
            flash(f"No {log_type} log file found", 'warning')
    except Exception as e:
        flash(f"Error clearing logs: {str(e)}", 'danger')
        
    return redirect(url_for('admin.logs', type=log_type))

@admin.route('/logs/download', methods=['GET'])
@login_required
@admin_required
def download_logs():
    """Download log file"""
    from flask import send_file
    
    log_type = request.args.get('type', 'application')
    
    log_dir = os.path.join(current_app.instance_path, 'logs')
    
    # Determine log file path based on type
    if log_type == 'application':
        log_file = os.path.join(log_dir, 'app.log')
        filename = 'application_log.txt'
    elif log_type == 'access':
        log_file = os.path.join(log_dir, 'access.log')
        filename = 'access_log.txt'
    elif log_type == 'error':
        log_file = os.path.join(log_dir, 'error.log')
        filename = 'error_log.txt'
    else:
        log_file = os.path.join(log_dir, 'app.log')
        filename = 'application_log.txt'
    
    # Check if log file exists
    if not os.path.exists(log_file):
        flash(f"No {log_type} log file found", 'warning')
        return redirect(url_for('admin.logs', type=log_type))
    
    return send_file(
        log_file,
        mimetype='text/plain',
        as_attachment=True,
        download_name=filename
    )

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

# Helper functions
def get_system_settings():
    """Get current system settings"""
    settings_file = os.path.join(current_app.instance_path, 'settings.json')
    
    # Default settings
    default_settings = {
        'company_name': 'Handyman KPI System',
        'email_notifications': False,
        'session_timeout': 30,
        'password_policy': {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special': False
        },
        'ui_theme': 'light'
    }
    
    # If settings file doesn't exist, create it with defaults
    if not os.path.exists(settings_file):
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, 'w') as f:
            json.dump(default_settings, f, indent=4)
        return default_settings
    
    # Read settings from file
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        current_app.logger.error(f"Error reading settings file: {str(e)}")
        return default_settings

def save_system_settings(settings):
    """Save system settings to file"""
    settings_file = os.path.join(current_app.instance_path, 'settings.json')
    
    try:
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        current_app.logger.error(f"Error saving settings file: {str(e)}")
        return False

def get_backups():
    """Get list of available backups"""
    backup_dir = os.path.join(current_app.instance_path, 'backups')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)
        return []
    
    backups = []
    
    # Get .sqlite files in the backup directory
    for filename in os.listdir(backup_dir):
        if filename.endswith('.sqlite'):
            backup_id = filename.split('.')[0]
            
            # Get backup metadata if available
            metadata_file = os.path.join(backup_dir, f"{backup_id}.json")
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except:
                    metadata = {}
            else:
                metadata = {}
            
            # Get file info
            backup_path = os.path.join(backup_dir, filename)
            file_stats = os.stat(backup_path)
            
            backups.append({
                'id': backup_id,
                'name': metadata.get('name', backup_id),
                'description': metadata.get('description', ''),
                'created_at': metadata.get('created_at', datetime.datetime.fromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')),
                'size': file_stats.st_size,
                'size_formatted': format_size(file_stats.st_size)
            })
    
    # Sort backups by creation date (newest first)
    return sorted(backups, key=lambda x: x['created_at'], reverse=True)

def create_database_backup(name, description=''):
    """Create a database backup"""
    try:
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(current_app.instance_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup ID
        backup_id = f"{name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Database path
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Backup path
        backup_path = os.path.join(backup_dir, f"{backup_id}.sqlite")
        
        # Copy database file
        shutil.copy2(db_path, backup_path)
        
        # Create metadata file
        metadata = {
            'name': name,
            'description': description,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': current_user.username
        }
        
        with open(os.path.join(backup_dir, f"{backup_id}.json"), 'w') as f:
            json.dump(metadata, f, indent=4)
        
        return True, f"Backup '{name}' created successfully"
    except Exception as e:
        current_app.logger.error(f"Error creating backup: {str(e)}")
        return False, f"Error creating backup: {str(e)}"

def restore_database_backup(backup_id):
    """Restore database from backup"""
    try:
        # Backup directory
        backup_dir = os.path.join(current_app.instance_path, 'backups')
        
        # Backup path
        backup_path = os.path.join(backup_dir, f"{backup_id}.sqlite")
        
        if not os.path.exists(backup_path):
            return False, "Backup file not found"
        
        # Database path
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Create a backup of the current database before restoring
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        pre_restore_backup = os.path.join(backup_dir, f"pre_restore_{timestamp}.sqlite")
        shutil.copy2(db_path, pre_restore_backup)
        
        # Create metadata for pre-restore backup
        metadata = {
            'name': 'Pre-restore Backup',
            'description': f"Automatic backup created before restoring {backup_id}",
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': current_user.username
        }
        
        with open(os.path.join(backup_dir, f"pre_restore_{timestamp}.json"), 'w') as f:
            json.dump(metadata, f, indent=4)
        
        # Restore the backup
        shutil.copy2(backup_path, db_path)
        
        return True, "Database restored successfully"
    except Exception as e:
        current_app.logger.error(f"Error restoring backup: {str(e)}")
        return False, f"Error restoring backup: {str(e)}"

def delete_database_backup(backup_id):
    """Delete a database backup"""
    try:
        # Backup directory
        backup_dir = os.path.join(current_app.instance_path, 'backups')
        
        # Backup paths
        backup_path = os.path.join(backup_dir, f"{backup_id}.sqlite")
        metadata_path = os.path.join(backup_dir, f"{backup_id}.json")
        
        # Check if backup exists
        if not os.path.exists(backup_path):
            return False, "Backup file not found"
        
        # Delete backup file
        os.remove(backup_path)
        
        # Delete metadata file if it exists
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        return True, "Backup deleted successfully"
    except Exception as e:
        current_app.logger.error(f"Error deleting backup: {str(e)}")
        return False, f"Error deleting backup: {str(e)}"

def cleanup_old_data(days=365):
    """Clean up old data from the database"""
    try:
        # Get database connection
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Calculate cutoff date
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Delete old evaluations
        cursor.execute("DELETE FROM evaluations WHERE date < ?", (cutoff_date,))
        evaluations_deleted = cursor.rowcount
        
        # Delete orphaned evaluation skills
        cursor.execute("""
            DELETE FROM eval_skills 
            WHERE evaluation_id NOT IN (SELECT id FROM evaluations)
        """)
        eval_skills_deleted = cursor.rowcount
        
        # Delete orphaned evaluation tools
        cursor.execute("""
            DELETE FROM eval_tools 
            WHERE evaluation_id NOT IN (SELECT id FROM evaluations)
        """)
        eval_tools_deleted = cursor.rowcount
        
        # Commit changes
        conn.commit()
        
        # Close connection
        conn.close()
        
        return {
            'success': True,
            'message': f"Cleanup successful: Deleted {evaluations_deleted} evaluations, {eval_skills_deleted} skill ratings, and {eval_tools_deleted} tool ratings older than {days} days"
        }
    except Exception as e:
        current_app.logger.error(f"Error cleaning up old data: {str(e)}")
        return {
            'success': False,
            'message': f"Error cleaning up old data: {str(e)}"
        }

def get_system_health():
    """Get system health data"""
    health_data = {
        'status': 'healthy',
        'database': {
            'size': 0,
            'size_formatted': '0 B',
            'last_backup': None,
            'tables': {}
        },
        'users': {
            'total': 0,
            'active': 0,
            'inactive': 0,
            'admins': 0,
            'managers': 0,
            'employees': 0
        },
        'evaluations': {
            'total': 0,
            'last_30_days': 0
        },
        'employees': {
            'total': 0,
            'by_tier': {}
        },
        'system': {
            'uptime': '0d 0h 0m',
            'storage': {
                'total': 0,
                'used': 0,
                'free': 0,
                'percent_used': 0
            }
        }
    }
    
    try:
        # Get database stats
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if os.path.exists(db_path):
            # Get database size
            db_size = os.path.getsize(db_path)
            health_data['database']['size'] = db_size
            health_data['database']['size_formatted'] = format_size(db_size)
            
            # Get table stats
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                # Skip sqlite_ tables
                if table_name.startswith('sqlite_'):
                    continue
                    
                # Count rows in table
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = cursor.fetchone()[0]
                
                health_data['database']['tables'][table_name] = row_count
            
            # Get user stats
            cursor.execute("SELECT COUNT(*) FROM users;")
            health_data['users']['total'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE active = 1;")
            health_data['users']['active'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE active = 0;")
            health_data['users']['inactive'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin';")
            health_data['users']['admins'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'manager';")
            health_data['users']['managers'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employee';")
            health_data['users']['employees'] = cursor.fetchone()[0]
            
            # Get evaluation stats
            cursor.execute("SELECT COUNT(*) FROM evaluations;")
            health_data['evaluations']['total'] = cursor.fetchone()[0]
            
            thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM evaluations WHERE date >= ?;", (thirty_days_ago,))
            health_data['evaluations']['last_30_days'] = cursor.fetchone()[0]
            
            # Get employee stats
            cursor.execute("SELECT COUNT(*) FROM employees;")
            health_data['employees']['total'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT tier, COUNT(*) FROM employees GROUP BY tier;")
            tiers = cursor.fetchall()
            
            for tier in tiers:
                health_data['employees']['by_tier'][tier[0]] = tier[1]
            
            # Get last backup date
            backup_dir = os.path.join(current_app.instance_path, 'backups')
            if os.path.exists(backup_dir):
                backups = get_backups()
                if backups:
                    health_data['database']['last_backup'] = backups[0]['created_at']
            
            # Close connection
            conn.close()
        
        # Get system stats
        import psutil
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        health_data['system']['storage']['total'] = disk.total
        health_data['system']['storage']['used'] = disk.used
        health_data['system']['storage']['free'] = disk.free
        health_data['system']['storage']['percent_used'] = disk.percent
        
        # Format storage values
        health_data['system']['storage']['total_formatted'] = format_size(disk.total)
        health_data['system']['storage']['used_formatted'] = format_size(disk.used)
        health_data['system']['storage']['free_formatted'] = format_size(disk.free)
        
        # Get uptime
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        health_data['system']['uptime'] = f"{days}d {hours}h {minutes}m"
        
        return health_data
    except Exception as e:
        current_app.logger.error(f"Error getting system health data: {str(e)}")
        health_data['status'] = 'error'
        return health_data

def get_system_logs(log_type='application', page=1, per_page=100):
    """Get system logs"""
    logs = []
    
    try:
        log_dir = os.path.join(current_app.instance_path, 'logs')
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            return {
                'logs': [],
                'total': 0,
                'pages': 0,
                'current_page': page
            }
        
        # Determine log file path based on type
        if log_type == 'application':
            log_file = os.path.join(log_dir, 'app.log')
        elif log_type == 'access':
            log_file = os.path.join(log_dir, 'access.log')
        elif log_type == 'error':
            log_file = os.path.join(log_dir, 'error.log')
        else:
            log_file = os.path.join(log_dir, 'app.log')
        
        # Check if log file exists
        if not os.path.exists(log_file):
            return {
                'logs': [],
                'total': 0,
                'pages': 0,
                'current_page': page
            }
        
        # Read log file
        with open(log_file, 'r') as f:
            all_logs = f.readlines()
        
        # Total logs
        total_logs = len(all_logs)
        
        # Calculate pagination
        total_pages = (total_logs + per_page - 1) // per_page
        
        # Get logs for current page
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        page_logs = all_logs[start_index:end_index]
        
        # Process logs
        for log_line in page_logs:
            log_line = log_line.strip()
            if log_line:
                logs.append(log_line)
        
        return {
            'logs': logs,
            'total': total_logs,
            'pages': total_pages,
            'current_page': page
        }
    except Exception as e:
        current_app.logger.error(f"Error getting system logs: {str(e)}")
        return {
            'logs': [],
            'total': 0,
            'pages': 0,
            'current_page': page
        }

def format_size(size_bytes):
    """Format file size from bytes to human-readable format"""
    if size_bytes == 0:
        return "0 B"
        
    size_names = ('B', 'KB', 'MB', 'GB', 'TB')
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
        
    return f"{size_bytes:.2f} {size_names[i]}"


def parse_log_line(log_line):
    """Parse a log line into its components
    
    Expected log format: [TIMESTAMP] [LEVEL] [SOURCE] Message
    """
    # Default values
    result = {
        'timestamp': '',
        'level': 'INFO',
        'level_class': 'info',
        'source': 'system',
        'message': log_line
    }
    
    # Try to parse with regex
    timestamp_pattern = r'\[(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)\]'
    level_pattern = r'\[(INFO|DEBUG|WARNING|ERROR|CRITICAL)\]'
    source_pattern = r'\[([^\]]+)\]'
    
    # Extract timestamp
    timestamp_match = re.search(timestamp_pattern, log_line)
    if timestamp_match:
        result['timestamp'] = timestamp_match.group(1).strip()
        log_line = log_line[timestamp_match.end():].strip()
    
    # Extract level
    level_match = re.search(level_pattern, log_line)
    if level_match:
        level = level_match.group(1).strip()
        result['level'] = level
        
        # Set level class for Bootstrap styling
        if level == 'INFO':
            result['level_class'] = 'info'
        elif level == 'DEBUG':
            result['level_class'] = 'secondary'
        elif level == 'WARNING':
            result['level_class'] = 'warning'
        elif level == 'ERROR':
            result['level_class'] = 'danger'
        elif level == 'CRITICAL':
            result['level_class'] = 'danger'
        
        log_line = log_line[level_match.end():].strip()
    
    # Extract source
    source_match = re.search(source_pattern, log_line)
    if source_match:
        result['source'] = source_match.group(1).strip()
        log_line = log_line[source_match.end():].strip()
    
    # Remaining text is the message
    if log_line:
        result['message'] = log_line
    
    return result
