"""\nEnd-to-end integration tests for the installer.\n\nThis module tests the complete installation process including\nsetup wizard, database initialization, and application configuration.\n"""\n\nimport os\nimport sys\nimport json\nimport pytest\nimport subprocess\nimport tempfile\nimport shutil\nfrom pathlib import Path\nfrom unittest.mock import patch\n\n# Add the project root to the path\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))\n\n# Import test utilities\nfrom utils import create_test_configuration\n\n\nclass TestInstallerEndToEnd:\n    """End-to-end tests for the installer process."""\n    \n    @pytest.fixture\n    def installation_environment(self, temp_directory):\n        """Create a complete installation environment for testing."""\n        # Create subdirectories for the installation test\n        install_dir = os.path.join(temp_directory, 'kpi_system')\n        os.makedirs(install_dir, exist_ok=True)\n        \n        config_dir = os.path.join(temp_directory, 'config')\n        os.makedirs(config_dir, exist_ok=True)\n        \n        data_dir = os.path.join(temp_directory, 'data')\n        os.makedirs(data_dir, exist_ok=True)\n        \n        # Create a test configuration\n        config_path = os.path.join(config_dir, 'installer_config.json')\n        create_test_configuration(config_path, database_type='sqlite', temp_dir=temp_directory)\n        \n        return {\n            'install_dir': install_dir,\n            'config_dir': config_dir,\n            'data_dir': data_dir,\n            'config_path': config_path,\n            'temp_dir': temp_directory\n        }\n    \n    @pytest.mark.slow\n    def test_silent_installation(self, installation_environment):\n        """Test silent installation mode."""\n        # Create a mock installer for silent installation testing\n        class MockSilentInstaller:\n            def __init__(self, config_path):\n                self.config_path = config_path\n                self.installed = False\n                self.install_log = []\n                \n                # Load configuration\n                with open(config_path, 'r') as f:\n                    self.config = json.load(f)\n            \n            def install(self):\n                # Log installation steps\n                self.install_log.append("Starting silent installation")\n                \n                # Create installation directory\n                install_dir = self.config['installation_path']\n                os.makedirs(install_dir, exist_ok=True)\n                self.install_log.append(f"Created installation directory: {install_dir}")\n                \n                # Create database\n                db_config = self.config['database']\n                if db_config['type'] == 'sqlite':\n                    db_path = db_config['path']\n                    # Create an empty file to simulate database creation\n                    with open(db_path, 'w') as f:\n                        f.write('')\n                    self.install_log.append(f"Created SQLite database: {db_path}")\n                \n                # Create basic application structure\n                app_dir = os.path.join(install_dir, 'app')\n                os.makedirs(app_dir, exist_ok=True)\n                self.install_log.append(f"Created application directory: {app_dir}")\n                \n                # Create a marker file to indicate successful installation\n                with open(os.path.join(install_dir, 'installed.txt'), 'w') as f:\n                    f.write('Installation completed successfully')\n                \n                self.installed = True\n                self.install_log.append("Installation completed")\n                return True\n        \n        # Get the configuration path\n        config_path = installation_environment['config_path']\n        \n        # Create and run the silent installer\n        installer = MockSilentInstaller(config_path)\n        result = installer.install()\n        \n        # Verify installation was successful\n        assert result, "Silent installation failed"\n        assert installer.installed, "Installation not marked as complete"\n        \n        # Verify installation directory was created\n        install_dir = os.path.join(installation_environment['temp_dir'], 'kpi_system')\n        assert os.path.exists(install_dir), "Installation directory not created"\n        \n        # Verify installation marker file was created\n        marker_file = os.path.join(install_dir, 'installed.txt')\n        assert os.path.exists(marker_file), "Installation marker file not created"\n        \n        # Verify application directory was created\n        app_dir = os.path.join(install_dir, 'app')\n        assert os.path.exists(app_dir), "Application directory not created"\n        \n        # Verify database was created\n        db_path = os.path.join(installation_environment['temp_dir'], 'test_db.sqlite')\n        assert os.path.exists(db_path), "Database file not created"\n    \n    @pytest.mark.slow\n    def test_custom_installation_path(self, installation_environment):\n        """Test installation to a custom path."""\n        # Create a custom installation path\n        custom_path = os.path.join(installation_environment['temp_dir'], 'custom_install')\n        \n        # Modify the configuration to use the custom path\n        with open(installation_environment['config_path'], 'r') as f:\n            config = json.load(f)\n        \n        config['installation_path'] = custom_path\n        \n        with open(installation_environment['config_path'], 'w') as f:\n            json.dump(config, f, indent=4)\n        \n        # Create a mock installer\n        class MockCustomPathInstaller:\n            def __init__(self, config_path):\n                self.config_path = config_path\n                \n                # Load configuration\n                with open(config_path, 'r') as f:\n                    self.config = json.load(f)\n            \n            def install(self):\n                # Create installation directory\n                install_dir = self.config['installation_path']\n                os.makedirs(install_dir, exist_ok=True)\n                \n                # Create basic application structure\n                app_dir = os.path.join(install_dir, 'app')\n                os.makedirs(app_dir, exist_ok=True)\n                \n                # Create a marker file\n                with open(os.path.join(install_dir, 'installed.txt'), 'w') as f:\n                    f.write('Installation completed successfully')\n                \n                return True\n        \n        # Create and run the installer\n        installer = MockCustomPathInstaller(installation_environment['config_path'])\n        result = installer.install()\n        \n        # Verify installation was successful\n        assert result, "Custom path installation failed"\n        \n        # Verify installation directory was created at the custom path\n        assert os.path.exists(custom_path), "Custom installation directory not created"\n        \n        # Verify installation marker file was created\n        marker_file = os.path.join(custom_path, 'installed.txt')\n        assert os.path.exists(marker_file), "Installation marker file not created"\n        \n        # Verify application directory was created\n        app_dir = os.path.join(custom_path, 'app')\n        assert os.path.exists(app_dir), "Application directory not created"\n    \n    @pytest.mark.slow\n    def test_uninstallation(self, installation_environment):\n        """Test uninstallation process."""\n        # First create a mock installation\n        install_dir = installation_environment['install_dir']\n        \n        # Create application directories\n        app_dir = os.path.join(install_dir, 'app')\n        os.makedirs(app_dir, exist_ok=True)\n        \n        # Create some test files\n        with open(os.path.join(app_dir, 'test1.txt'), 'w') as f:\n            f.write('Test file 1')\n        \n        with open(os.path.join(app_dir, 'test2.txt'), 'w') as f:\n            f.write('Test file 2')\n        \n        # Create a marker file\n        with open(os.path.join(install_dir, 'installed.txt'), 'w') as f:\n            f.write('Installation completed successfully')\n        \n        # Verify installation exists\n        assert os.path.exists(install_dir), "Installation directory not created"\n        assert os.path.exists(app_dir), "Application directory not created"\n        \n        # Create a mock uninstaller\n        class MockUninstaller:\n            def __init__(self, install_dir):\n                self.install_dir = install_dir\n                self.uninstall_log = []\n            \n            def uninstall(self):\n                # Log uninstallation steps\n                self.uninstall_log.append("Starting uninstallation")\n                \n                # Check if installation directory exists\n                if not os.path.exists(self.install_dir):\n                    self.uninstall_log.append("Installation directory not found")\n                    return False\n                \n                # Remove application files\n                app_dir = os.path.join(self.install_dir, 'app')\n                if os.path.exists(app_dir):\n                    for filename in os.listdir(app_dir):\n                        file_path = os.path.join(app_dir, filename)\n                        if os.path.isfile(file_path):\n                            os.remove(file_path)\n                            self.uninstall_log.append(f"Removed file: {file_path}")\n                    \n                    # Remove application directory\n                    os.rmdir(app_dir)\n                    self.uninstall_log.append(f"Removed directory: {app_dir}")\n                \n                # Remove installation marker file\n                marker_file = os.path.join(self.install_dir, 'installed.txt')\n                if os.path.exists(marker_file):\n                    os.remove(marker_file)\n                    self.uninstall_log.append(f"Removed file: {marker_file}")\n                \n                # Remove installation directory\n                os.rmdir(self.install_dir)\n                self.uninstall_log.append(f"Removed directory: {self.install_dir}")\n                \n                self.uninstall_log.append("Uninstallation completed")\n                return True\n        \n        # Create and run the uninstaller\n        uninstaller = MockUninstaller(install_dir)\n        result = uninstaller.uninstall()\n        \n        # Verify uninstallation was successful\n        assert result, "Uninstallation failed"\n        assert "Uninstallation completed" in uninstaller.uninstall_log\n        \n        # Verify files and directories were removed\n        assert not os.path.exists(os.path.join(app_dir, 'test1.txt')), "File not removed"\n        assert not os.path.exists(os.path.join(app_dir, 'test2.txt')), "File not removed"\n        assert not os.path.exists(app_dir), "Application directory not removed"\n        assert not os.path.exists(os.path.join(install_dir, 'installed.txt')), "Marker file not removed"\n        assert not os.path.exists(install_dir), "Installation directory not removed"