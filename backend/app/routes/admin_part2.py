"""
Admin routes for the KPI system - Part 2: Database maintenance, system health, logs
This file contains additional routes to be merged into admin.py
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app, send_file
import os
import json
import datetime
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

from app.middleware.access_control import admin_required
from app.utils.db_maintenance import optimize_database, get_database_stats, check_database_integrity, export_database, import_csv_data
from app.utils.admin_helpers import get_system_health, get_system_logs, cleanup_old_data

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
    result = check_database_integrity()
    
    # Add result to URL parameters to show in modal
    return redirect(url_for('admin.maintenance', integrity_results=json.dumps(result)))

@admin.route('/maintenance/integrity-check-ajax', methods=['POST'])
@login_required
@admin_required
def integrity_check_ajax():
    """AJAX endpoint for checking database integrity"""
    result = check_database_integrity()
    return jsonify(result)

@admin.route('/maintenance/export', methods=['POST'])
@login_required
@admin_required
def export():
    """Export database"""
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

# System Logs
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