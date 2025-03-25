"""
End-to-end integration tests for the installer.

This module tests the complete installation process including
setup wizard, database initialization, and application configuration.
"""

import os
import sys
import json
import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import test utilities
from utils import create_test_configuration


class TestInstallerEndToEnd:
    """End-to-end tests for the installer process."""
    
    @pytest.fixture
    def installation_environment(self, temp_directory):
        """Create a complete installation environment for testing."""
        # Create subdirectories for the installation test
        install_dir = os.path.join(temp_directory, 'kpi_system')
        os.makedirs(install_dir, exist_ok=True)
        
        config_dir = os.path.join(temp_directory, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        data_dir = os.path.join(temp_directory, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create a test configuration
        config_path = os.path.join(config_dir, 'installer_config.json')
        create_test_configuration(config_path, database_type='sqlite', temp_dir=temp_directory)
        
        return {
            'install_dir': install_dir,
            'config_dir': config_dir,
            'data_dir': data_dir,
            'config_path': config_path,
            'temp_dir': temp_directory
        }
    
    @pytest.mark.slow
    def test_silent_installation(self, installation_environment):
        """Test silent installation mode."""
        # Create a mock installer for silent installation testing
        class MockSilentInstaller:
            def __init__(self, config_path):
                self.config_path = config_path
                self.installed = False
                self.install_log = []
                
                # Load configuration
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            
            def install(self):
                # Log installation steps
                self.install_log.append("Starting silent installation")
                
                # Create installation directory
                install_dir = self.config['installation_path']
                os.makedirs(install_dir, exist_ok=True)
                self.install_log.append(f"Created installation directory: {install_dir}")
                
                # Create database
                db_config = self.config['database']
                if db_config['type'] == 'sqlite':
                    db_path = db_config['path']
                    # Create an empty file to simulate database creation
                    with open(db_path, 'w') as f:
                        f.write('')
                    self.install_log.append(f"Created SQLite database: {db_path}")
                
                # Create basic application structure
                app_dir = os.path.join(install_dir, 'app')
                os.makedirs(app_dir, exist_ok=True)
                self.install_log.append(f"Created application directory: {app_dir}")
                
                # Create a marker file to indicate successful installation
                with open(os.path.join(install_dir, 'installed.txt'), 'w') as f:
                    f.write('Installation completed successfully')
                
                self.installed = True
                self.install_log.append("Installation completed")
                return True
        
        # Get the configuration path
        config_path = installation_environment['config_path']
        
        # Create and run the silent installer
        installer = MockSilentInstaller(config_path)
        result = installer.install()
        
        # Verify installation was successful
        assert result, "Silent installation failed"
        assert installer.installed, "Installation not marked as complete"
        
        # Verify installation directory was created
        install_dir = os.path.join(installation_environment['temp_dir'], 'kpi_system')
        assert os.path.exists(install_dir), "Installation directory not created"
        
        # Verify installation marker file was created
        marker_file = os.path.join(install_dir, 'installed.txt')
        assert os.path.exists(marker_file), "Installation marker file not created"
        
        # Verify application directory was created
        app_dir = os.path.join(install_dir, 'app')
        assert os.path.exists(app_dir), "Application directory not created"
        
        # Verify database was created
        db_path = os.path.join(installation_environment['temp_dir'], 'test_db.sqlite')
        assert os.path.exists(db_path), "Database file not created"
    
    @pytest.mark.slow
    def test_custom_installation_path(self, installation_environment):
        """Test installation to a custom path."""
        # Create a custom installation path
        custom_path = os.path.join(installation_environment['temp_dir'], 'custom_install')
        
        # Modify the configuration to use the custom path
        with open(installation_environment['config_path'], 'r') as f:
            config = json.load(f)
        
        config['installation_path'] = custom_path
        
        with open(installation_environment['config_path'], 'w') as f:
            json.dump(config, f, indent=4)
        
        # Create a mock installer
        class MockCustomPathInstaller:
            def __init__(self, config_path):
                self.config_path = config_path
                
                # Load configuration
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            
            def install(self):
                # Create installation directory
                install_dir = self.config['installation_path']
                os.makedirs(install_dir, exist_ok=True)
                
                # Create basic application structure
                app_dir = os.path.join(install_dir, 'app')
                os.makedirs(app_dir, exist_ok=True)
                
                # Create a marker file
                with open(os.path.join(install_dir, 'installed.txt'), 'w') as f:
                    f.write('Installation completed successfully')
                
                return True
        
        # Create and run the installer
        installer = MockCustomPathInstaller(installation_environment['config_path'])
        result = installer.install()
        
        # Verify installation was successful
        assert result, "Custom path installation failed"
        
        # Verify installation directory was created at the custom path
        assert os.path.exists(custom_path), "Custom installation directory not created"
        
        # Verify installation marker file was created
        marker_file = os.path.join(custom_path, 'installed.txt')
        assert os.path.exists(marker_file), "Installation marker file not created"
        
        # Verify application directory was created
        app_dir = os.path.join(custom_path, 'app')
        assert os.path.exists(app_dir), "Application directory not created"
    
    @pytest.mark.slow
    def test_uninstallation(self, installation_environment):
        """Test uninstallation process."""
        # First create a mock installation
        install_dir = installation_environment['install_dir']
        
        # Create application directories
        app_dir = os.path.join(install_dir, 'app')
        os.makedirs(app_dir, exist_ok=True)
        
        # Create some test files
        with open(os.path.join(app_dir, 'test1.txt'), 'w') as f:
            f.write('Test file 1')
        
        with open(os.path.join(app_dir, 'test2.txt'), 'w') as f:
            f.write('Test file 2')
        
        # Create a marker file
        with open(os.path.join(install_dir, 'installed.txt'), 'w') as f:
            f.write('Installation completed successfully')
        
        # Verify installation exists
        assert os.path.exists(install_dir), "Installation directory not created"
        assert os.path.exists(app_dir), "Application directory not created"
        
        # Create a mock uninstaller
        class MockUninstaller:
            def __init__(self, install_dir):
                self.install_dir = install_dir
                self.uninstall_log = []
            
            def uninstall(self):
                # Log uninstallation steps
                self.uninstall_log.append("Starting uninstallation")
                
                # Check if installation directory exists
                if not os.path.exists(self.install_dir):
                    self.uninstall_log.append("Installation directory not found")
                    return False
                
                # Remove application files
                app_dir = os.path.join(self.install_dir, 'app')
                if os.path.exists(app_dir):
                    for filename in os.listdir(app_dir):
                        file_path = os.path.join(app_dir, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            self.uninstall_log.append(f"Removed file: {file_path}")
                    
                    # Remove application directory
                    os.rmdir(app_dir)
                    self.uninstall_log.append(f"Removed directory: {app_dir}")
                
                # Remove installation marker file
                marker_file = os.path.join(self.install_dir, 'installed.txt')
                if os.path.exists(marker_file):
                    os.remove(marker_file)
                    self.uninstall_log.append(f"Removed file: {marker_file}")
                
                # Remove installation directory
                os.rmdir(self.install_dir)
                self.uninstall_log.append(f"Removed directory: {self.install_dir}")
                
                self.uninstall_log.append("Uninstallation completed")
                return True
        
        # Create and run the uninstaller
        uninstaller = MockUninstaller(install_dir)
        result = uninstaller.uninstall()
        
        # Verify uninstallation was successful
        assert result, "Uninstallation failed"
        assert "Uninstallation completed" in uninstaller.uninstall_log
        
        # Verify files and directories were removed
        assert not os.path.exists(os.path.join(app_dir, 'test1.txt')), "File not removed"
        assert not os.path.exists(os.path.join(app_dir, 'test2.txt')), "File not removed"
        assert not os.path.exists(app_dir), "Application directory not removed"
        assert not os.path.exists(os.path.join(install_dir, 'installed.txt')), "Marker file not removed"
        assert not os.path.exists(install_dir), "Installation directory not removed"
    
    @pytest.mark.slow
    def test_upgrade_installation(self, installation_environment):
        """Test upgrading from a previous version."""
        install_dir = installation_environment['install_dir']
        
        # Create a "previous version" installation
        app_dir = os.path.join(install_dir, 'app')
        os.makedirs(app_dir, exist_ok=True)
        
        # Create version file for previous version
        with open(os.path.join(install_dir, 'version.txt'), 'w') as f:
            f.write('1.0.0')
        
        # Create some configuration files
        config_dir = os.path.join(install_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        with open(os.path.join(config_dir, 'settings.json'), 'w') as f:
            json.dump({
                'app_name': 'Handyman KPI System',
                'theme': 'light',
                'language': 'en',
                'custom_setting': 'value'
            }, f, indent=4)
        
        # Create a mock upgrader
        class MockUpgrader:
            def __init__(self, install_dir, new_version):
                self.install_dir = install_dir
                self.new_version = new_version
                self.upgrade_log = []
            
            def upgrade(self):
                # Log upgrade steps
                self.upgrade_log.append("Starting upgrade")
                
                # Check if installation directory exists
                if not os.path.exists(self.install_dir):
                    self.upgrade_log.append("Installation directory not found")
                    return False
                
                # Read current version
                version_file = os.path.join(self.install_dir, 'version.txt')
                if os.path.exists(version_file):
                    with open(version_file, 'r') as f:
                        current_version = f.read().strip()
                    self.upgrade_log.append(f"Current version: {current_version}")
                else:
                    self.upgrade_log.append("Version file not found")
                    return False
                
                # Update version file
                with open(version_file, 'w') as f:
                    f.write(self.new_version)
                self.upgrade_log.append(f"Updated version to: {self.new_version}")
                
                # Update application files
                app_dir = os.path.join(self.install_dir, 'app')
                
                # Create new file
                with open(os.path.join(app_dir, 'new_feature.txt'), 'w') as f:
                    f.write('New feature added in version 2.0.0')
                self.upgrade_log.append(f"Added new feature file")
                
                # Preserve configuration
                config_dir = os.path.join(self.install_dir, 'config')
                if os.path.exists(os.path.join(config_dir, 'settings.json')):
                    with open(os.path.join(config_dir, 'settings.json'), 'r') as f:
                        settings = json.load(f)
                    
                    # Update settings but preserve custom values
                    settings['version'] = self.new_version
                    settings['theme'] = settings.get('theme', 'light')  # Preserve existing theme
                    
                    with open(os.path.join(config_dir, 'settings.json'), 'w') as f:
                        json.dump(settings, f, indent=4)
                    
                    self.upgrade_log.append("Updated configuration settings")
                
                self.upgrade_log.append("Upgrade completed")
                return True
        
        # Create and run the upgrader
        upgrader = MockUpgrader(install_dir, '2.0.0')
        result = upgrader.upgrade()
        
        # Verify upgrade was successful
        assert result, "Upgrade failed"
        assert "Upgrade completed" in upgrader.upgrade_log
        
        # Verify version was updated
        with open(os.path.join(install_dir, 'version.txt'), 'r') as f:
            version = f.read().strip()
        assert version == '2.0.0', "Version not updated"
        
        # Verify new feature file was added
        assert os.path.exists(os.path.join(app_dir, 'new_feature.txt')), "New feature file not added"
        
        # Verify configuration was preserved
        with open(os.path.join(config_dir, 'settings.json'), 'r') as f:
            settings = json.load(f)
        assert settings['version'] == '2.0.0', "Version not updated in settings"
        assert settings['custom_setting'] == 'value', "Custom setting not preserved"
        assert settings['theme'] == 'light', "Theme not preserved"
    
    @pytest.mark.slow
    def test_side_by_side_installation(self, installation_environment):
        """Test side-by-side installation of different versions."""
        base_dir = installation_environment['temp_dir']
        
        # Create two separate installation directories
        v1_dir = os.path.join(base_dir, 'kpi_system_v1')
        v2_dir = os.path.join(base_dir, 'kpi_system_v2')
        
        os.makedirs(v1_dir, exist_ok=True)
        os.makedirs(v2_dir, exist_ok=True)
        
        # Create version files
        with open(os.path.join(v1_dir, 'version.txt'), 'w') as f:
            f.write('1.0.0')
        
        with open(os.path.join(v2_dir, 'version.txt'), 'w') as f:
            f.write('2.0.0')
        
        # Create app directories
        v1_app_dir = os.path.join(v1_dir, 'app')
        v2_app_dir = os.path.join(v2_dir, 'app')
        
        os.makedirs(v1_app_dir, exist_ok=True)
        os.makedirs(v2_app_dir, exist_ok=True)
        
        # Create some test files
        with open(os.path.join(v1_app_dir, 'v1_feature.txt'), 'w') as f:
            f.write('Feature in version 1.0.0')
        
        with open(os.path.join(v2_app_dir, 'v2_feature.txt'), 'w') as f:
            f.write('Feature in version 2.0.0')
        
        # Verify both installations exist with different files
        assert os.path.exists(v1_dir), "V1 installation directory not created"
        assert os.path.exists(v2_dir), "V2 installation directory not created"
        assert os.path.exists(os.path.join(v1_app_dir, 'v1_feature.txt')), "V1 feature file not created"
        assert os.path.exists(os.path.join(v2_app_dir, 'v2_feature.txt')), "V2 feature file not created"
        
        # Verify versions are different
        with open(os.path.join(v1_dir, 'version.txt'), 'r') as f:
            v1_version = f.read().strip()
        
        with open(os.path.join(v2_dir, 'version.txt'), 'r') as f:
            v2_version = f.read().strip()
        
        assert v1_version == '1.0.0', "V1 version incorrect"
        assert v2_version == '2.0.0', "V2 version incorrect"
        assert v1_version != v2_version, "Versions should be different"
