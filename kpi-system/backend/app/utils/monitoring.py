"""
System Health Monitoring Module for KPI System

This module provides tools for monitoring the health and performance of the KPI System.
It includes functions for checking database health, disk usage, and system statistics.
"""

import os
import time
import sqlite3
import psutil
import datetime
import logging
from functools import wraps
from flask import current_app, g, request

# Get module-specific logger
logger = logging.getLogger(__name__)

class PerformanceMetrics:
    """Class for tracking and recording performance metrics."""
    
    def __init__(self):
        """Initialize the performance metrics container."""
        self.reset()
    
    def reset(self):
        """Reset all metrics to default values."""
        self.request_count = 0
        self.response_times = []
        self.error_count = 0
        self.route_stats = {}
        self.slow_queries = []
        self.start_time = datetime.datetime.now()
    
    def record_request_time(self, route, response_time):
        """
        Record the response time for a request.
        
        Args:
            route (str): The route that was requested
            response_time (float): Response time in seconds
        """
        self.request_count += 1
        self.response_times.append(response_time)
        
        # Update route-specific stats
        if route not in self.route_stats:
            self.route_stats[route] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0
            }
            
        stats = self.route_stats[route]
        stats['count'] += 1
        stats['total_time'] += response_time
        stats['min_time'] = min(stats['min_time'], response_time)
        stats['max_time'] = max(stats['max_time'], response_time)
        
        # Record slow queries (more than 1 second)
        if response_time > 1.0:
            self.slow_queries.append({
                'route': route,
                'time': response_time,
                'timestamp': datetime.datetime.now()
            })
    
    def record_error(self):
        """Record an error occurrence."""
        self.error_count += 1
    
    def get_average_response_time(self):
        """
        Calculate the average response time.
        
        Returns:
            float: Average response time in seconds, or 0 if no requests
        """
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)
    
    def get_route_stats(self):
        """
        Get statistics for each route.
        
        Returns:
            dict: Route statistics with calculated averages
        """
        result = {}
        for route, stats in self.route_stats.items():
            route_result = stats.copy()
            if stats['count'] > 0:
                route_result['avg_time'] = stats['total_time'] / stats['count']
            else:
                route_result['avg_time'] = 0
            result[route] = route_result
        return result
    
    def get_summary(self):
        """
        Get a summary of all metrics.
        
        Returns:
            dict: Summary of all performance metrics
        """
        uptime = datetime.datetime.now() - self.start_time
        uptime_seconds = uptime.total_seconds()
        
        return {
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': uptime_seconds,
            'uptime': str(uptime),
            'request_count': self.request_count,
            'error_count': self.error_count,
            'error_rate': (self.error_count / self.request_count) if self.request_count > 0 else 0,
            'avg_response_time': self.get_average_response_time(),
            'requests_per_second': self.request_count / uptime_seconds if uptime_seconds > 0 else 0,
            'route_stats': self.get_route_stats(),
            'slow_queries': self.slow_queries[:10]  # Show only the last 10
        }

# Global metrics instance
metrics = PerformanceMetrics()

def get_system_health():
    """
    Get overall system health metrics.
    
    Returns:
        dict: System health metrics including CPU, memory, and disk usage
    """
    try:
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }
        
        # Get disk usage for the application directory
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        disk = psutil.disk_usage(app_dir)
        disk_usage = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }
        
        # Check if any critical thresholds are exceeded
        warnings = []
        if cpu_usage > 80:
            warnings.append(f"High CPU usage: {cpu_usage}%")
        if memory_usage['percent'] > 80:
            warnings.append(f"High memory usage: {memory_usage['percent']}%")
        if disk_usage['percent'] > 80:
            warnings.append(f"High disk usage: {disk_usage['percent']}%")
        
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage,
            'warnings': warnings,
            'status': 'warning' if warnings else 'healthy'
        }
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'status': 'error',
            'error': str(e)
        }

