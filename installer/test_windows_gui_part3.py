"""Test script for the Windows GUI components of the KPI System Installer (Part 3).

Additional test cases for admin account validation and configuration.
"""

import os
import sys
import unittest
import tempfile
import shutil
import tkinter as tk
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the installer directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import installer components
from installer.platforms.windows.gui.setup_wizard_integrated import SetupWizard
from installer.core.config import ConfigManager
from installer.core.database import DatabaseManager
from installer.shared.utils.error_utils import InstallerError


class TestWindowsSetupWizardAdminAndConfig(unittest.TestCase):
    """Test case for admin validation and configuration handling in the Windows Setup Wizard."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock the tkinter root window
        self.root = MagicMock(spec=tk.Tk)
        
        # Mock configuration manager
        self.config_manager = MagicMock(spec=ConfigManager)
        
        # Mock database manager
        self.db_manager = MagicMock(spec=DatabaseManager)
        
        # Create wizard instance with mocks
        self.wizard = SetupWizard(self.root, self.config_manager, self.db_manager)
    
    def test_validation_admin_account(self):
        """Test validation of admin account configuration."""
        # Setup mock for the admin page
        self.wizard.pages[2] = MagicMock()
        
        # Test with valid admin data
        self.wizard.pages[2].get_data.return_value = {
            'admin_username': 'admin',
            'admin_password': 'Password123!',
            'admin_password_confirm': 'Password123!',
            'admin_email': 'admin@example.com'
        }
        self.wizard.current_page = 2
        result = self.wizard.validate_page()
        self.assertTrue(result)
        
        # Test with short password
        self.wizard.pages[2].get_data.return_value = {
            'admin_username': 'admin',
            'admin_password': 'pass',  # Too short
            'admin_password_confirm': 'pass',
            'admin_email': 'admin@example.com'
        }
        result = self.wizard.validate_page()
        self.assertFalse(result)
        
        # Test with non-matching passwords
        self.wizard.pages[2].get_data.return_value = {
            'admin_username': 'admin',
            'admin_password': 'Password123!',
            'admin_password_confirm': 'DifferentPassword!',
            'admin_email': 'admin@example.com'
        }
        result = self.wizard.validate_page()
        self.assertFalse(result)
        
        # Test with invalid email
        self.wizard.pages[2].get_data.return_value = {
            'admin_username': 'admin',
            'admin_password': 'Password123!',
            'admin_password_confirm': 'Password123!',
            'admin_email': 'invalid-email'  # Invalid email format
        }
        result = self.wizard.validate_page()
        self.assertFalse(result)
    
    def test_save_configuration(self):
        """Test that configuration is saved correctly."""
        # Setup wizard with mock data
        self.wizard.get_all_data = MagicMock(return_value={
            'installation_path': 'C:\\HandymanKPI',
            'create_shortcuts': True,
            'start_on_boot': True,
            'db_type': 'sqlite',
            'db_path': 'C:\\HandymanKPI\\data\\kpi.db',
            'admin_username': 'admin',
            'admin_password': 'Password123!',
            'admin_email': 'admin@example.com'
        })
        
        # Call save_configuration
        self.wizard.save_configuration()
        
        # Verify that the configuration was saved
        self.config_manager.set_config.assert_called_once()
        
        # Verify the configuration structure
        config = self.config_manager.set_config.call_args[0][0]
        self.assertIn('general', config)
        self.assertIn('database', config)
        self.assertIn('admin', config)
        
        # Verify specific configuration values
        self.assertEqual(config['general']['installation_path'], 'C:\\HandymanKPI')
        self.assertEqual(config['database']['type'], 'sqlite')
        self.assertEqual(config['admin']['username'], 'admin')
    
    def test_error_handling(self):
        """Test error handling in the wizard."""
        # Mock an error in database connection test
        self.db_manager.test_connection.side_effect = InstallerError("Database connection error")
        
        # Setup mock for the database page
        self.wizard.pages[1] = MagicMock()
        self.wizard.pages[1].get_data.return_value = {
            'db_type': 'mysql',
            'db_host': 'localhost',
            'db_port': '3306',
            'db_name': 'kpi_db',
            'db_user': 'kpi_user',
            'db_password': 'password'
        }
        
        # Set current page to database page
        self.wizard.current_page = 1
        
        # Test that the error is handled (should not raise an exception)
        result = self.wizard.validate_page()
        self.assertFalse(result)
        
        # Mock the show_error method to check if it's called
        self.wizard.show_error = MagicMock()
        result = self.wizard.validate_page()
        self.wizard.show_error.assert_called_once()
    
    def test_long_running_operations(self):
        """Test handling of long-running operations."""
        # Mock a long-running database operation
        def slow_test_connection(*args, **kwargs):
            import time
            time.sleep(0.1)  # Short sleep for test purposes
            return True, "Connection successful"
            
        self.db_manager.test_connection.side_effect = slow_test_connection
        
        # Set up the progress dialog mock
        self.wizard.show_progress_dialog = MagicMock()
        self.wizard.close_progress_dialog = MagicMock()
        
        # Setup mock for the database page
        self.wizard.pages[1] = MagicMock()
        self.wizard.pages[1].get_data.return_value = {
            'db_type': 'mysql',
            'db_host': 'localhost',
            'db_port': '3306',
            'db_name': 'kpi_db',
            'db_user': 'kpi_user',
            'db_password': 'password'
        }
        
        # Set current page to database page
        self.wizard.current_page = 1
        
        # Validate page (should show and close progress dialog)
        result = self.wizard.validate_page()
        self.assertTrue(result)
        self.wizard.show_progress_dialog.assert_called_once()
        self.wizard.close_progress_dialog.assert_called_once()