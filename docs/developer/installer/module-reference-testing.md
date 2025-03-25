## Testing Modules

### `installer.run_tests`

**Purpose**: Provides a test runner for executing installer tests.

**Functions**:
- `discover_tests(test_dir)`: Discovers test modules in directory
- `run_tests(test_list=None)`: Runs specified tests or all tests
- `generate_report(results)`: Generates test report
- `main()`: Main entry point for test runner

**Example Usage**:
```python
# Run all tests
python -m installer.run_tests

# Run specific test category
python -m installer.run_tests --category database

# Run with increased verbosity
python -m installer.run_tests --verbose
```

### `installer.test_database_adapters`

**Purpose**: Tests database adapter functionality.

**Test Classes**:
- `SQLiteAdapterTest`: Tests for SQLite adapter
- `MySQLAdapterTest`: Tests for MySQL adapter
- `PostgresAdapterTest`: Tests for PostgreSQL adapter
- `MSSQLAdapterTest`: Tests for SQL Server adapter

**Example Usage**:
```python
# Run all database adapter tests
python -m unittest installer.test_database_adapters

# Run specific adapter tests
python -m unittest installer.test_database_adapters.SQLiteAdapterTest
```

### `installer.test_database_integration`

**Purpose**: Tests database integration with the installer.

**Test Classes**:
- `DatabaseIntegrationTest`: Tests database setup during installation
- `MigrationTest`: Tests database migration functionality
- `SchemaTest`: Tests database schema creation

**Example Usage**:
```python
# Run all database integration tests
python -m unittest installer.test_database_integration

# Run specific integration tests
python -m unittest installer.test_database_integration.MigrationTest
```

### `installer.test_windows_builder`

**Purpose**: Tests Windows installer builder functionality.

**Test Classes**:
- `WindowsBuilderTest`: Tests for Windows builder
- `InnoSetupTest`: Tests for Inno Setup integration

**Example Usage**:
```python
# Run all Windows builder tests
python -m unittest installer.test_windows_builder

# Run with mocked Inno Setup compiler
python -m unittest installer.test_windows_builder --mock-compiler
```

### `installer.test_windows_gui`

**Purpose**: Tests Windows GUI functionality.

**Test Classes**:
- `SetupWizardTest`: Tests setup wizard navigation
- `WizardPageTest`: Tests individual wizard pages
- `InputValidationTest`: Tests GUI input validation

**Example Usage**:
```python
# Run all Windows GUI tests
python -m unittest installer.test_windows_gui

# Run with headless mode (no actual GUI shown)
python -m unittest installer.test_windows_gui --headless
```

### `installer.test_windows_gui_integration`

**Purpose**: Tests integration between Windows GUI and other components.

**Test Classes**:
- `GUIConfigIntegrationTest`: Tests GUI with configuration manager
- `GUIDatabaseIntegrationTest`: Tests GUI with database adapters

**Example Usage**:
```python
# Run all Windows GUI integration tests
python -m unittest installer.test_windows_gui_integration
```

### `installer.test_windows_gui_part2`

**Purpose**: Additional tests for Windows GUI components.

**Test Classes**:
- `InputValidationTest`: Tests input validation in wizard
- `ErrorHandlingTest`: Tests error handling in GUI
- `NavigationTest`: Tests wizard navigation behavior

**Example Usage**:
```python
# Run specific GUI test category
python -m unittest installer.test_windows_gui_part2.ErrorHandlingTest
```

### `installer.test_windows_gui_part3`

**Purpose**: Extended testing for Windows GUI components.

**Test Classes**:
- `CustomizationTest`: Tests GUI customization options
- `AccessibilityTest`: Tests GUI accessibility features
- `PerformanceTest`: Tests GUI performance

**Example Usage**:
```python
# Run all extended GUI tests
python -m unittest installer.test_windows_gui_part3
```

### `installer.test_inno_setup_integration`

**Purpose**: Tests integration with Inno Setup for Windows installer creation.

