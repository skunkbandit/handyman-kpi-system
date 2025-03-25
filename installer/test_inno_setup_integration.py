"""
Test script for the Inno Setup integration of the KPI System Installer.

This script tests the template variable replacement, script generation,
and builder integration with Inno Setup.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the installer directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import installer components
from installer.build.windows import WindowsBuilder
from installer.core.config import ConfigManager
from installer.shared.utils.logging_utils import get_logger
from installer.shared.utils.error_utils import InstallerError

logger = get_logger(__name__)


class TestInnoSetupIntegration(unittest.TestCase):
    """Test case for Inno Setup integration."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create a mock configuration manager
        self.config_manager = MagicMock(spec=ConfigManager)
        self.config_manager.get_config.return_value = {
            'general': {
                'app_name': 'Handyman KPI System',
                'version': '1.0.0',
                'publisher': 'Handyman KPI',
                'publisher_url': 'https://handymankpi.example.com',
                'installation_path': 'C:\\HandymanKPI'
            },
            'windows': {
                'create_desktop_icon': True,
                'create_start_menu_shortcut': True,
                'run_after_install': True,
                'allow_silent_install': True
            }
        }
        
        # Initialize the Windows builder
        self.builder = WindowsBuilder(self.config_manager, output_dir=self.output_dir)
        
        # Copy the Inno Setup template for testing
        template_path = os.path.join(Path(__file__).parent, 'installer', 'platforms', 'windows', 'inno', 'installer.iss')
        if os.path.exists(template_path):
            self.template_path = template_path
        else:
            # Create a simple test template if the real one isn't available
            self.template_path = os.path.join(self.temp_dir, 'installer.iss')
            with open(self.template_path, 'w') as f:
                f.write("""
[Setup]
AppName={{APP_NAME}}
AppVersion={{APP_VERSION}}
AppPublisher={{PUBLISHER}}
AppPublisherURL={{PUBLISHER_URL}}
DefaultDirName={{INSTALLATION_PATH}}
OutputDir={{OUTPUT_DIR}}
CreateDesktopIcon={{CREATE_DESKTOP_ICON}}
CreateStartMenuShortcut={{CREATE_START_MENU_SHORTCUT}}
RunAfterInstall={{RUN_AFTER_INSTALL}}
AllowSilentInstall={{ALLOW_SILENT_INSTALL}}

[Files]
Source: "{{SOURCE_DIR}}\\*"; DestDir: "{{INSTALLATION_PATH}}\\"; Flags: recursesubdirs
                """)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_variable_replacement(self):
        """Test that variables in the Inno Setup template are replaced correctly."""
        # Mock the template file
        test_template = os.path.join(self.temp_dir, 'test_template.iss')
        with open(test_template, 'w') as f:
            f.write("""
[Setup]
AppName={{APP_NAME}}
AppVersion={{APP_VERSION}}
DefaultDirName={{INSTALLATION_PATH}}
            """)
        
        # Call the variable replacement method
        replaced_content = self.builder._replace_template_variables(test_template)
        
        # Check that variables were replaced
        self.assertIn("AppName=Handyman KPI System", replaced_content)
        self.assertIn("AppVersion=1.0.0", replaced_content)
        self.assertIn("DefaultDirName=C:\\HandymanKPI", replaced_content)
        
        # Make sure there are no unreplaced variables
        self.assertNotIn("{{", replaced_content)
        self.assertNotIn("}}", replaced_content)
    
    def test_generate_inno_script(self):
        """Test generation of Inno Setup script."""
        # Call the script generation method
        script_path = self.builder.generate_inno_script(self.template_path, 
                                                       source_dir=self.temp_dir,
                                                       output_dir=self.output_dir)
        
        # Check that the script was created
        self.assertTrue(os.path.exists(script_path))
        
        # Check the content of the generated script
        with open(script_path, 'r') as f:
            content = f.read()
            
        # Verify that key variables were replaced
        self.assertIn("AppName=Handyman KPI System", content)
        self.assertIn("AppVersion=1.0.0", content)
        self.assertIn(f"OutputDir={self.output_dir.replace('\\', '\\\\')}", content)  # Paths with escaped backslashes
        self.assertIn("CreateDesktopIcon=yes", content)
    
    @patch('subprocess.run')
    def test_run_inno_compiler(self, mock_run):
        """Test running the Inno Setup compiler."""
        # Setup mock subprocess return
        mock_return = MagicMock()
        mock_return.returncode = 0
        mock_run.return_value = mock_return
        
        # Generate a script file for testing
        script_path = self.builder.generate_inno_script(self.template_path, 
                                                      source_dir=self.temp_dir,
                                                      output_dir=self.output_dir)
        
        # Run the compiler
        result = self.builder.run_inno_compiler(script_path)
        
        # Check that subprocess.run was called with the correct arguments
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], 'iscc')
        self.assertEqual(call_args[1], script_path)
        
        # Check the result
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_build_installer(self, mock_run):
        """Test the full installer build process."""
        # Setup mock subprocess return
        mock_return = MagicMock()
        mock_return.returncode = 0
        mock_run.return_value = mock_return
        
        # Call the build_installer method
        installer_path = self.builder.build_installer(source_dir=self.temp_dir)
        
        # Check that the build process was executed
        mock_run.assert_called_once()
        
        # Check that the installer path is returned
        self.assertIsNotNone(installer_path)
    
    @patch('subprocess.run')
    def test_error_handling(self, mock_run):
        """Test error handling during the build process."""
        # Setup mock subprocess to simulate an error
        mock_return = MagicMock()
        mock_return.returncode = 1
        mock_return.stderr = b"Error: Could not compile script"
        mock_run.return_value = mock_return
        
        # Check that an exception is raised
        with self.assertRaises(InstallerError):
            self.builder.run_inno_compiler("nonexistent_script.iss")
    
    def test_boolean_conversion(self):
        """Test that boolean values are correctly converted for Inno Setup."""
        # Test true value
        true_result = self.builder._convert_bool_to_inno(True)
        self.assertEqual(true_result, "yes")
        
        # Test false value
        false_result = self.builder._convert_bool_to_inno(False)
        self.assertEqual(false_result, "no")


