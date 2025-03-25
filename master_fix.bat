@echo off
echo ================================================
echo Handyman KPI System - Master Fix Script
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

REM Step 4: Fix base.html template
echo.
echo Step 4: Fixing base.html template...
copy /Y "C:\Users\dtest\KPI Project\fixed_base.html" "%INSTALLED_APP%\app\templates\base.html"

REM Step 5: Re-enable dashboard blueprint
echo.
echo Step 5: Checking and fixing dashboard blueprint...
set INIT_FILE=%INSTALLED_APP%\app\__init__.py
copy /Y "%INIT_FILE%" "%INIT_FILE%.bak"

REM Create our own fixed version of the init file
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
echo     # Register blueprints - Import directly to match the expected names >> fixed_init.py
echo     # in the routes/__init__.py file >> fixed_init.py
echo     from app.routes.main import bp as main_bp >> fixed_init.py
echo     from app.routes.auth import bp as auth_bp >> fixed_init.py
echo. >> fixed_init.py
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

echo.
echo Fix completed! Please try starting the application again.
echo.
cd /d "C:\Users\dtest\KPI Project"
echo Note: If you continue to experience issues, please reinstall the application and apply this fix again.
echo.

pause
