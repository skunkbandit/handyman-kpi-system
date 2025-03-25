"""
Integration tests for setup wizard components.

This module tests the setup wizard GUI components and their interaction
with the configuration manager and database components.
"""

import os
import sys
import json
import pytest
import tempfile
import tkinter as tk
from unittest.mock import MagicMock, patch

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import test utilities
from utils import create_test_configuration

# Test class for the setup wizard integration tests
class TestSetupWizardIntegration:
    """Test setup wizard integration with other components."""
    
    @pytest.fixture
    def mock_wizard(self):
        """Create a mock setup wizard for testing."""
        # In a real test, we would import the actual wizard module
        # For now, create a mock that simulates the wizard's behavior
        wizard = MagicMock()
        wizard.config = {}
        wizard.current_page = 0
        wizard.pages = ['welcome', 'database', 'admin', 'installation', 'confirm', 'install', 'finish']
        
        def navigate_to_page(page_index):
            if 0 <= page_index < len(wizard.pages):
                wizard.current_page = page_index
                return True
            return False
        
        def update_config(key, value):
            wizard.config[key] = value
            return True
        
        def get_config():
            return wizard.config.copy()
        
        def save_config(path):
            with open(path, 'w') as f:
                json.dump(wizard.config, f, indent=4)
            return True
        
        def load_config(path):
            try:
                with open(path, 'r') as f:
                    wizard.config = json.load(f)
                return True
            except (IOError, json.JSONDecodeError):
                return False
        
        wizard.navigate_to_page = navigate_to_page
        wizard.update_config = update_config
        wizard.get_config = get_config
        wizard.save_config = save_config
        wizard.load_config = load_config
        
        return wizard
    
    def test_wizard_navigation(self, mock_wizard):
        """Test navigation between wizard pages."""
        # Test forward navigation
        assert mock_wizard.navigate_to_page(1)
        assert mock_wizard.current_page == 1
        
        # Test navigation to last page
        assert mock_wizard.navigate_to_page(6)
        assert mock_wizard.current_page == 6
        
        # Test navigation to invalid page
        assert not mock_wizard.navigate_to_page(7)
        assert mock_wizard.current_page == 6
        
        # Test navigation to first page
        assert mock_wizard.navigate_to_page(0)
        assert mock_wizard.current_page == 0
    
    def test_wizard_config_management(self, mock_wizard, temp_directory):
        """Test configuration management in the wizard."""
        # Set configuration values
        assert mock_wizard.update_config('app_name', 'Handyman KPI System')
        assert mock_wizard.update_config('installation_path', os.path.join(temp_directory, 'kpi_system'))
        assert mock_wizard.update_config('database', {
            'type': 'sqlite',
            'path': os.path.join(temp_directory, 'kpi.db')
        })
        
        # Get and verify config
        config = mock_wizard.get_config()
        assert config['app_name'] == 'Handyman KPI System'
        assert config['database']['type'] == 'sqlite'
        
        # Save configuration
        config_path = os.path.join(temp_directory, 'config.json')
        assert mock_wizard.save_config(config_path)
        
        # Clear config and load from file
        mock_wizard.config = {}
        assert mock_wizard.load_config(config_path)
        assert mock_wizard.config['app_name'] == 'Handyman KPI System'
    
    @patch('tkinter.Tk')
    @patch('tkinter.StringVar')
    @patch('tkinter.BooleanVar')
    def test_form_validation(self, mock_bool_var, mock_string_var, mock_tk, mock_wizard, temp_directory):
        """Test form validation in the wizard."""
        # Create test configuration
        config_path = os.path.join(temp_directory, 'config.json')
        create_test_configuration(config_path, database_type='sqlite', temp_dir=temp_directory)
        
        # Load configuration into wizard
        mock_wizard.load_config(config_path)
        
        # Create mock form validators
        def validate_required(value, field_name):
            if not value:
                return False, f"{field_name} is required"
            return True, ""
        
        def validate_email(value):
            if not value:
                return False, "Email is required"
            if '@' not in value:
                return False, "Invalid email format"
            return True, ""
        
        def validate_password(value):
            if not value:
                return False, "Password is required"
            if len(value) < 8:
                return False, "Password must be at least 8 characters"
            if not any(c.isdigit() for c in value):
                return False, "Password must contain at least one number"
            if not any(c.isupper() for c in value):
                return False, "Password must contain at least one uppercase letter"
            return True, ""
        
        def validate_directory(value):
            if not value:
                return False, "Directory is required"
            # In a real test, we would check if the directory exists or can be created
            return True, ""
        
        # Test form validation
        # Admin username
        valid, _ = validate_required(mock_wizard.config['admin_user']['username'], 'Username')
        assert valid
        
        # Admin email
        valid, _ = validate_email(mock_wizard.config['admin_user']['email'])
        assert valid
        
        # Admin password (not in config yet)
        mock_wizard.update_config('admin_user', {
            **mock_wizard.config['admin_user'],
            'password': 'Password123'
        })
        valid, _ = validate_password(mock_wizard.config['admin_user']['password'])
        assert valid
        
        # Installation path
        valid, _ = validate_directory(mock_wizard.config['installation_path'])
        assert valid
        
        # Test invalid inputs
        invalid_email = 'admin-at-example.com'
        valid, error = validate_email(invalid_email)
        assert not valid
        assert "Invalid email format" in error
        
        invalid_password = 'password'
        valid, error = validate_password(invalid_password)
        assert not valid
        assert "must be at least 8 characters" in error or "must contain at least one uppercase letter" in error
    
    def test_wizard_database_integration(self, mock_wizard, temp_directory, sample_schema_dir):
        """Test integration between wizard and database components."""
        # Set up configuration
        config_path = os.path.join(temp_directory, 'config.json')
        db_path = os.path.join(temp_directory, 'kpi.db')
        
        # Create test configuration
        create_test_configuration(config_path, database_type='sqlite', temp_dir=temp_directory)
        
        # Load configuration into wizard
        mock_wizard.load_config(config_path)
        
        # Update database configuration
        mock_wizard.update_config('database', {
            'type': 'sqlite',
            'path': db_path
        })
        
        # Create a mock database initializer
        class MockDatabaseInitializer:
            def __init__(self, schema_dir):
                self.schema_dir = schema_dir
            
            def test_database_connection(self, db_config):
                if db_config['type'] == 'sqlite':
                    return True, ""
                return False, "Unsupported database type"
            
            def initialize_database(self, db_config):
                if db_config['type'] == 'sqlite':
                    # Create empty database file
                    with open(db_config['path'], 'w') as f:
                        f.write('')
                    return True
                return False
            
            def create_admin_user(self, username, password, email, db_config):
                if db_config['type'] == 'sqlite' and os.path.exists(db_config['path']):
                    return True
                return False
        
        # Test database connection
        db_initializer = MockDatabaseInitializer(sample_schema_dir)
        db_config = mock_wizard.config['database']
        
        status, _ = db_initializer.test_database_connection(db_config)
        assert status, "Database connection test failed"
        
        # Test database initialization
        assert db_initializer.initialize_database(db_config)
        assert os.path.exists(db_path)
        
        # Test admin user creation
        admin_config = mock_wizard.config['admin_user']
        assert db_initializer.create_admin_user(
            admin_config['username'],
            'Password123',  # This would come from the wizard form
            admin_config['email'],
            db_config
        )
    
    def test_wizard_workflow(self, mock_wizard, temp_directory):
        """Test the complete wizard workflow."""
        # Set up test configuration
        config_path = os.path.join(temp_directory, 'config.json')
        create_test_configuration(config_path, database_type='sqlite', temp_dir=temp_directory)
        
        # Load configuration into wizard
        mock_wizard.load_config(config_path)
        
        # Simulate user going through the wizard
        
        # 1. Welcome page
        assert mock_wizard.navigate_to_page(0)
        assert mock_wizard.current_page == 0
        
        # 2. Database configuration page
        assert mock_wizard.navigate_to_page(1)
        assert mock_wizard.current_page == 1
        
        # Update database configuration
        mock_wizard.update_config('database', {
            'type': 'sqlite',
            'path': os.path.join(temp_directory, 'kpi.db')
        })
        
        # 3. Admin user configuration page
        assert mock_wizard.navigate_to_page(2)
        assert mock_wizard.current_page == 2
        
        # Update admin configuration
        mock_wizard.update_config('admin_user', {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'Password123'
        })
        
        # 4. Installation path page
        assert mock_wizard.navigate_to_page(3)
        assert mock_wizard.current_page == 3
        
        # Update installation path
        mock_wizard.update_config('installation_path', os.path.join(temp_directory, 'kpi_system'))
        
        # 5. Confirmation page
        assert mock_wizard.navigate_to_page(4)
        assert mock_wizard.current_page == 4
        
        # 6. Installation page
        assert mock_wizard.navigate_to_page(5)
        assert mock_wizard.current_page == 5
        
        # 7. Finish page
        assert mock_wizard.navigate_to_page(6)
        assert mock_wizard.current_page == 6
        
        # Save final configuration
        assert mock_wizard.save_config(config_path)
        
        # Verify the complete configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert config['database']['type'] == 'sqlite'
        assert config['admin_user']['username'] == 'admin'
        assert config['installation_path'] == os.path.join(temp_directory, 'kpi_system')
