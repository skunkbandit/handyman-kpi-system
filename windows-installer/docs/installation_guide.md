# Handyman KPI System - Installation Guide

This guide will walk you through the installation process for the Handyman KPI System on Windows.

## System Requirements

- Windows 10 or higher (64-bit)
- 500 MB of free disk space
- Administrator privileges for installation
- Network connection for multi-user database (optional)

## Installation Steps

1. **Download the Installer**
   
   Download the `handyman-kpi-system-setup.exe` file from the provided location.

2. **Run the Installer**
   
   Double-click the installer file to begin the installation process.
   
   *Note: If you see a User Account Control (UAC) prompt asking for permission to make changes to your device, click "Yes" to continue.*

3. **Follow the Installation Wizard**
   
   The installer will guide you through these steps:
   
   - Accept the license agreement
   - Choose an installation directory (default: `C:\Program Files\Handyman KPI System`)
   - Select Start Menu folder
   - Choose whether to create a desktop shortcut
   - Review your selections and click "Install"

4. **Complete the Installation**
   
   After the files are installed, you'll see a completion screen. Leave the "Launch Handyman KPI System" checkbox checked and click "Finish".

## First-Run Setup

When you first run the application, you'll go through a one-time setup process:

1. **Database Configuration**
   
   The setup wizard will guide you through configuring the database:
   
   - **SQLite** (Recommended for single users)
     - Simplest option with no additional setup required
     - Data stored locally in the application directory
   
   - **MySQL** or **PostgreSQL** (For multi-user environments)
     - Requires an existing database server
     - You'll need to provide connection details (host, port, database name, username, password)

2. **Admin Account Creation**
   
   You'll create an administrator account:
   
   - Enter a username (default: "admin")
   - Create a secure password (minimum 8 characters)

3. **Setup Completion**
   
   After the setup is complete, the application will start automatically and open in your default web browser.

## Accessing the Application

After installation, you can access the Handyman KPI System in several ways:

- **Desktop Shortcut**: Double-click the "Handyman KPI System" icon on your desktop (if you chose to create one)
- **Start Menu**: Go to Start Menu > Handyman KPI System > Handyman KPI System
- **Browser**: Once the application is running, open your web browser and go to `http://localhost:8080`

## Uninstalling

To uninstall the Handyman KPI System:

1. Go to Control Panel > Programs > Programs and Features
2. Find "Handyman KPI System" in the list
3. Click "Uninstall" and follow the prompts

*Note: Uninstalling will not remove your database or configuration files by default. These are stored in `%APPDATA%\Handyman KPI System`.*

## Troubleshooting

- **Application doesn't start**: Check your antivirus settings to ensure it's not blocking the application.
- **Database connection error**: Verify your database server is running and credentials are correct.
- **Browser doesn't open**: Manually navigate to `http://localhost:8080` in your web browser.
- **Port conflict**: If port 8080 is already in use, edit the config.ini file in the installation directory and change the port.

## Getting Help

For additional assistance, please:

- Refer to the full user documentation
- Contact your system administrator
- Submit an issue on the GitHub repository
