# Testing Framework Documentation

This guide covers the testing framework for the Handyman KPI System, including unit tests, integration tests, and UI tests.

## Table of Contents

- [Testing Overview](#testing-overview)
- [Test Organization](#test-organization)
- [Test Environment](#test-environment)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [UI Tests](#ui-tests)
- [Test Fixtures](#test-fixtures)
- [Mocking](#mocking)
- [Continuous Integration](#continuous-integration)
- [Code Coverage](#code-coverage)
- [Test Reports](#test-reports)

## Testing Overview

The Handyman KPI System uses a comprehensive testing approach with three main types of tests:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **UI Tests**: Test the user interface and end-to-end workflows

The testing framework is built on:
- **pytest**: For test discovery, execution, and assertions
- **pytest-flask**: For Flask application testing
- **coverage**: For measuring code coverage
- **selenium**: For UI testing

## Test Organization

Tests are organized in the `tests/` directory with the following structure:

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── run_tests.py                # Test runner script
├── __init__.py                 # Makes tests importable
├── unit/                       # Unit tests
│   ├── test_employee_model.py
│   ├── test_evaluation_model.py
│   ├── test_skill_model.py
│   ├── test_tool_model.py
│   └── test_user_model.py
├── integration/                # Integration tests
│   ├── test_admin_routes.py
│   ├── test_auth_routes.py
│   ├── test_dashboard_routes.py
│   ├── test_database_migration.py
│   ├── test_employee_routes.py
│   ├── test_error_handling.py
│   ├── test_evaluation_routes.py
│   └── test_reports_routes.py
└── ui/                         # UI tests
    ├── base.py                 # Base test class for UI tests
    ├── test_employee_management.py
    └── test_responsive_design.py
```

## Test Environment

Tests run in a dedicated test environment with:
- In-memory SQLite database
- Test-specific configuration
- Disabled external services (email, notifications)
- Test fixtures and sample data

### Configuration

Test environment settings are defined in `config.py` under the `TestingConfig` class:

```python
class TestingConfig(Config):
    """Configuration for running tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    MAIL_SUPPRESS_SEND = True
```

## Running Tests

### Running All Tests

To run all tests:

```bash
# For Docker deployment
docker-compose exec web python -m pytest

# For traditional deployment
python -m pytest
```

### Running Specific Test Types

To run specific types of tests:

```bash
# Run only unit tests
python -m pytest tests/unit/

# Run only integration tests
python -m pytest tests/integration/

# Run only UI tests
python -m pytest tests/ui/
```

### Running Specific Test Files

To run tests from a specific file:

```bash
python -m pytest tests/unit/test_employee_model.py
```

### Running Specific Test Cases

To run a specific test case:

```bash
python -m pytest tests/unit/test_employee_model.py::TestEmployeeModel::test_create_employee
```

### Test Options

Common pytest options:

```bash
# Run tests in verbose mode
python -m pytest -v

# Show test progress
python -m pytest -v --show-progress

# Stop on first failure
python -m pytest -x

# Run tests matching a pattern
python -m pytest -k "employee"

# Collect test coverage data
python -m pytest --cov=app
```

## Writing Tests

### Unit Tests

Unit tests focus on testing individual components in isolation. They should be:
- Fast
- Independent
- Focused on a single component

Example unit test for the Employee model:

```python
def test_create_employee(app, db):
    """Test creating a new employee record."""
    employee = Employee(
        first_name="John",
        last_name="Smith",
        tier_level=3,
        hire_date=date(2023, 5, 15),
        active=True
    )
    db.session.add(employee)
    db.session.commit()
    
    # Verify the employee was created
    assert employee.id is not None
    assert employee.first_name == "John"
    assert employee.last_name == "Smith"
    assert employee.tier_level == 3
    assert employee.hire_date == date(2023, 5, 15)
    assert employee.active is True
```

### Integration Tests

Integration tests verify interactions between components. They typically:
- Use the Flask test client
- Test route endpoints
- Verify database interactions
- Test authentication and permissions

Example integration test for the employee routes:

```python
def test_get_employee(client, auth, test_employee):
    """Test retrieving an employee record."""
    # Login as admin
    auth.login("admin", "password")
    
    # Request employee data
    response = client.get(f"/api/v1/employees/{test_employee.id}")
    data = json.loads(response.data)
    
    # Verify response
    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["data"]["id"] == test_employee.id
    assert data["data"]["first_name"] == test_employee.first_name
    assert data["data"]["last_name"] == test_employee.last_name
```

### UI Tests

UI tests verify the user interface and end-to-end workflows using Selenium:

```python
def test_employee_creation(browser, auth, base_url):
    """Test creating an employee through the UI."""
    # Login
    auth.login_via_browser(browser, "admin", "password")
    
    # Navigate to employee creation page
    browser.get(f"{base_url}/employees/create")
    
    # Fill out the form
    browser.find_element_by_id("first_name").send_keys("John")
    browser.find_element_by_id("last_name").send_keys("Doe")
    browser.find_element_by_id("tier_level").send_keys("2")
    browser.find_element_by_id("hire_date").send_keys("2025-03-01")
    browser.find_element_by_id("submit").click()
    
    # Verify the employee was created
    assert "Employee created successfully" in browser.page_source
    
    # Verify employee appears in the list
    browser.get(f"{base_url}/employees")
    assert "John Doe" in browser.page_source
```

## Test Fixtures

Test fixtures provide reusable test data and objects. They are defined in `conftest.py`:

```python
@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestingConfig)
    
    # Create application context
    with app.app_context():
        # Create database tables
        db.create_all()
        yield app
        # Clean up
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Database session for testing."""
    return db

@pytest.fixture
def test_employee(db):
    """Create a test employee."""
    employee = Employee(
        first_name="Test",
        last_name="Employee",
        phone_number="555-123-4567",
        tier_level=3,
        hire_date=date(2023, 5, 15),
        active=True
    )
    db.session.add(employee)
    db.session.commit()
    return employee
```

## Mocking

The testing framework uses `unittest.mock` for mocking external dependencies:

```python
@patch('app.routes.auth.send_email')
def test_password_reset(mock_send_email, client, test_user):
    """Test password reset functionality."""
    # Configure the mock
    mock_send_email.return_value = True
    
    # Test password reset request
    response = client.post('/auth/reset-password', data={
        'email': test_user.email
    })
    
    # Verify email was "sent"
    assert response.status_code == 200
    mock_send_email.assert_called_once()
    call_args = mock_send_email.call_args[0]
    assert call_args[0] == test_user.email
    assert "Password Reset" in call_args[1]
```

## Continuous Integration

The project uses GitHub Actions for continuous integration, automatically running tests on:
- Every push to the main branch
- Every pull request

The CI workflow is defined in `.github/workflows/test.yml`:

```yaml
name: Run Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        python -m pytest --cov=app
    
    - name: Upload coverage report
      uses: codecov/codecov-action@v1
```

## Code Coverage

The project uses the `coverage` tool to measure test coverage:

```bash
# Run tests with coverage
python -m pytest --cov=app

# Generate HTML coverage report
python -m pytest --cov=app --cov-report=html
```

Coverage reports are generated in the `htmlcov/` directory.

### Coverage Thresholds

The project maintains the following minimum coverage thresholds:
- Overall: 85%
- Models: 90%
- Routes: 85%
- Utils: 80%

Coverage requirements are defined in the `.coveragerc` file:

```ini
[run]
source = app
omit = app/static/*, app/templates/*, app/test/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    pass
    raise ImportError

[html]
directory = htmlcov

[xml]
output = coverage.xml
```

## Test Reports

Test reports are generated automatically for CI/CD pipelines:

```bash
# Generate JUnit XML report
python -m pytest --junitxml=test-results.xml

# Generate HTML report
python -m pytest --html=report.html --self-contained-html
```

### Report Formats

The testing framework supports multiple report formats:
- JUnit XML: For CI/CD integration
- HTML: For human-readable reports
- JSON: For programmatic analysis

### Test Results Dashboard

The CI pipeline automatically publishes test results to a dashboard showing:
- Pass/fail status
- Execution time
- Coverage metrics
- Trends over time

## Test Data Management

### Generating Test Data

The project includes utilities for generating test data:

```python
# Generate test data for development or testing
python -m scripts.generate_test_data --employees 50 --evaluations 200
```

Test data generation options:
- `--employees`: Number of employees to generate
- `--evaluations`: Number of evaluations to generate
- `--seed`: Random seed for reproducibility
- `--output`: Output SQL file (optional)

### Database Fixtures

Database fixtures are managed using pytest fixtures:

```python
@pytest.fixture(scope="function")
def sample_data(db):
    """Create a sample dataset for testing."""
    # Create skill categories
    categories = []
    for i in range(3):
        category = SkillCategory(
            name=f"Test Category {i}",
            display_order=i,
            description=f"Test description {i}"
        )
        db.session.add(category)
        categories.append(category)
    
    # Create skills
    skills = []
    for i, category in enumerate(categories):
        for j in range(3):
            skill = Skill(
                category_id=category.id,
                name=f"Test Skill {i}-{j}",
                description=f"Test description {i}-{j}",
                display_order=j
            )
            db.session.add(skill)
            skills.append(skill)
    
    db.session.commit()
    
    return {
        "categories": categories,
        "skills": skills
    }
```

## Best Practices

### Test Structure

Follow these best practices for test structure:
- Group tests in classes based on functionality
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Keep tests independent
- Minimize test dependencies

Example test class structure:

```python
class TestEmployeeModel:
    """Test cases for the Employee model."""
    
    def test_create_employee(self, db):
        """Test creating a new employee."""
        # Arrange
        employee_data = {...}
        
        # Act
        employee = Employee(**employee_data)
        db.session.add(employee)
        db.session.commit()
        
        # Assert
        assert employee.id is not None
        assert employee.first_name == employee_data['first_name']
```

### Maintainable Tests

Tips for maintainable tests:
- Avoid repetition with fixtures and helper functions
- Keep test scope focused
- Document test purpose and edge cases
- Use parametrized tests for similar test cases
- Keep assertion messages clear and informative

Example of parametrized tests:

```python
@pytest.mark.parametrize("tier_level,is_valid", [
    (1, True),    # Apprentice - valid
    (2, True),    # Handyman - valid
    (3, True),    # Craftsman - valid
    (4, True),    # Master Craftsman - valid
    (5, True),    # Lead Craftsman - valid
    (0, False),   # Below minimum - invalid
    (6, False),   # Above maximum - invalid
])
def test_employee_tier_validation(db, tier_level, is_valid):
    """Test validation of employee tier levels."""
    employee = Employee(
        first_name="Test",
        last_name="Employee",
        tier_level=tier_level,
        hire_date=date(2023, 5, 15)
    )
    
    if is_valid:
        # Should not raise an exception
        db.session.add(employee)
        db.session.commit()
        assert employee.id is not None
    else:
        # Should raise a validation error
        with pytest.raises(ValidationError):
            db.session.add(employee)
            db.session.commit()
```

## Troubleshooting Tests

Common testing issues and solutions:

### Database State Issues

Problem: Tests fail due to unexpected database state.

Solution:
- Use in-memory database for tests
- Reset database between tests
- Use database transactions for isolation

```python
@pytest.fixture(autouse=True)
def transaction(db):
    """Create a database transaction for test isolation."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    yield
    
    transaction.rollback()
    connection.close()
```

### Authentication Issues

Problem: Tests fail due to authentication.

Solution:
- Disable CSRF protection in tests
- Create authentication fixture
- Mock authentication for unit tests

```python
@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def login(self, username="admin", password="password"):
            return client.post(
                "/auth/login",
                data={"username": username, "password": password},
                follow_redirects=True
            )
            
        def logout(self):
            return client.get("/auth/logout", follow_redirects=True)
    
    return AuthActions()
```

### Async and Background Tasks

Problem: Tests fail or hang due to background tasks.

Solution:
- Mock background tasks
- Use synchronous alternatives for testing
- Set timeouts for async operations

```python
@patch('app.tasks.send_notification')
def test_notification_trigger(mock_send_notification, client, auth):
    """Test notification trigger."""
    # Configure the mock
    mock_send_notification.return_value = True
    
    # Test functionality
    auth.login()
    response = client.post('/evaluations/1/submit')
    
    # Verify notification was triggered
    assert response.status_code == 302
    mock_send_notification.assert_called_once()
```

## Appendix: Testing Checklist

Use this checklist for implementing new features:

- [ ] Unit tests for all models
- [ ] Integration tests for all routes
- [ ] UI tests for critical user journeys
- [ ] Test both success and failure cases
- [ ] Verify permissions and access control
- [ ] Test validation logic
- [ ] Ensure minimum code coverage
- [ ] Document test cases
- [ ] Run performance tests for database operations
- [ ] Verify error handling
