"""
Test script for the Windows GUI components of the KPI System Installer.

This script tests the setup wizard functionality, input validation,
and integration with other installer components.
"""

import os
import sys
import unittest
import tkinter as tk
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the installer directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import installer components
from installer.platforms.windows.gui.setup_wizard_integrated import SetupWizard
from installer.core.config import ConfigManager
from installer.core.database import DatabaseManager
from installer.shared.utils.logging_utils import get_logger
from installer.shared.utils.error_utils import InstallerError

logger = get_logger(__name__)


class TestWindowsSetupWizard(unittest.TestCase):
    """Test case for the Windows Setup Wizard."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock the tkinter root window
        self.root = MagicMock(spec=tk.Tk)
        
        # Mock configuration manager
        self.config_manager = MagicMock(spec=ConfigManager)
        self.config_manager.get_config.return_value = {
            'general': {
                'installation_path': 'C:\\HandymanKPI',
                'create_shortcuts': True,
                'start_on_boot': True
            },
            'database': {
                'type': 'sqlite',
                'path': 'C:\\HandymanKPI\\data\\kpi.db'
            },
            'admin': {
                'username': 'admin',
                'email': 'admin@example.com'
            }
        }
        
        # Mock database manager
        self.db_manager = MagicMock(spec=DatabaseManager)
        self.db_manager.test_connection.return_value = (True, "Connection successful")
        
        # Create wizard instance with mocks
        self.wizard = SetupWizard(self.root, self.config_manager, self.db_manager)
    
    def test_wizard_initialization(self):
        """Test that the wizard initializes properly."""
        self.assertIsNotNone(self.wizard)
        self.assertEqual(self.wizard.current_page, 0)
        self.assertIsNotNone(self.wizard.pages)
        self.assertGreater(len(self.wizard.pages), 0)
    
    def test_navigation(self):
        """Test wizard navigation methods."""
        # Mock the validate_page method to always return True
        self.wizard.validate_page = MagicMock(return_value=True)
        
        # Test next_page
        initial_page = self.wizard.current_page
        self.wizard.next_page()
        self.assertEqual(self.wizard.current_page, initial_page + 1)
        
        # Test previous_page
        self.wizard.previous_page()
        self.assertEqual(self.wizard.current_page, initial_page)
        
        # Test go_to_page
        target_page = 2
        self.wizard.go_to_page(target_page)
        self.assertEqual(self.wizard.current_page, target_page)
    
    def test_validation_installation_path(self):
        """Test validation of installation path."""
        # Setup mock for the installation page
        self.wizard.pages[0] = MagicMock()
        self.wizard.pages[0].get_data.return_value = {
            'installation_path': 'C:\\InvalidPath\\with\\invalid\\characters\\<>:"|?*'
        }
        
        # Test with invalid path
        self.wizard.current_page = 0
        result = self.wizard.validate_page()
        self.assertFalse(result)
        
        # Test with valid path
        self.wizard.pages[0].get_data.return_value = {
            'installation_path': 'C:\\ValidPath'
        }
        result = self.wizard.validate_page()
        self.assertTrue(result)
    
    def test_validation_database_config(self):
        """Test validation of database configuration."""
        # Setup mock for the database page
        self.wizard.pages[1] = MagicMock()
        
        # Test with SQLite
        self.wizard.pages[1].get_data.return_value = {
            'db_type': 'sqlite',
            'db_path': 'C:\\ValidPath\\database.db'
        }
        self.wizard.current_page = 1
        result = self.wizard.validate_page()
        self.assertTrue(result)
        
        # Test with MySQL - invalid configuration
        self.wizard.pages[1].get_data.return_value = {
            'db_type': 'mysql',
            'db_host': '',  # Empty host - invalid
            'db_port': '3306',
            'db_name': 'kpi_db',
            'db_user': 'kpi_user',
            'db_password': 'password'
        }
        result = self.wizard.validate_page()
        self.assertFalse(result)
        
        # Test with MySQL - valid configuration
        self.wizard.pages[1].get_data.return_value = {
            'db_type': 'mysql',
            'db_host': 'localhost',
            'db_port': '3306',
            'db_name': 'kpi_db',
            'db_user': 'kpi_user',
            'db_password': 'password'
        }
        
        # Mock connection test
        self.db_manager.test_connection.return_value = (True, "Connection successful")
        result = self.wizard.validate_page()
        self.assertTrue(result)
        
        # Test with MySQL - connection failure
        self.db_manager.test_connection.return_value = (False, "Connection failed")
        result = self.wizard.validate_page()
        self.assertFalse(result)
    
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


class TestSetupWizardIntegration(unittest.TestCase):
    """Integration tests for the Setup Wizard with real components."""
    
    @patch('tkinter.Tk')
    def test_wizard_with_real_config_manager(self, mock_tk):
        """Test wizard with actual ConfigManager."""
        # Create a temporary directory for config files
        import tempfile
        config_dir = tempfile.mkdtemp()
        config_file = os.path.join(config_dir, 'config.ini')
        
        try:
            # Create a real config manager
            from installer.core.config import ConfigManager
            config_manager = ConfigManager(config_file)
            
            # Create wizard with mocked Tk and real config manager
            db_manager = MagicMock(spec=DatabaseManager)
            wizard = SetupWizard(mock_tk, config_manager, db_manager)
            
            # Verify that the wizard initializes properly
            self.assertIsNotNone(wizard)
            
            # Simulate completing the installation
            wizard.get_all_data = MagicMock(return_value={
                'installation_path': config_dir,
                'create_shortcuts': True,
                'start_on_boot': True,
                'db_type': 'sqlite',
                'db_path': os.path.join(config_dir, 'kpi.db'),
                'admin_username': 'admin',
                'admin_password': 'Password123!',
                'admin_email': 'admin@example.com'
            })
            
            # Save configuration
            wizard.save_configuration()
            
            # Verify that the configuration file was created
            self.assertTrue(os.path.exists(config_file))
            
            # Verify that we can load the configuration
            loaded_config = config_manager.get_config()
            self.assertEqual(loaded_config['general']['installation_path'], config_dir)
            self.assertEqual(loaded_config['database']['type'], 'sqlite')
            
        finally:
            # Clean up temporary directory
            import shutil
            shutil.rmtree(config_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
