# Handyman KPI System - Launcher Module

This directory contains the core launcher for the Handyman KPI System.

## Recent Fixes

### App Import Fix (April 1, 2025)

The launcher has been updated to fix the "ModuleNotFoundError: No module named 'app'" issue that was occurring during application startup. This error was caused by incorrect Python path configuration in the launcher script.

#### Key Changes

1. Enhanced Python path configuration:
   - Added the backend directory to PYTHONPATH
   - Added the app module directory to PYTHONPATH
   - Added the parent directory to PYTHONPATH

2. Improved error handling:
   - Added a fallback mechanism using Python's module import system
   - Enhanced logging to make future troubleshooting easier

#### How to Apply the Fix

For existing installations:

1. Run the `fix_launcher.bat` script included in the project directory
2. Rebuild the installer with `rebuild_installer.bat`
3. Test the installation to verify the fix

For new installations:

- The fix is already included in the latest installer

## Components

- `handyman_kpi_launcher.py`: Main application launcher
- `backend/`: Backend application code
- `app/`: Flask application module

## Architecture

The launcher follows this execution flow:

1. Detect installation environment and configure paths
2. Locate Python interpreter and application script
3. Set up PYTHONPATH for proper module resolution
4. Launch the application with proper environment variables
5. Handle errors and provide diagnostic information

## Troubleshooting

If you encounter issues with module imports or application startup:

1. Check the log file at `<installation_dir>/logs/launcher.log`
2. Verify that Python is properly installed at `<installation_dir>/python/python.exe`
3. Ensure all application files are present in the expected locations
4. Run the launcher with administrative privileges if necessary

## Building the Launcher

The launcher is built into an executable using PyInstaller. See the `create_launcher.bat` script for details.
