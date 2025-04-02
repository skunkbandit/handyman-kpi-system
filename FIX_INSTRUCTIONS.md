# Handyman KPI System - Fix Instructions

## Database Schema and Launcher Issues Fix

This document provides instructions for fixing the following issues with the Handyman KPI System:

1. Database schema mismatch causing SQL errors
2. Launcher issues with terminal window remaining open

## Quick Fix Instructions

For immediate fix of both issues, follow these steps:

1. Right-click on `fix_kpi_system_complete.bat` and select "Run as Administrator"
2. Follow the on-screen prompts
3. Once completed, use the newly created desktop shortcut to start the application

## Manual Fix Instructions

If you prefer to fix the issues step-by-step, follow the instructions below:

### Fix Database Schema Issues

1. Open a Command Prompt as Administrator
2. Navigate to the installation directory: `cd "C:\Program Files\Handyman KPI System"`
3. Run the database fix script: `python fix_database_all.py`
4. The script will create a backup of the current database and fix the schema issues

### Fix Launcher Issues

1. Open a Command Prompt as Administrator
2. Navigate to the installation directory: `cd "C:\Program Files\Handyman KPI System"`
3. Run the launcher creation script: `python create_detached_launcher.py`
4. The script will create a proper detached launcher that runs without showing a terminal window

## Verification

To verify that the fixes have been applied successfully:

1. Launch the application using the desktop shortcut
2. Log in with the default admin user (if you haven't set up other users):
   - Username: `admin`
   - Password: `admin`
3. Navigate to the employee management section to ensure that employee data is displayed correctly

## Troubleshooting

If you encounter any issues with the fixes:

1. Check the log files in `C:\Users\[username]\AppData\Local\Handyman KPI System\logs\`
2. Try running the fix scripts individually to see which step is failing
3. If the database fix fails, you can restore from the backup created by the script

## Technical Details

### Database Schema Fix

The database schema fix addresses a mismatch between the SQLAlchemy models and the actual database tables:

- Fixes the `employees` table to use `employee_id` as the primary key
- Consolidates `first_name` and `last_name` fields into a single `name` field
- Updates the `tier` field to use string values instead of numeric IDs
- Ensures foreign key relationships are correctly maintained

### Detached Launcher Fix

The detached launcher fix creates a properly detached launcher that:

- Uses `pythonw.exe` instead of `python.exe` to run without a console window
- Redirects all output to log files instead of the console
- Properly handles process creation to ensure the application runs in the background
- Creates a desktop shortcut that uses the detached launcher

## Support

If you need further assistance with these fixes, please contact support.
