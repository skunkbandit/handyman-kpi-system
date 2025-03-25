@echo off
echo ================================================
echo Handyman KPI System - Disable PDF Reports Fix
echo ================================================
echo.

set INSTALLED_APP=C:\Users\dtest\AppData\Local\Programs\Handyman KPI System

REM Step 1: Stopping any running instances
echo Step 1: Stopping any running instances...
taskkill /F /IM python.exe 2>nul

REM Step 2: Create a simplified __init__.py that doesn't import reports
echo.
echo Step 2: Creating a simplified app initialization...
set INIT_FILE=%INSTALLED_APP%\app\__init__.py
echo Creating backup...
copy /Y "%INIT_FILE%" "%INIT_FILE%.bak2"

echo Creating simplified init file...
echo """ > fixed_init.py
echo Flask application factory for the KPI system >> fixed_init.py
echo """ >> fixed_init.py
echo import os >> fixed_init.py
echo from flask import Flask, redirect, url_for, render_template, send_from_directory >> fixed_init.py
echo from flask_sqlalchemy import SQLAlchemy >> fixed_init.py
echo from flask_login import LoginManager >> fixed_init.py
echo from flask_wtf.csrf import CSRFProtect >> fixed_init.py
echo. >> fixed_init.py
echo # Create extension instances >> fixed_init.py
echo db = SQLAlchemy() >> fixed_init.py
echo login_manager = LoginManager() >> fixed_init.py
echo csrf = CSRFProtect() >> fixed_init.py
echo. >> fixed_init.py
echo def create_app(test_config=None): >> fixed_init.py
echo     """ >> fixed_init.py
echo     Create and configure the Flask application >> fixed_init.py
echo     """ >> fixed_init.py
echo     # Create app instance >> fixed_init.py
echo     app = Flask(__name__, instance_relative_config=True) >> fixed_init.py
echo. >> fixed_init.py
echo     # Default configuration >> fixed_init.py
echo     app.config.from_mapping( >> fixed_init.py
echo         SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_not_for_production'), >> fixed_init.py
echo         SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'database', 'kpi_system.db')}", >> fixed_init.py
echo         SQLALCHEMY_TRACK_MODIFICATIONS=False, >> fixed_init.py
echo         APP_NAME='Handyman KPI System', >> fixed_init.py
echo         APP_VERSION='1.0.0', >> fixed_init.py
echo         WTF_CSRF_ENABLED=True, >> fixed_init.py
echo         REMEMBER_COOKIE_DURATION=86400,  # 1 day in seconds >> fixed_init.py
echo         REMEMBER_COOKIE_SECURE=False,    # Set to True in production with HTTPS >> fixed_init.py
echo         REMEMBER_COOKIE_HTTPONLY=True >> fixed_init.py
echo     ) >> fixed_init.py
echo. >> fixed_init.py
echo     # Load test config if passed in >> fixed_init.py
echo     if test_config is not None: >> fixed_init.py
echo         app.config.from_mapping(test_config) >> fixed_init.py
echo. >> fixed_init.py
echo     # Ensure the instance folder exists >> fixed_init.py
echo     try: >> fixed_init.py
echo         os.makedirs(app.instance_path) >> fixed_init.py
echo     except OSError: >> fixed_init.py
echo         pass >> fixed_init.py
echo. >> fixed_init.py
echo     # Initialize extensions with app >> fixed_init.py
echo     db.init_app(app) >> fixed_init.py
echo     csrf.init_app(app) >> fixed_init.py
echo. >> fixed_init.py
echo     # Configure Flask-Login >> fixed_init.py
echo     login_manager.init_app(app) >> fixed_init.py
echo     login_manager.login_view = 'auth.login' >> fixed_init.py
echo     login_manager.login_message = 'Please log in to access this page.' >> fixed_init.py
echo     login_manager.login_message_category = 'info' >> fixed_init.py
echo. >> fixed_init.py
echo     @login_manager.user_loader >> fixed_init.py
echo     def load_user(user_id): >> fixed_init.py
echo         from app.models.user import User >> fixed_init.py
echo         return User.query.get(int(user_id)) >> fixed_init.py
echo. >> fixed_init.py
echo     # Direct import to avoid importing all routes at once >> fixed_init.py
echo     from app.routes.main import bp as main_bp >> fixed_init.py
echo     from app.routes.auth import bp as auth_bp >> fixed_init.py
echo. >> fixed_init.py
echo     # Register only the essential blueprints >> fixed_init.py
echo     app.register_blueprint(main_bp) >> fixed_init.py
echo     app.register_blueprint(auth_bp) >> fixed_init.py
echo. >> fixed_init.py
echo     # Add favicon route to prevent 404 errors >> fixed_init.py
echo     @app.route('/favicon.ico') >> fixed_init.py
echo     def favicon(): >> fixed_init.py
echo         return '', 204  # Return empty response with No Content status >> fixed_init.py
echo. >> fixed_init.py
echo     # Setup context processors >> fixed_init.py
echo     @app.context_processor >> fixed_init.py
echo     def inject_app_info(): >> fixed_init.py
echo         return dict( >> fixed_init.py
echo             app_name=app.config['APP_NAME'], >> fixed_init.py
echo             app_version=app.config['APP_VERSION'] >> fixed_init.py
echo         ) >> fixed_init.py
echo. >> fixed_init.py
echo     # Add context processor for templates to get current year >> fixed_init.py
echo     @app.context_processor >> fixed_init.py
echo     def inject_now(): >> fixed_init.py
echo         from datetime import datetime >> fixed_init.py
echo         return {'now': datetime.utcnow} >> fixed_init.py
echo. >> fixed_init.py
echo     # Add welcome route >> fixed_init.py
echo     @app.route('/welcome') >> fixed_init.py
echo     def welcome(): >> fixed_init.py
echo         return render_template('welcome.html') >> fixed_init.py
echo. >> fixed_init.py
echo     # Restore template-based error handlers >> fixed_init.py
echo     @app.errorhandler(404) >> fixed_init.py
echo     def page_not_found(e): >> fixed_init.py
echo         return render_template('errors/404.html'), 404 >> fixed_init.py
echo. >> fixed_init.py
echo     @app.errorhandler(403) >> fixed_init.py
echo     def forbidden(e): >> fixed_init.py
echo         return render_template('errors/403.html'), 403 >> fixed_init.py
echo. >> fixed_init.py
echo     @app.errorhandler(500) >> fixed_init.py
echo     def server_error(e): >> fixed_init.py
echo         return render_template('errors/500.html'), 500 >> fixed_init.py
echo. >> fixed_init.py
echo     return app >> fixed_init.py
echo. >> fixed_init.py
echo # Create the Flask app instance for direct import >> fixed_init.py
echo app = create_app() >> fixed_init.py

