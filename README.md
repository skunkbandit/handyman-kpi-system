# Handyman KPI System

A comprehensive KPI (Key Performance Indicator) tracking system for handyman businesses with tiered skill structure (apprentice, handyman, craftsman, master craftsman, lead craftsman) and performance evaluation.

## Installation Fixes

This repository contains fixes for the Handyman KPI System installation process, addressing database path issues and terminal window problems.

### Issues Fixed

1. **Database Configuration Issue**: 
   - The SQLite database is now stored in the user's AppData directory for proper write permissions
   - Added automatic database initialization during installation
   - Implemented a fallback mechanism for database path detection

2. **Terminal Window Issue**:
   - Application now runs as a detached process
   - No console window stays open during application execution
   - Modified desktop shortcut to hide console window

## How to Apply Fixes

### For Existing Installations

1. Download the `fix_installation.bat` script from this repository
2. Run the script as administrator
3. Use the new desktop shortcut created by the fix script to launch the application

### For New Installations

The fixes will be integrated into future installers and will be applied automatically during installation.

## Technical Details

### Database Path Fix

The database path has been changed to use the following locations (in order of precedence):

1. Path from environment variable `KPI_SYSTEM_DATABASE_PATH`
2. Path from config file in `%LOCALAPPDATA%\Handyman KPI System\config\database.json`
3. Default path in `%LOCALAPPDATA%\Handyman KPI System\database\kpi_system.db`

### Launcher Fix

The application launcher has been modified to:

1. Use `subprocess.Popen()` with detached process flags instead of `subprocess.run()`
2. Use `CREATE_NO_WINDOW` to hide the console window on Windows
3. Create a proper desktop shortcut that uses `pythonw.exe` instead of `python.exe`

## Default Login Credentials

After applying the fixes, you can log in with the following default credentials:

- **Username**: admin
- **Password**: admin

Please change these credentials after your first login.

## Features

- Employee management with skill tiers
- Performance evaluation based on role-specific metrics
- Dashboard with performance trends
- Detailed reports and analytics
- User management with role-based access control

## System Requirements

- Windows 10 or 11
- 500MB of disk space
- 4GB RAM (minimum)
- 1024×768 screen resolution

## Support

For issues or questions, please create an issue in this repository or contact support.
