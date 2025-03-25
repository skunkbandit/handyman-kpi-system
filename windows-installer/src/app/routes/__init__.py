"""
Route blueprints for the KPI system.
Each blueprint is registered with the Flask application at startup.
"""
from flask import Blueprint

# Import all route blueprints
from .main import bp as main_bp
from .auth import bp as auth_bp
from .dashboard import bp as dashboard_bp
from .employees import bp as employees_bp
from .evaluations import bp as evaluations_bp
from .reports import bp as reports_bp
from .admin import admin as admin_bp

# Function to register all blueprints with the application
def register_blueprints(app):
    """Register all application blueprints"""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(evaluations_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