copy /Y fixed_init.py "%INIT_FILE%"
del fixed_init.py

REM Step 3: Create a welcome template if it doesn't exist
echo.
echo Step 3: Creating a welcome template...
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
    echo                             ^<a href="{{ url_for('auth.login') }}" class="btn btn-outline-primary"^>Login^</a^> >> "%TEMPLATE_DIR%\welcome.html"
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

REM Step 4: Update routes/__init__.py to avoid importing all modules
echo.
echo Step 4: Updating routes/__init__.py...
set ROUTES_INIT=%INSTALLED_APP%\app\routes\__init__.py
echo Creating backup...
copy /Y "%ROUTES_INIT%" "%ROUTES_INIT%.bak"

echo """Routes package for the KPI system""" > fixed_routes_init.py
echo. >> fixed_routes_init.py
echo # Individual route imports will be done directly in app/__init__.py >> fixed_routes_init.py
echo # This prevents circular imports and allows selective importing >> fixed_routes_init.py
echo. >> fixed_routes_init.py
echo __all__ = [] >> fixed_routes_init.py

copy /Y fixed_routes_init.py "%ROUTES_INIT%"
del fixed_routes_init.py

echo.
echo Fix completed! Please try starting the application again.
echo.
echo Note: This fix disables the PDF reports functionality to allow basic
echo authentication to work. The WeasyPrint library requires additional
echo system dependencies (GTK libraries) that would need to be installed
echo separately for full functionality.

pause
