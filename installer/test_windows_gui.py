"""Test script for the Windows GUI components of the KPI System Installer.

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