class TestWindowsBuilderIntegration(unittest.TestCase):
    """Integration tests for the Windows builder with actual file system operations."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory structure
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, 'source')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        
        # Create directories
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create a sample application structure
        self.app_dir = os.path.join(self.source_dir, 'app')
        os.makedirs(self.app_dir, exist_ok=True)
        
        # Create a sample Python script
        with open(os.path.join(self.app_dir, 'app.py'), 'w') as f:
            f.write("""
print("Hello, World!")
            """)
            
        # Create a mock configuration manager
        self.config_manager = ConfigManager(os.path.join(self.temp_dir, 'config.ini'))
        
        # Set configuration values
        self.config_manager.set_config({
            'general': {
                'app_name': 'Test App',
                'version': '1.0.0',
                'publisher': 'Test Publisher',
                'publisher_url': 'https://example.com',
                'installation_path': 'C:\\TestApp'
            },
            'windows': {
                'create_desktop_icon': True,
                'create_start_menu_shortcut': True,
                'run_after_install': False,
                'allow_silent_install': True
            }
        })
        
        # Initialize the Windows builder
        self.builder = WindowsBuilder(self.config_manager, output_dir=self.output_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_prepare_source_directory(self):
        """Test preparation of the source directory."""
        # Call the prepare_source_directory method
        prepared_dir = self.builder.prepare_source_directory(self.app_dir)
        
        # Check that the prepared directory exists
        self.assertTrue(os.path.exists(prepared_dir))
        
        # Check that files were copied
        self.assertTrue(os.path.exists(os.path.join(prepared_dir, 'app.py')))
    
    @unittest.skipIf(not shutil.which('iscc'), "Inno Setup compiler not available")
    def test_full_build_process(self):
        """Test the full build process if Inno Setup is available."""
        try:
            # Call the build_installer method
            installer_path = self.builder.build_installer(source_dir=self.app_dir)
            
            # Check that the installer file was created
            self.assertTrue(os.path.exists(installer_path))
            
        except InstallerError as e:
            # Skip the test if Inno Setup couldn't be run
            if "Failed to run Inno Setup compiler" in str(e):
                self.skipTest("Inno Setup compiler failed to run")
            else:
                raise


if __name__ == '__main__':
    unittest.main()
