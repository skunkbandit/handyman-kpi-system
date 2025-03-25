# Code Organization

This document explains the organization and structure of the Handyman KPI System codebase.

## Table of Contents

- [Overview](#overview)
- [Directory Structure](#directory-structure)
- [Application Structure](#application-structure)
- [Module Organization](#module-organization)
- [Coding Patterns](#coding-patterns)
- [Dependency Management](#dependency-management)
- [Configuration Management](#configuration-management)
- [Static Assets](#static-assets)
- [Templates](#templates)
- [Database Access](#database-access)

## Overview

The Handyman KPI System follows a modular architecture based on the Flask web framework. The codebase is organized to promote:

- **Separation of Concerns**: Distinct layers for models, views, and business logic
- **Modularity**: Functionality divided into self-contained components
- **Testability**: Structure supports comprehensive automated testing
- **Maintainability**: Clear organization makes the code easier to understand and modify
- **Scalability**: Design allows for future growth and extension

## Directory Structure

The top-level directory structure organizes code by its role in the system:

```
handyman-kpi-system/
├── kpi-system/                # Main application code
│   ├── backend/               # Backend code
│   │   ├── app/               # Application package
│   │   │   ├── models/        # Database models
│   │   │   ├── routes/        # Route blueprints
│   │   │   ├── static/        # Static assets
│   │   │   ├── templates/     # HTML templates
│   │   │   ├── utils/         # Utility functions
│   │   │   └── __init__.py    # Application factory
│   │   └── run.py             # Development entry point
│   ├── config.py              # Configuration settings
│   ├── database/              # Database scripts
│   ├── docs/                  # Documentation
│   ├── frontend/              # Frontend code (if separate)
│   └── requirements.txt       # Dependencies
├── database/                  # Database migration files
├── scripts/                   # Utility scripts
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── ui/                    # UI tests
├── .env.example               # Environment variables template
├── docker-compose.yml         # Production Docker setup
├── docker-compose.dev.yml     # Development Docker setup
└── Dockerfile                 # Docker image definition
```

## Application Structure

The application follows a blueprint-based structure, dividing functionality into modular components:

### Application Factory

The application is initialized using the application factory pattern in `app/__init__.py`:

```python
def create_app(config_object=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(get_config())
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # ... other extensions
    
    # Register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.employees import employees_bp
    app.register_blueprint(employees_bp, url_prefix='/employees')
    
    from app.routes.evaluations import evaluations_bp
    app.register_blueprint(evaluations_bp, url_prefix='/evaluations')
    
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    from app.routes.reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Configure logging
    configure_logging(app)
    
    return app
```

### Blueprints

The application is divided into functional blueprints:

| Blueprint | Purpose | URL Prefix |
|-----------|---------|------------|
| `main` | Basic pages (home, about) | `/` |
| `auth` | Authentication and user management | `/auth` |
| `employees` | Employee record management | `/employees` |
| `evaluations` | Skill and tool evaluations | `/evaluations` |
| `dashboard` | Performance visualizations | `/dashboard` |
| `reports` | Report generation | `/reports` |
| `admin` | System administration | `/admin` |
| `api` | REST API endpoints | `/api` |

Each blueprint is defined in a separate module within the `routes` directory.

## Module Organization

### Models

Database models are organized by domain entity in the `models` directory:

```
app/models/
├── __init__.py           # Exports all models
├── employee.py           # Employee model
├── evaluation.py         # Evaluation models
├── skill.py              # Skill and category models
├── tool.py               # Tool and category models
├── user.py               # User model
└── mixins.py             # Shared model functionality
```

Each model file contains related models and their relationships. For example, `skill.py` contains:

```python
class SkillCategory(db.Model):
    """Skill category model."""
    __tablename__ = 'skill_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    display_order = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('Skill', back_populates='category', cascade='all, delete-orphan')


class Skill(db.Model):
    """Skill model."""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('skill_categories.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('SkillCategory', back_populates='skills')
    eval_skills = db.relationship('EvalSkill', back_populates='skill')
```

### Routes

Routes are organized by functional area, with each blueprint in a separate module:

```
app/routes/
├── __init__.py           # Blueprint registration
├── admin.py              # Admin routes
├── auth.py               # Authentication routes
├── dashboard.py          # Dashboard routes
├── employees.py          # Employee management routes
├── evaluations.py        # Evaluation routes
├── main.py               # Main routes
└── reports.py            # Report generation routes
```

Each route module defines a blueprint and its routes:

```python
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.models import Employee, Evaluation
from app.utils.access_control import manager_required

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/')
@login_required
def index():
    """List all employees."""
    employees = Employee.query.filter_by(active=True).all()
    return render_template('employees/index.html', employees=employees)

@employees_bp.route('/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create():
    """Create a new employee."""
    # Implementation...
```

### Templates

Templates follow a hierarchical structure aligned with blueprints:

```
app/templates/
├── base.html                 # Base layout template
├── about.html                # About page
├── index.html                # Home page
├── admin/                    # Admin templates
│   ├── admin_base.html       # Admin-specific base layout
│   ├── dashboard.html        # Admin dashboard
│   ├── settings.html         # System settings
│   └── user_management.html  # User management
├── auth/                     # Authentication templates
│   ├── login.html            # Login form
│   ├── reset_password.html   # Password reset
│   └── profile.html          # User profile
├── dashboard/                # Dashboard templates
│   └── index.html            # Main dashboard
├── employees/                # Employee templates
│   ├── create.html           # Create employee form
│   ├── edit.html             # Edit employee form
│   ├── index.html            # Employee list
│   └── view.html             # Employee detail view
└── evaluations/              # Evaluation templates
    ├── create.html           # Create evaluation form
    ├── edit.html             # Edit evaluation form
    ├── index.html            # Evaluation list
    └── view.html             # Evaluation detail view
```

### Utilities

Utility functions are organized by purpose:

```
app/utils/
├── __init__.py               # Exports utility functions
├── access_control.py         # Authorization decorators
├── db_maintenance.py         # Database maintenance utilities
├── email.py                  # Email sending utilities
├── logging_config.py         # Logging configuration
└── monitoring.py             # System monitoring utilities
```

## Coding Patterns

### Data Access

Data access follows the repository pattern, with SQLAlchemy models and query methods:

```python
# Direct model access for simple queries
employees = Employee.query.filter_by(tier_level=3).all()

# Repository pattern for complex queries
def get_employee_with_skills(employee_id):
    """Get employee with skills, categorized by skill category."""
    employee = Employee.query.get_or_404(employee_id)
    
    # Get all categories and skills
    categories = SkillCategory.query.order_by(SkillCategory.display_order).all()
    
    # Get latest evaluation for this employee
    latest_eval = Evaluation.query.filter_by(employee_id=employee_id) \
        .order_by(Evaluation.evaluation_date.desc()) \
        .first()
    
    # Build skill data structure
    skill_data = []
    for category in categories:
        category_data = {
            'id': category.id,
            'name': category.name,
            'skills': []
        }
        
        for skill in category.skills:
            skill_rating = None
            if latest_eval:
                eval_skill = EvalSkill.query.filter_by(
                    evaluation_id=latest_eval.id,
                    skill_id=skill.id
                ).first()
                if eval_skill:
                    skill_rating = eval_skill.rating
            
            category_data['skills'].append({
                'id': skill.id,
                'name': skill.name,
                'rating': skill_rating
            })
        
        skill_data.append(category_data)
    
    return employee, skill_data
```

### Form Handling

Forms use Flask-WTF with consistent patterns:

```python
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class EmployeeForm(FlaskForm):
    """Form for creating and editing employees."""
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    tier_level = SelectField('Tier Level', choices=[
        (1, 'Apprentice'),
        (2, 'Handyman'),
        (3, 'Craftsman'),
        (4, 'Master Craftsman'),
        (5, 'Lead Craftsman')
    ], coerce=int, validators=[DataRequired()])
    hire_date = DateField('Hire Date', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
```

### Authentication and Authorization

Authentication uses Flask-Login:

```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html', form=form)
```

Authorization uses custom decorators:

```python
def admin_required(f):
    """Decorator for routes that require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """Decorator for routes that require manager access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (current_user.is_admin or current_user.is_manager):
            flash('Manager access required', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
```

## Dependency Management

Dependencies are managed through `requirements.txt` files:

- `requirements.txt`: Core dependencies for production
- `requirements-dev.txt`: Additional dependencies for development and testing

The main dependencies include:

```
# Web Framework
Flask==2.0.1
Werkzeug==2.0.1

# Database
Flask-SQLAlchemy==2.5.1
SQLAlchemy==1.4.23
Flask-Migrate==3.1.0
alembic==1.7.1

# Forms and Validation
Flask-WTF==0.15.1
WTForms==2.3.3
email-validator==1.1.3

# Authentication
Flask-Login==0.5.0

# API
Flask-RESTful==0.3.9
marshmallow==3.13.0

# Utilities
python-dotenv==0.19.0
Pillow==8.3.1
pdfkit==1.0.0
xlsxwriter==3.0.1

# Testing
pytest==6.2.5
pytest-flask==1.2.0
coverage==6.0.1
```

## Configuration Management

Configuration uses a class-based approach with environment-specific subclasses:

```python
class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///kpi.db')
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 't', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # General settings
    COMPANY_NAME = os.environ.get('COMPANY_NAME', 'Handyman Company')
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # Security
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


def get_config():
    """Return the appropriate configuration class based on the environment."""
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)
```

## Static Assets

Static assets are organized by type:

```
app/static/
├── css/
│   ├── style.css                # Main CSS styles
│   ├── dashboard.css            # Dashboard-specific styles
│   └── admin.css                # Admin interface styles
├── js/
│   ├── script.js                # Main JavaScript
│   ├── chart-config.js          # Chart configuration
│   ├── evaluations.js           # Evaluation form handlers
│   └── reports.js               # Report generation logic
├── img/
│   ├── logo.png                 # Company logo
│   ├── favicon.ico              # Site favicon
│   └── icons/                   # UI icons
└── vendor/                      # Third-party libraries
    ├── bootstrap/               # Bootstrap framework
    ├── chartjs/                 # Chart.js library
    └── fontawesome/             # Font Awesome icons
```

## Templates

Templates use Jinja2 with a base template system:

```html
<!-- base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Handyman KPI System{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='vendor/bootstrap/css/bootstrap.min.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block styles %}{% endblock %}
</head>
<body>
    {% include 'includes/header.html' %}
    
    <div class="container mt-4">
        {% include 'includes/flash.html' %}
        
        {% block content %}
        {% endblock %}
    </div>
    
    {% include 'includes/footer.html' %}
    
    <script src="{{ url_for('static', filename='vendor/bootstrap/js/bootstrap.bundle.min.js') }}"></script>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

Page templates extend the base template:

```html
<!-- employees/index.html -->
{% extends 'base.html' %}

{% block title %}Employees | Handyman KPI System{% endblock %}

{% block content %}
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h2>Employees</h2>
        {% if current_user.is_manager or current_user.is_admin %}
        <a href="{{ url_for('employees.create') }}" class="btn btn-primary">Add Employee</a>
        {% endif %}
    </div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Tier</th>
                        <th>Hire Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for employee in employees %}
                    <tr>
                        <td>{{ employee.first_name }} {{ employee.last_name }}</td>
                        <td>{{ employee.get_tier_name() }}</td>
                        <td>{{ employee.hire_date.strftime('%Y-%m-%d') }}</td>
                        <td>
                            <a href="{{ url_for('employees.view', id=employee.id) }}" class="btn btn-sm btn-outline-primary">View</a>
                            {% if current_user.is_manager or current_user.is_admin %}
                            <a href="{{ url_for('employees.edit', id=employee.id) }}" class="btn btn-sm btn-outline-secondary">Edit</a>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/employees.js') }}"></script>
{% endblock %}
```

## Database Access

Database access uses SQLAlchemy with migrations handled by Alembic/Flask-Migrate:

```python
# Database instance
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Migration instance
from flask_migrate import Migrate
migrate = Migrate()

# Initialize in application factory
def create_app(config_object=None):
    app = Flask(__name__)
    # ...
    db.init_app(app)
    migrate.init_app(app, db)
    # ...
```

Migrations are managed through command-line tools:

```bash
# Initialize migrations directory (first time only)
flask db init

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migrations
flask db downgrade
```

Custom migration scripts handle structural changes and data migrations:

```python
# migrations/versions/1a2b3c4d5e6f_add_evaluations_table.py
"""add evaluations table

Revision ID: 1a2b3c4d5e6f
Revises: previous_revision_id
Create Date: 2025-03-10 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '1a2b3c4d5e6f'
down_revision = 'previous_revision_id'
branch_labels = None
depends_on = None


def upgrade():
    # Create evaluations table
    op.create_table(
        'evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('evaluation_date', sa.Date(), nullable=False),
        sa.Column('evaluator_id', sa.Integer(), nullable=True),
        sa.Column('evaluation_type', sa.String(length=10), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['evaluator_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_evaluations_employee_id'), 'evaluations', ['employee_id'], unique=False)
    op.create_index(op.f('ix_evaluations_evaluation_date'), 'evaluations', ['evaluation_date'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_evaluations_evaluation_date'), table_name='evaluations')
    op.drop_index(op.f('ix_evaluations_employee_id'), table_name='evaluations')
    
    # Drop table
    op.drop_table('evaluations')
```
