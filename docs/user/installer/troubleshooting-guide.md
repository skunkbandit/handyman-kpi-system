# Handyman KPI System Installation Troubleshooting Guide

This guide provides solutions for common issues you might encounter when installing or running the Handyman KPI System.

## Installation Issues

### Installation Fails to Start

**Symptoms:**
- Double-clicking the installer doesn't do anything
- You get an error message when trying to run the installer
- The installer opens and then immediately closes

**Solutions:**
1. **Run as Administrator**
   - Right-click the installer file
   - Select "Run as administrator"

2. **Check File Integrity**
   - Re-download the installer
   - Verify the file isn't corrupted

3. **Disable Antivirus Temporarily**
   - Some antivirus programs may block the installer
   - Temporarily disable your antivirus software
   - Remember to enable it again after installation

### Installation Freezes or Takes Too Long

**Symptoms:**
- The progress bar stops moving
- Installation has been running for more than 30 minutes

**Solutions:**
1. **Check System Resources**
   - Close other applications to free up memory
   - Restart your computer and try again
   
2. **Check Disk Space**
   - Ensure you have at least 1GB of free disk space
   
3. **Manual Termination and Retry**
   - Press Ctrl+Alt+Del and end the installer process
   - Restart your computer
   - Try installing again

## Database Configuration Issues

### Cannot Connect to Database Server

**Symptoms:**
- "Connection failed" error during database setup
- "Could not connect to server" message

**Solutions:**
1. **Verify Server Credentials**
   - Double-check the hostname/IP address
   - Confirm username and password are correct
   
2. **Check Server Status**
   - Ensure the database server is running
   - Try connecting with another tool to verify server accessibility
   
3. **Check Firewall Settings**
   - Ensure your firewall allows connections to the database port
     - MySQL typically uses port 3306
     - PostgreSQL typically uses port 5432

### Database Initialization Errors

**Symptoms:**
- "Error creating database schema" message
- "Permission denied" errors

**Solutions:**
1. **Check User Permissions**
   - Ensure the database user has CREATE, ALTER, and DROP permissions
   
2. **Manual Database Creation**
   - Create the database manually before installation
   - Grant proper permissions to the user

3. **Check Database Version**
   - Verify your database server version is compatible
     - MySQL: 5.7 or higher
     - PostgreSQL: 10.0 or higher

## Post-Installation Issues

### Application Won't Start

**Symptoms:**
- Clicking the application shortcut does nothing
- You see an error message when trying to start the application
- The application starts and then immediately closes

**Solutions:**
1. **Run as Administrator (First Time Only)**
   - Right-click the application shortcut
   - Select "Run as administrator"
   
2. **Check Installation Logs**
   - Look in `C:\ProgramData\Handyman KPI System\logs` for error messages
   
3. **Repair Installation**
   - Run the installer again
   - Select the "Repair" option
   
4. **Check Windows Event Viewer**
   - Press Win+R, type "eventvwr" and press Enter
   - Look for errors related to the application

### Missing Components or Features

**Symptoms:**
- Certain features are unavailable
- You see "Component not found" errors
- Menu items are grayed out

**Solutions:**
1. **Rerun Installer to Add Components**
   - Run the installer again
   - Select the "Modify" option
   - Check boxes for missing components
   
2. **Check Permissions**
   - Ensure your Windows user account has full access to the installation folder
   
3. **Verify Requirements**
   - Some features may require additional components
   - Check the documentation for specific feature requirements

## Security and Permission Issues

### Access Denied Errors

**Symptoms:**
- "Access denied" messages
- "Insufficient permissions" errors
- Unable to save settings or data

**Solutions:**
1. **Run as Administrator**
   - Right-click the application shortcut
   - Select "Run as administrator"
   
2. **Check Folder Permissions**
   - Right-click on the installation folder (typically `C:\Program Files\Handyman KPI System`)
   - Select "Properties"
   - Go to the "Security" tab
   - Click "Edit" and ensure your user account has "Full control"
   
