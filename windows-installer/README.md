# Windows Installer for Handyman KPI System

This directory contains the files needed to build a Windows installer for the Handyman KPI System.

## Recent Fixes

The following issues have been fixed:

1. Fixed Flask app import error:
   - Modified `app/__init__.py` to create and export a global app instance
   - Enhanced Python path handling in the launcher script
   - Added multiple fallback options for importing the Flask app
   
2. Fixed installation path issues:
   - Ensured proper installation to `{localappdata}\Handyman KPI System`
   - Updated launcher to use the correct paths

## Building the Installer

1. Run the `rebuild_installer.bat` script to build the installer
2. The output will be in the `output` directory as `handyman-kpi-system-setup.exe`

## Installation

After building, the installer can be run on Windows systems to install the application. The installation will:

1. Copy required files to the user's AppData directory
2. Create Start Menu and Desktop shortcuts
3. Run a setup wizard on first launch to configure the database
4. Start the application automatically after installation if requested

## Troubleshooting

If you encounter issues with the installation:

1. Check the console output for error messages
2. Verify that Python dependencies are correctly installed
3. Make sure no other application is using port 5000
4. Check that the user has write permission to their AppData directory