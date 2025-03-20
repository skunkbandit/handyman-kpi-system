# Handyman KPI System Tests

## Overview
This directory contains test scripts for verifying the functionality of the Handyman KPI System. The tests cover various aspects of the application including models, routes, and overall application functionality.

## Test Structure

- **test_models.py**: Tests for database models and their relationships
- **test_app_functionality.py**: Tests for application initialization and core functionality

## Running Tests

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)
- Required packages installed (Flask, SQLAlchemy, etc.)

### Setup Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Running All Tests
To run all tests, use the pytest command from the project root directory:

```bash
python -m pytest tests/
```

### Running Specific Tests
To run a specific test file:

```bash
python -m pytest tests/test_models.py
```

To run a specific test case:

```bash
python -m pytest tests/test_models.py::ModelTestCase::test_user_model
```

### Using the Test Runner
You can also use the included test runner script which provides more options and better reporting:

```bash
python run_tests.py
```

Options for the test runner:

```bash
python run_tests.py --unit      # Run only unit tests
python run_tests.py --integration # Run only integration tests
python run_tests.py --coverage   # Run tests with coverage reporting
```

## Manual Verification

In addition to automated tests, you can manually verify the application functionality using the following scripts:

- **test_app_functionality.py**: Verifies basic application initialization and configuration
- **simplified_db_test.py**: Tests database connections and model relationships
- **model_consistency_check.py**: Checks for inconsistencies in model relationships

To run these scripts directly:

```bash
python test_app_functionality.py
python simplified_db_test.py
python model_consistency_check.py
```

## Adding New Tests

When adding new tests, follow these guidelines:

1. Create a new test file following the naming convention `test_*.py`
2. Use the unittest framework or pytest fixtures
3. Include setup and teardown methods to ensure test isolation
4. Document the purpose of the test file at the top
5. Use descriptive test method names that explain what is being tested

## Troubleshooting

If you encounter issues with the tests:

1. Ensure your virtual environment is activated
2. Verify that all required packages are installed
3. Check that the application code is in the expected directory structure
4. Look for Python path issues if imports are failing
5. Try running with increased verbosity: `python -m pytest -v tests/`
