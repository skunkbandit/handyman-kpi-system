"""
Flask application factory for the KPI system
"""
import os
from flask import Flask, redirect, url_for, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Create extension instances
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(test_config=None):
    """
    Create and configure the Flask application
    """
    # Create app instance
    app = Flask(__name__, instance_relative_config=True)
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_not_for_production'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'database', 'kpi_system.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        APP_NAME='Handyman KPI System',
        APP_VERSION='1.0.0',
        WTF_CSRF_ENABLED=True,
        REMEMBER_COOKIE_DURATION=86400,  # 1 day in seconds
        REMEMBER_COOKIE_SECURE=False,    # Set to True in production with HTTPS
        REMEMBER_COOKIE_HTTPONLY=True
    )
    
    # Load test config if passed in
    if test_config is not None:
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    
    # Configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints - comment out for now to avoid import errors
    # from app.routes import dashboard, employees, evaluations, reports, main, auth
    # 
    # app.register_blueprint(main.bp)
    # app.register_blueprint(dashboard.bp)
    # app.register_blueprint(employees.bp)
    # app.register_blueprint(evaluations.bp)
    # app.register_blueprint(reports.bp)
    # app.register_blueprint(auth.auth_bp)
    
    # Simplified route for testing
    @app.route('/')
    def index():
        return 'Handyman KPI System is running!'
    
    # Add favicon route to prevent 404 errors
    @app.route('/favicon.ico')
    def favicon():
        return '', 204  # Return empty response with No Content status
    
    # Make url_for('index') work for the main index page
    app.add_url_rule('/', endpoint='index')
    
    # Setup context processors
    @app.context_processor
    def inject_app_info():
        return dict(
            app_name=app.config['APP_NAME'],
            app_version=app.config['APP_VERSION']
        )

    # Simplified error handlers that don't use templates
    @app.errorhandler(404)
    def page_not_found(e):
        return "404 Not Found - The requested page does not exist", 404

    @app.errorhandler(403)
    def forbidden(e):
        return "403 Forbidden - You don't have permission to access this resource", 403

    @app.errorhandler(500)
    def server_error(e):
        return "500 Server Error - An internal server error occurred", 500
    
    return app

# Create the Flask app instance for direct import
app = create_app()