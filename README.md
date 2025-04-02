# Handyman KPI System

A comprehensive KPI (Key Performance Indicator) tracking system for handyman businesses with tiered skill structure (apprentice, handyman, craftsman, master craftsman, lead craftsman) and performance evaluation.

## Installation Fixes

This repository contains fixes for the Handyman KPI System installation process, addressing database path issues and terminal window problems.

### Issues Fixed

1. **Database Schema Issue**: 
   - Fixed SQLite error `no such column: users.employee_id` by updating the database schema
   - Added missing columns to match the expected schema
   - Implemented a database location fix to use AppData for proper write permissions
   - Added automatic database initialization during installation

2. **Terminal Window Issue**:
   - Fixed the issue where the console window stays open and if closed, it kills the application
   - Application now runs as a detached process with no visible console window
   - Modified desktop shortcut to use pythonw.exe instead of python.exe
   - Added a browser shortcut option for direct access

3. **CSRF Token Missing Error**:
   - Fixed "400 Bad Request: The CSRF token is missing" error when trying to add new employees
   - Added missing CSRF token input fields to employee forms

4. **User-Employee Linking Issue** (Added April 2, 2025):
   - Fixed issue where employee names weren't displaying in user management dropdowns
   - Updated templates to correctly reference the `name` field instead of non-existent `first_name`/`last_name` fields
   - Fixed field value mismatch between `employee_id` and `id` in templates
   - See [User-Employee Linking Fix README](fixes/README-user-employee-linking-fix.md) for details

## How to Apply Fixes

### For Users With Admin Access

1. Download the `fix_kpi_system.bat` script from this repository
2. Run the script as administrator
3. Follow the on-screen instructions
4. Use the new desktop shortcuts to launch the application

### For Users Without Admin Access

1. Download the `fix_kpi_system.bat` script
2. Run the script as regular user
3. Database fixes will be applied automatically
4. Follow the on-screen instructions to complete the launcher fix

### For User-Employee Linking Issue

1. Download the `fix_user_employee_linking_direct.bat` script
2. Run the script in the KPI system root directory
3. The fix will automatically backup and update the affected templates

## Technical Details

### Database Schema Fix

The `fix_database_schema.py` script:

1. Examines the current database schema
2. Compares it with the expected schema from `schema.sql`
3. Adds missing columns (particularly `employee_id`)
4. Creates a default admin user if none exists

### Launcher Window Fix

The `fix_launcher_window.py` script:

1. Creates a detached launcher using `subprocess.Popen()` with proper flags
2. Creates improved desktop shortcuts using `pythonw.exe`
3. Sets proper process creation flags to hide the console window
4. Provides admin deployment instructions if needed

### User-Employee Linking Fix

The `fix_user_employee_linking.py` script:

1. Creates backups of the original template files
2. Updates the field references in the templates to match the Employee model
3. Corrects the dropdown options to show employee names properly

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

For issues or questions, please create an issue in this repository.
