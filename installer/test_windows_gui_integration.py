"""Integration tests for the Windows GUI components of the KPI System Installer.

This script tests the setup wizard with real components.
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


class TestSetupWizardIntegration(unittest.TestCase):
    """Integration tests for the Setup Wizard with real components."""
    
    @patch('tkinter.Tk')
    def test_wizard_with_real_config_manager(self, mock_tk):
        """Test wizard with actual ConfigManager."""
        # Create a temporary directory for config files
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
            shutil.rmtree(config_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()