def check_database_health(db_path=None):
    """
    Check the health of the SQLite database.
    
    Args:
        db_path (str, optional): Path to the database file. If None, use
            the application's configured database path.
            
    Returns:
        dict: Database health metrics
    """
    try:
        # Get database path from app config if not provided
        if db_path is None:
            db_path = current_app.config['DATABASE_PATH']
        
        # Check if database file exists
        if not os.path.exists(db_path):
            return {
                'status': 'error',
                'message': f"Database file not found: {db_path}"
            }
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get database size
        db_size = os.path.getsize(db_path)
        
        # Run integrity check
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        # Get table statistics
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        table_stats = {}
        for table in tables:
            table_name = table[0]
            if table_name.startswith('sqlite_'):
                continue
                
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            table_stats[table_name] = {
                'row_count': row_count
            }
        
        # Check for fragmentation
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA freelist_count")
        freelist_count = cursor.fetchone()[0]
        
        fragmentation = 0
        if page_count > 0:
            fragmentation = (freelist_count / page_count) * 100
        
        conn.close()
        
        # Determine database status
        status = 'healthy'
        message = 'Database is healthy'
        warnings = []
        
        if integrity_result != 'ok':
            status = 'error'
            message = 'Database integrity check failed'
            warnings.append(f"Integrity check result: {integrity_result}")
        
        if fragmentation > 20:
            if status == 'healthy':
                status = 'warning'
                message = 'Database has high fragmentation'
            warnings.append(f"High fragmentation: {fragmentation:.2f}%")
        
        if db_size > 100 * 1024 * 1024:  # 100 MB
            if status == 'healthy':
                status = 'warning'
                message = 'Database file is large'
            warnings.append(f"Large database size: {format_bytes(db_size)}")
        
        return {
            'status': status,
            'message': message,
            'warnings': warnings,
            'size_bytes': db_size,
            'size_formatted': format_bytes(db_size),
            'integrity': integrity_result,
            'tables': table_stats,
            'page_count': page_count,
            'page_size': page_size,
            'fragmentation_percent': fragmentation
        }
    except Exception as e:
        logger.error(f"Error checking database health: {e}")
        return {
            'status': 'error',
            'message': f"Error checking database health: {str(e)}"
        }

def format_bytes(bytes_value):
    """
    Format bytes into a human-readable string.
    
    Args:
        bytes_value (int): Bytes value to format
        
    Returns:
        str: Formatted string (e.g., "1.23 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024 or unit == 'TB':
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024

def request_timer(f):
    """
    Decorator to time request processing.
    
    Args:
        f: The view function to wrap
        
    Returns:
        function: Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Record start time
        start_time = time.time()
        
        # Execute the view function
        try:
            response = f(*args, **kwargs)
            
            # Record end time and calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            route = request.endpoint
            metrics.record_request_time(route, duration)
            
            # Add timing header to response
            response.headers['X-Response-Time'] = f"{duration:.6f}s"
            
            return response
        except Exception as e:
            # Record error and re-raise
            metrics.record_error()
            raise
    
    return decorated_function

def setup_monitoring(app):
    """
    Set up monitoring for the Flask application.
    
    Args:
        app: Flask application instance
        
    Returns:
        Flask application instance with monitoring configured
    """
    # Reset metrics on application startup
    metrics.reset()
    
    # Set up request timing
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            route = request.endpoint or 'unknown'
            metrics.record_request_time(route, duration)
            response.headers['X-Response-Time'] = f"{duration:.6f}s"
        return response
    
    # Register error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        metrics.record_error()
        # Let the default error handlers deal with the exception
        raise e
    
    # Add monitoring route
    @app.route('/admin/health')
    def health_check():
        from flask import jsonify
        
        # Check if the request has a secret key for security
        expected_key = app.config.get('HEALTH_CHECK_KEY', 'healthcheck')
        provided_key = request.args.get('key')
        
        if provided_key != expected_key:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized health check request'
            }), 403
        
        # Perform health checks
        health_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'application': {
                'status': 'running',
                'uptime': str(datetime.datetime.now() - metrics.start_time),
                'version': app.config.get('VERSION', 'unknown')
            },
            'system': get_system_health(),
            'database': check_database_health(),
            'performance': {
                'request_count': metrics.request_count,
                'error_count': metrics.error_count,
                'avg_response_time': metrics.get_average_response_time()
            }
        }
        
        # Determine overall status
        if (health_data['system'].get('status') == 'error' or 
            health_data['database'].get('status') == 'error'):
            health_data['status'] = 'critical'
        elif (health_data['system'].get('status') == 'warning' or 
              health_data['database'].get('status') == 'warning'):
            health_data['status'] = 'warning'
        else:
            health_data['status'] = 'healthy'
        
        return jsonify(health_data)
    
    return app
