"""
KPI System Main Application
----------------------------
Flask application for the handyman business KPI tracking system.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///../database/kpi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Import models
from models.employee import Employee
from models.evaluation import Evaluation, EvalSkill, EvalTool
from models.skill import SkillCategory, Skill
from models.tool import ToolCategory, Tool
from models.user import User
from models.special_skill import SpecialSkill

# Import routes
from routes.auth import auth_bp
from routes.employees import employees_bp
from routes.evaluations import evaluations_bp
from routes.dashboard import dashboard_bp
from routes.reports import reports_bp
from routes.admin import admin_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(employees_bp)
app.register_blueprint(evaluations_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    """Home page route."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('dashboard.index'))

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(debug=True)