**Test Classes**:
- `TemplateProcessingTest`: Tests Inno Setup template processing
- `CompilerIntegrationTest`: Tests Inno Setup compiler integration
- `InstallerBuildTest`: Tests complete installer build process

**Example Usage**:
```python
# Run all Inno Setup integration tests
python -m unittest installer.test_inno_setup_integration

# Run specific test class
python -m unittest installer.test_inno_setup_integration.TemplateProcessingTest
```

## Mock Objects and Test Helpers

### `installer.test.mocks.database_mock`

**Purpose**: Provides mock database objects for testing.

**Classes**:
- `MockDatabaseConnection`: Mock database connection
- `MockCursor`: Mock database cursor
- `MockDatabaseAdapter`: Mock database adapter

**Example Usage**:
```python
from installer.test.mocks.database_mock import MockDatabaseAdapter

# Create mock adapter for testing
mock_adapter = MockDatabaseAdapter(config={"type": "sqlite"})

# Use mock adapter in tests
result = mock_adapter.test_connection()
assert result.success == True

# Simulate failure
mock_adapter.should_fail = True
result = mock_adapter.test_connection()
assert result.success == False
```

### `installer.test.mocks.gui_mock`

**Purpose**: Provides mock GUI objects for headless testing.

**Classes**:
- `MockWizard`: Mock setup wizard
- `MockWizardPage`: Mock wizard page
- `MockGUIElements`: Mock GUI elements (buttons, textboxes, etc.)

**Example Usage**:
```python
from installer.test.mocks.gui_mock import MockWizard, MockWizardPage

# Create mock wizard for testing
wizard = MockWizard()
welcome_page = MockWizardPage("welcome")
license_page = MockWizardPage("license")
wizard.add_page(welcome_page)
wizard.add_page(license_page)

# Test navigation
wizard.current_page = welcome_page
wizard.next_page()
assert wizard.current_page == license_page
```

### `installer.test.mocks.inno_setup_mock`

**Purpose**: Provides mock Inno Setup compiler for testing.

**Classes**:
- `MockInnoCompiler`: Mock Inno Setup compiler
- `MockCompilerResult`: Mock compiler result

**Example Usage**:
```python
from installer.test.mocks.inno_setup_mock import MockInnoCompiler

# Create mock compiler for testing
compiler = MockInnoCompiler()

# Test successful compilation
result = compiler.compile("setup.iss")
assert result.success == True
assert result.output_file == "Output/setup.exe"

# Test compilation failure
compiler.should_fail = True
result = compiler.compile("setup.iss")
assert result.success == False
assert "Failed to compile" in result.error
```

### `installer.test.fixtures.test_data`

**Purpose**: Provides test data fixtures for consistent testing.

**Functions**:
- `get_test_config()`: Gets test configuration data
- `get_test_database_config()`: Gets test database configuration
- `get_test_user_input()`: Gets simulated user input data

**Example Usage**:
```python
from installer.test.fixtures.test_data import get_test_config, get_test_database_config

# Get standard test configuration
config = get_test_config()

# Get database-specific test configuration
db_config = get_test_database_config("sqlite")
```

### `installer.test.fixtures.file_fixtures`

**Purpose**: Provides file-related test fixtures.

**Functions**:
- `create_temp_file(content)`: Creates temporary file with content
- `create_temp_dir()`: Creates temporary directory
- `get_test_archive()`: Gets test archive file
- `cleanup_temp_files()`: Cleans up temporary test files

**Example Usage**:
```python
from installer.test.fixtures.file_fixtures import create_temp_file, cleanup_temp_files

# Create temporary file for testing
temp_config = create_temp_file('{"version": "1.0.0", "app_name": "Test App"}')
try:
    # Test with temporary file
    config_manager = ConfigManager(temp_config)
    assert config_manager.get("version") == "1.0.0"
finally:
    # Clean up
    cleanup_temp_files()
```
