# Handyman KPI System - Launcher Module

This directory contains the core launcher for the Handyman KPI System.

## Recent Fixes

### Complete Import and Permissions Fix (April 1, 2025)

We've implemented a comprehensive solution that addresses multiple issues with the application installer:

1. **Python Module Import Fix**:
   - Enhanced Python path configuration in the launcher
   - Implemented an alternative import method in the backend script
   - Added paths for all necessary directories (backend, app, site-packages)

2. **Log File Permissions Fix**:
   - Changed log file location from Program Files to AppData
   - Created a central app data directory for user-specific data
   - Added environment variable support for components to use the same path

3. **Enhanced Debugging**:
   - Added output capture from subprocess execution
   - Improved error reporting and logging
   - Added verification of critical directories and files

The application now correctly handles module imports and respects Windows security models.

### Log File Permission Fix (April 1, 2025)

The launcher has been updated to fix the "Permission denied" error when writing to log files in the Program Files directory. This error occurred because standard users don't have write access to the Program Files directory.

#### Key Changes

1. Log file location moved to user's AppData directory:
   - Changed from `C:\Program Files\Handyman KPI System\logs` to `%LOCALAPPDATA%\Handyman KPI System\logs`
   - This directory is user-specific and doesn't require elevated permissions

2. Added application data directory access:
   - Added a new environment variable `KPI_SYSTEM_APP_DATA` for the application to use
   - This allows components to consistently access the same user data directory

3. Improved logging information:
   - Added more detailed logging to help with troubleshooting
   - Added a console message showing the log file location

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

## Components

- `handyman_kpi_launcher.py`: Main application launcher
- `backend/run.py`: Backend application initialization script
- `backend/app/`: Flask application module

## Architecture

The launcher follows this execution flow:

1. Set up logging in the user's AppData directory
2. Detect installation environment and configure paths
3. Locate Python interpreter and application script
4. Set up PYTHONPATH for proper module resolution
5. Launch the application with proper environment variables
6. Handle errors and provide diagnostic information

## Troubleshooting

If you encounter issues with the application startup:

1. Check the log files at:
   - `%LOCALAPPDATA%\Handyman KPI System\logs\launcher.log`
   - `%LOCALAPPDATA%\Handyman KPI System\logs\backend.log`
2. Verify that Python is properly installed at `<installation_dir>/python/python.exe`
3. Ensure all application files are present in the expected locations
4. Make sure your user account has normal user permissions (elevated permissions shouldn't be needed)

## Building the Launcher

The launcher is built into an executable using PyInstaller. See the `create_launcher.bat` script for details.
