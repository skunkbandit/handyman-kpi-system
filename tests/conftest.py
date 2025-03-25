"""
Test configuration for pytest.
This file contains fixtures and configuration settings for all tests.
"""
import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Adjust path to import from our application
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import models and application after path adjustment
from kpi_system.backend.app import create_app
from kpi_system.backend.app.models.user import User
from kpi_system.backend.app.models.employee import Employee
from kpi_system.backend.app.models.skill import SkillCategory, Skill
from kpi_system.backend.app.models.tool import ToolCategory, Tool
from kpi_system.backend.app.models.evaluation import Evaluation, EvalSkill, EvalTool

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Create the database and tables
    with app.app_context():
        from kpi_system.backend.app.models import db
        db.create_all()
        
        # Load test data
        _load_test_data(db.session)
        
    yield app
    
    # Clean up
    with app.app_context():
        from kpi_system.backend.app.models import db
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Creates a new database session for testing."""
    with app.app_context():
        from kpi_system.backend.app.models import db
        connection = db.engine.connect()
        transaction = connection.begin()
        
        session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=connection)
        )
        
        yield session
        
        session.close()
        transaction.rollback()
        connection.close()

def _load_test_data(session):
    """Load test data into the database."""
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin'
    )
    admin.set_password('adminpass')
    session.add(admin)
    
    # Create manager user
    manager = User(
        username='manager',
        email='manager@example.com',
        role='manager'
    )
    manager.set_password('managerpass')
    session.add(manager)
    
    # Create employee user
    employee_user = User(
        username='employee',
        email='employee@example.com',
        role='employee'
    )
    employee_user.set_password('employeepass')
    session.add(employee_user)
    
    # Create test employees
    employee1 = Employee(
        first_name='John',
        last_name='Doe',
        tier='Craftsman',
        hire_date='2023-01-15',
        active=True,
        user_id=employee_user.id
    )
    session.add(employee1)
    
    employee2 = Employee(
        first_name='Jane',
        last_name='Smith',
        tier='Master Craftsman',
        hire_date='2022-05-10',
        active=True
    )
    session.add(employee2)
    
    # Create skill categories and skills
    carpentry = SkillCategory(name='Carpentry')
    session.add(carpentry)
    
    plumbing = SkillCategory(name='Plumbing')
    session.add(plumbing)
    
    electrical = SkillCategory(name='Electrical')
    session.add(electrical)
    
    # Add specific skills
    session.add(Skill(name='Framing', category=carpentry))
    session.add(Skill(name='Cabinet Installation', category=carpentry))
    session.add(Skill(name='Pipe Fitting', category=plumbing))
    session.add(Skill(name='Fixture Installation', category=plumbing))
    session.add(Skill(name='Wiring', category=electrical))
    session.add(Skill(name='Circuit Testing', category=electrical))
    
    # Create tool categories and tools
    hand_tools = ToolCategory(name='Hand Tools')
    session.add(hand_tools)
    
    power_tools = ToolCategory(name='Power Tools')
    session.add(power_tools)
    
    # Add specific tools
    session.add(Tool(name='Hammer', category=hand_tools))
    session.add(Tool(name='Screwdriver Set', category=hand_tools))
    session.add(Tool(name='Circular Saw', category=power_tools))
    session.add(Tool(name='Drill', category=power_tools))
    
    # Commit all test data
    session.commit()
