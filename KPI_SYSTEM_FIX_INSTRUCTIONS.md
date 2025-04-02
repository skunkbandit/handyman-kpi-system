# Handyman KPI System - Fix Instructions

## Overview

This document provides instructions for fixing two major issues with the Handyman KPI System:

1. **Database Schema Mismatch**: The SQLAlchemy models expect a different database schema than what exists in the database, causing SQL errors.
2. **Launcher Issues**: The terminal window stays open and if closed, kills the application.

## Quick Fix Instructions

The easiest way to fix both issues is to run the comprehensive fix script:

1. Open Command Prompt as Administrator
2. Navigate to the directory where you've downloaded the fix scripts
3. Run `fix_kpi_system_complete.bat`

This script will:
- Fix the database schema issues
- Install the detached launcher
- Create a proper desktop shortcut

## Manual Fix Instructions

If you prefer to fix issues individually or need more control, follow these steps:

### 1. Fix Database Schema

```
python fix_database_all.py
```

This script will:
- Back up your existing database
- Fix the employees table structure
- Fix the users table structure
- Add a default admin user if needed

### 2. Fix Launcher Issues

Copy the `handyman_kpi_launcher_detached.pyw` file to your installation directory (typically `C:\Program Files\Handyman KPI System\`).

Create a shortcut with the following properties:
- Target: `"C:\Program Files\Handyman KPI System\python\pythonw.exe" "C:\Program Files\Handyman KPI System\handyman_kpi_launcher_detached.pyw"`
- Start in: `"C:\Program Files\Handyman KPI System\"`
- Icon: `"C:\Program Files\Handyman KPI System\kpi-system\static\images\favicon.ico"`

## Technical Details

### Database Schema Issue

The database schema issue involves a mismatch between the SQLAlchemy models and the actual database structure:

- The model expects `employee_id` as the primary key, but the database has `id`
- The model expects a single `name` field, but the database has separate `first_name` and `last_name` fields
- The model expects a string `tier` field, but the database has a numeric `tier_id` field

The fix script restructures the tables to match what the application expects while preserving existing data.

### Launcher Issue

The launcher issue is caused by the application running in a foreground console process. The fix creates a detached launcher that:

- Uses `pythonw.exe` instead of `python.exe` to avoid showing a console window
- Redirects all output to log files instead of the console
- Properly backgrounds the process
- Includes error handling and recovery mechanisms

## Default Login

After running the fix scripts, you can log in with:

- Username: **admin**
- Password: **admin**

**Important**: Please change this password immediately after logging in.

## Logs and Troubleshooting

Logs are stored in:
`C:\Users\[YourUsername]\AppData\Local\Handyman KPI System\logs\`

Check these files if you encounter any issues:
- `database_fix_all.log` - Database fix log
- `kpi_system_YYYYMMDD.log` - Application runtime log

## Support

If you encounter any issues with these fixes, please contact technical support or submit an issue on the GitHub repository.
