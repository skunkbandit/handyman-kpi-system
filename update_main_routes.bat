@echo off
echo ================================================
echo Handyman KPI System - Update Main Routes Fix
echo ================================================
echo.

set INSTALLED_APP=C:\Users\dtest\AppData\Local\Programs\Handyman KPI System

REM Step 1: Stopping any running instances
echo Step 1: Stopping any running instances...
taskkill /F /IM python.exe 2>nul

REM Step 2: Update the main.py routes file
echo.
echo Step 2: Updating main routes...
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
    Index page - redirects to dashboard for authenticated users
    or to login page for anonymous users
    """
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
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

echo.
echo Fix completed! Please run the disable_pdf_reports.bat script next,
echo then try starting the application again.
echo.

pause