3. **Run in Compatibility Mode**
   - Right-click the application shortcut
   - Select "Properties"
   - Go to the "Compatibility" tab
   - Check "Run this program as an administrator"
   - Click "Apply" and "OK"

### UAC (User Account Control) Issues

**Symptoms:**
- You repeatedly get UAC prompts when using the application
- Some features don't work properly with UAC enabled

**Solutions:**
1. **Adjust UAC Settings**
   - Press Win+R, type "UserAccountControlSettings" and press Enter
   - Adjust the slider to a lower setting (not recommended to turn it off completely)
   - Click "OK" and restart your computer
   
2. **Move Installation to Non-Protected Folder**
   - During installation, choose a location outside of Program Files
   - Example: `C:\HandymanKPI`

## Database-Specific Issues

### SQLite Issues

**Symptoms:**
- Database file is locked
- Cannot write to database
- Application crashes when accessing certain features

**Solutions:**
1. **Check File Permissions**
   - Ensure the database file has write permissions
   
2. **Close Other Applications**
   - Make sure no other applications are using the database file
   
3. **Repair Database**
   - From the Tools menu, select "Database Maintenance"
   - Click "Repair Database"

### MySQL Issues

**Symptoms:**
- Connection timeouts
- "Too many connections" errors
- Slow performance

**Solutions:**
1. **Check MySQL Server Configuration**
   - Verify that max_connections is set appropriately
   - Ensure the server has enough resources

2. **Optimize Database**
   - Run the MySQL optimization tools on your database
   
3. **Update MySQL Drivers**
   - From the Help menu, select "Check for Updates"
   - Update database drivers if available

### PostgreSQL Issues

**Symptoms:**
- Authentication issues
- Schema errors
- Performance problems

**Solutions:**
1. **Verify PostgreSQL Authentication Method**
   - Check that the authentication method in pg_hba.conf is compatible
   
2. **Check Database User Roles**
   - Ensure the user has the necessary roles and permissions
   
3. **Update PostgreSQL Drivers**
   - From the Help menu, select "Check for Updates"
   - Update database drivers if available

## Advanced Troubleshooting

### Using Diagnostic Tools

1. **Enable Verbose Logging**
   - From the Settings menu, select "Advanced"
   - Set "Logging Level" to "Debug"
   - Save settings and restart the application
   - Logs will be stored in `C:\ProgramData\Handyman KPI System\logs`

2. **Run Built-in Diagnostics**
   - From the Help menu, select "Diagnostics"
   - Click "Run Diagnostics"
   - Save the report when prompted

3. **Check Windows Event Logs**
   - Press Win+R, type "eventvwr" and press Enter
   - Check "Application" logs for entries from "Handyman KPI System"

### Reinstallation

If all else fails, a clean reinstallation may be necessary:

1. **Backup Your Data**
   - From the File menu, select "Backup Database"
   - Save the backup file to a safe location

2. **Uninstall Completely**
   - Go to Control Panel > Programs > Uninstall a program
   - Select "Handyman KPI System" and uninstall
   - Delete any remaining files in the installation folder
   - Delete `C:\ProgramData\Handyman KPI System` (backup any important data first)

3. **Clean Registry (Advanced Users Only)**
   - Press Win+R, type "regedit" and press Enter
   - Navigate to `HKEY_LOCAL_MACHINE\SOFTWARE`
   - Look for and delete the "Handyman KPI System" key
   - Navigate to `HKEY_CURRENT_USER\SOFTWARE`
   - Look for and delete the "Handyman KPI System" key

4. **Reinstall**
   - Run the installer as administrator
   - Follow the installation steps

5. **Restore Your Data**
   - From the File menu, select "Restore Database"
   - Select your backup file

## Getting Help

If you've tried these solutions and are still experiencing issues:

1. **Contact IT Support**
   - Your internal IT department may be able to help

2. **Contact Technical Support**
   - Email: support@handyman-kpi.com
   - Phone: 1-800-555-1234 (Monday-Friday, 9am-5pm ET)

3. **Online Resources**
   - Visit our knowledge base at: https://support.handyman-kpi.com
   - Check for updated troubleshooting guides and FAQs
