"""Test script for the Windows GUI components of the KPI System Installer (Part 2).

Additional test cases for various validations and features.
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
from installer.shared.utils.error_utils import InstallerError


class TestWindowsSetupWizardValidation(unittest.TestCase):
    """Test case for the validation methods of the Windows Setup Wizard."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock the tkinter root window
        self.root = MagicMock(spec=tk.Tk)
        
        # Mock configuration manager
        self.config_manager = MagicMock(spec=ConfigManager)
        
        # Mock database manager
        self.db_manager = MagicMock(spec=DatabaseManager)
        self.db_manager.test_connection.return_value = (True, "Connection successful")
        
        # Create wizard instance with mocks
        self.wizard = SetupWizard(self.root, self.config_manager, self.db_manager)
    
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