@echo off
echo ================================================
echo Handyman KPI System - Complete Fix Script
echo ================================================
echo.

set INSTALLED_APP=C:\Users\dtest\AppData\Local\Programs\Handyman KPI System

REM Step 1: Stopping any running instances
echo Step 1: Stopping any running instances...
taskkill /F /IM python.exe 2>nul

REM Step 2: Install missing dependencies
echo.
echo Step 2: Installing missing dependencies...
cd /d "%INSTALLED_APP%\python"
.\python.exe -m pip install pandas

REM Step 3: Fix the auth blueprint in auth.py
echo.
echo Step 3: Fixing auth blueprint in auth.py...
set AUTH_FILE=%INSTALLED_APP%\app\routes\auth.py
echo Creating backup...
copy /Y "%AUTH_FILE%" "%AUTH_FILE%.bak"
echo Replacing auth_bp with bp...
powershell -Command "(Get-Content '%AUTH_FILE%') -replace 'auth_bp', 'bp' | Set-Content '%AUTH_FILE%'"

REM Step 4: Update the main.py routes file
echo.
echo Step 4: Updating main routes...
set MAIN_FILE=%INSTALLED_APP%\app\routes\main.py
echo Creating backup...
copy /Y "%MAIN_FILE%" "%MAIN_FILE%.bak"

echo """
Main routes for the KPI system
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """
    Index page - redirects to welcome for authenticated users
    or to login page for anonymous users
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.welcome'))
    else:
        return redirect(url_for('auth.login'))

@bp.route('/about')
@login_required
def about():
    """
    About page with system information
    """
    return render_template('about.html')

@bp.route('/welcome')
@login_required
def welcome():
    """
    Welcome page for authenticated users
    """
    return render_template('welcome.html')
> "%MAIN_FILE%"

REM Step 5: Update routes/__init__.py to avoid importing all modules
echo.
echo Step 5: Updating routes/__init__.py...
set ROUTES_INIT=%INSTALLED_APP%\app\routes\__init__.py
echo Creating backup...
copy /Y "%ROUTES_INIT%" "%ROUTES_INIT%.bak"

echo """Routes package for the KPI system""" > "%ROUTES_INIT%"
echo. >> "%ROUTES_INIT%"
echo # Individual route imports will be done directly in app/__init__.py >> "%ROUTES_INIT%"
echo # This prevents circular imports and allows selective importing >> "%ROUTES_INIT%"
echo. >> "%ROUTES_INIT%"
echo __all__ = [] >> "%ROUTES_INIT%"

REM Step 6: Create a simplified __init__.py that doesn't import reports
echo.
echo Step 6: Creating a simplified app initialization...
set INIT_FILE=%INSTALLED_APP%\app\__init__.py
echo Creating backup...
copy /Y "%INIT_FILE%" "%INIT_FILE%.bak2"

echo """
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
    
    # Direct import to avoid importing all routes at once
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    
    # Register only the essential blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    # Add favicon route to prevent 404 errors
    @app.route('/favicon.ico')
    def favicon():
        return '', 204  # Return empty response with No Content status
    
    # Setup context processors
    @app.context_processor
    def inject_app_info():
        return dict(
            app_name=app.config['APP_NAME'],
            app_version=app.config['APP_VERSION']
        )
    
    # Add context processor for templates to get current year
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow}
    
    # Restore template-based error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

# Create the Flask app instance for direct import
app = create_app()
> "%INIT_FILE%"

REM Step 7: Create a welcome template if it doesn't exist
echo.
echo Step 7: Creating a welcome template...
set TEMPLATE_DIR=%INSTALLED_APP%\app\templates
if not exist "%TEMPLATE_DIR%\welcome.html" (
    echo ^<!DOCTYPE html^> > "%TEMPLATE_DIR%\welcome.html"
    echo ^<html lang="en"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo ^<head^> >> "%TEMPLATE_DIR%\welcome.html"
    echo     ^<meta charset="UTF-8"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo     ^<meta name="viewport" content="width=device-width, initial-scale=1.0"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo     ^<title^>Welcome to Handyman KPI System^</title^> >> "%TEMPLATE_DIR%\welcome.html"
    echo     ^<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo ^</head^> >> "%TEMPLATE_DIR%\welcome.html"
    echo ^<body^> >> "%TEMPLATE_DIR%\welcome.html"
    echo     ^<div class="container mt-5"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo         ^<div class="row"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo             ^<div class="col-md-8 offset-md-2"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                 ^<div class="card shadow-sm"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                     ^<div class="card-body text-center"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                         ^<h1 class="display-4 mb-4"^>Welcome to Handyman KPI System^</h1^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                         ^<p class="lead"^>The system is currently in maintenance mode. Basic functionality is enabled.^</p^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                         ^<hr class="my-4"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                         ^<p^>Please check back later for full functionality including reports and dashboard.^</p^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                         ^<div class="mt-4"^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                             ^<a href="{{ url_for('main.index') }}" class="btn btn-primary me-2"^>Home^</a^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                             ^<a href="{{ url_for('auth.logout') }}" class="btn btn-outline-danger"^>Logout^</a^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                         ^</div^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                     ^</div^> >> "%TEMPLATE_DIR%\welcome.html"
    echo                 ^</div^> >> "%TEMPLATE_DIR%\welcome.html"
    echo             ^</div^> >> "%TEMPLATE_DIR%\welcome.html"
    echo         ^</div^> >> "%TEMPLATE_DIR%\welcome.html"
    echo     ^</div^> >> "%TEMPLATE_DIR%\welcome.html"
    echo     ^<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"^>^</script^> >> "%TEMPLATE_DIR%\welcome.html"
    echo ^</body^> >> "%TEMPLATE_DIR%\welcome.html"
    echo ^</html^> >> "%TEMPLATE_DIR%\welcome.html"
)

REM Step 8: Fix base.html template
echo.
echo Step 8: Fixing base.html template...
set BASE_TEMPLATE=%INSTALLED_APP%\app\templates\base.html
echo Creating backup...
copy /Y "%BASE_TEMPLATE%" "%BASE_TEMPLATE%.bak"

echo ^<!DOCTYPE html^> > "%BASE_TEMPLATE%"
echo ^<html lang="en"^> >> "%BASE_TEMPLATE%"
echo ^<head^> >> "%BASE_TEMPLATE%"
echo     ^<meta charset="UTF-8"^> >> "%BASE_TEMPLATE%"
echo     ^<meta name="viewport" content="width=device-width, initial-scale=1.0"^> >> "%BASE_TEMPLATE%"
echo     ^<title^>{% block title %}Handyman KPI System{% endblock %}^</title^> >> "%BASE_TEMPLATE%"
echo     ^<!-- Bootstrap CSS --^> >> "%BASE_TEMPLATE%"
echo     ^<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet"^> >> "%BASE_TEMPLATE%"
echo     ^<!-- Custom CSS --^> >> "%BASE_TEMPLATE%"
echo     ^<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}"^> >> "%BASE_TEMPLATE%"
echo     ^<!-- Font Awesome --^> >> "%BASE_TEMPLATE%"
echo     ^<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"^> >> "%BASE_TEMPLATE%"
echo     {% block styles %}{% endblock %} >> "%BASE_TEMPLATE%"
echo ^</head^> >> "%BASE_TEMPLATE%"
echo ^<body^> >> "%BASE_TEMPLATE%"
echo     ^<header^> >> "%BASE_TEMPLATE%"
echo         ^<nav class="navbar navbar-expand-lg navbar-dark bg-primary"^> >> "%BASE_TEMPLATE%"
echo             ^<div class="container"^> >> "%BASE_TEMPLATE%"
echo                 ^<a class="navbar-brand" href="{{ url_for('main.index') }}"^> >> "%BASE_TEMPLATE%"
echo                     ^<i class="fas fa-tools me-2"^>^</i^> Handyman KPI System >> "%BASE_TEMPLATE%"
echo                 ^</a^> >> "%BASE_TEMPLATE%"
echo                 ^<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation"^> >> "%BASE_TEMPLATE%"
echo                     ^<span class="navbar-toggler-icon"^>^</span^> >> "%BASE_TEMPLATE%"
echo                 ^</button^> >> "%BASE_TEMPLATE%"
echo                 ^<div class="collapse navbar-collapse" id="navbarNav"^> >> "%BASE_TEMPLATE%"
echo                     ^<ul class="navbar-nav me-auto"^> >> "%BASE_TEMPLATE%"
echo                         ^<li class="nav-item"^> >> "%BASE_TEMPLATE%"
echo                             ^<a class="nav-link" href="{{ url_for('main.index') }}"^>Home^</a^> >> "%BASE_TEMPLATE%"
echo                         ^</li^> >> "%BASE_TEMPLATE%"
echo                         {% if current_user.is_authenticated %} >> "%BASE_TEMPLATE%"
echo                         ^<li class="nav-item"^> >> "%BASE_TEMPLATE%"
echo                             ^<a class="nav-link" href="{{ url_for('main.welcome') }}"^>Welcome^</a^> >> "%BASE_TEMPLATE%"
echo                         ^</li^> >> "%BASE_TEMPLATE%"
echo                         {% endif %} >> "%BASE_TEMPLATE%"
echo                     ^</ul^> >> "%BASE_TEMPLATE%"
echo                     ^<ul class="navbar-nav ms-auto"^> >> "%BASE_TEMPLATE%"
echo                         {% if current_user.is_authenticated %} >> "%BASE_TEMPLATE%"
echo                         ^<li class="nav-item dropdown"^> >> "%BASE_TEMPLATE%"
echo                             ^<a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false"^> >> "%BASE_TEMPLATE%"
echo                                 ^<i class="fas fa-user me-1"^>^</i^>{{ current_user.username }} >> "%BASE_TEMPLATE%"
echo                             ^</a^> >> "%BASE_TEMPLATE%"
echo                             ^<ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown"^> >> "%BASE_TEMPLATE%"
echo                                 ^<li^>^<a class="dropdown-item" href="{{ url_for('auth.profile') }}"^>Profile^</a^>^</li^> >> "%BASE_TEMPLATE%"
echo                                 ^<li^>^<hr class="dropdown-divider"^>^</li^> >> "%BASE_TEMPLATE%"
echo                                 ^<li^>^<a class="dropdown-item" href="{{ url_for('auth.logout') }}"^>Logout^</a^>^</li^> >> "%BASE_TEMPLATE%"
echo                             ^</ul^> >> "%BASE_TEMPLATE%"
echo                         ^</li^> >> "%BASE_TEMPLATE%"
echo                         {% else %} >> "%BASE_TEMPLATE%"
echo                         ^<li class="nav-item"^> >> "%BASE_TEMPLATE%"
echo                             ^<a class="nav-link" href="{{ url_for('auth.login') }}"^>Login^</a^> >> "%BASE_TEMPLATE%"
echo                         ^</li^> >> "%BASE_TEMPLATE%"
echo                         {% endif %} >> "%BASE_TEMPLATE%"
echo                     ^</ul^> >> "%BASE_TEMPLATE%"
echo                 ^</div^> >> "%BASE_TEMPLATE%"
echo             ^</div^> >> "%BASE_TEMPLATE%"
echo         ^</nav^> >> "%BASE_TEMPLATE%"
echo     ^</header^> >> "%BASE_TEMPLATE%"
echo. >> "%BASE_TEMPLATE%"
echo     ^<main class="container mt-4"^> >> "%BASE_TEMPLATE%"
echo         {% with messages = get_flashed_messages(with_categories=true) %} >> "%BASE_TEMPLATE%"
echo             {% if messages %} >> "%BASE_TEMPLATE%"
echo                 {% for category, message in messages %} >> "%BASE_TEMPLATE%"
echo                     ^<div class="alert alert-{{ category }} alert-dismissible fade show" role="alert"^> >> "%BASE_TEMPLATE%"
echo                         {{ message }} >> "%BASE_TEMPLATE%"
echo                         ^<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"^>^</button^> >> "%BASE_TEMPLATE%"
echo                     ^</div^> >> "%BASE_TEMPLATE%"
echo                 {% endfor %} >> "%BASE_TEMPLATE%"
echo             {% endif %} >> "%BASE_TEMPLATE%"
echo         {% endwith %} >> "%BASE_TEMPLATE%"
echo. >> "%BASE_TEMPLATE%"
echo         {% block content %}{% endblock %} >> "%BASE_TEMPLATE%"
echo     ^</main^> >> "%BASE_TEMPLATE%"
echo. >> "%BASE_TEMPLATE%"
echo     ^<footer class="container mt-5 mb-3"^> >> "%BASE_TEMPLATE%"
echo         ^<hr^> >> "%BASE_TEMPLATE%"
echo         ^<p class="text-center text-muted"^> >> "%BASE_TEMPLATE%"
echo             ^&copy; {{ now().year }} Handyman KPI System | Version {{ app_version }} >> "%BASE_TEMPLATE%"
echo         ^</p^> >> "%BASE_TEMPLATE%"
echo     ^</footer^> >> "%BASE_TEMPLATE%"
echo. >> "%BASE_TEMPLATE%"
echo     ^<!-- Bootstrap Bundle with Popper --^> >> "%BASE_TEMPLATE%"
echo     ^<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"^>^</script^> >> "%BASE_TEMPLATE%"
echo     ^<!-- Custom JavaScript --^> >> "%BASE_TEMPLATE%"
echo     ^<script src="{{ url_for('static', filename='js/script.js') }}"^>^</script^> >> "%BASE_TEMPLATE%"
echo     {% block scripts %}{% endblock %} >> "%BASE_TEMPLATE%"
echo ^</body^> >> "%BASE_TEMPLATE%"
echo ^</html^> >> "%BASE_TEMPLATE%"

echo.
echo Fix completed! Please try starting the application again.
echo.
echo Note: This fix disables the PDF reports functionality and other advanced
echo features to allow basic authentication to work. The WeasyPrint library
echo requires additional system dependencies (GTK libraries) that would need
echo to be installed separately for full functionality.
echo.
echo A more comprehensive solution would be to either:
echo 1. Install the required system dependencies for WeasyPrint
echo 2. Modify the application to use a different PDF generation library
echo 3. Create a completely separate report generation module that runs on demand

pause
