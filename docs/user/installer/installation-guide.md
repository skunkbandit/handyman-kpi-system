# Handyman KPI System Installation Guide

This guide will walk you through installing the Handyman KPI System on your Windows computer.

## System Requirements

Before installing, make sure your computer meets these minimum requirements:

- **Operating System**: Windows 10 (64-bit) or newer
- **Processor**: 2.0 GHz dual-core processor or better
- **Memory**: 4 GB RAM minimum (8 GB recommended)
- **Disk Space**: 1 GB of free disk space
- **Display**: 1280 x 720 screen resolution or higher
- **Internet**: Required for initial setup and database synchronization

## Pre-Installation Checklist

Before starting the installation:

1. Ensure you have administrator privileges on your computer
2. Close any applications that might be using the database
3. Back up any existing data if you're upgrading from a previous version
4. Disable any antivirus software temporarily (can sometimes interfere with installation)

## Installation Steps

### Step 1: Obtain the Installer

1. Download the Handyman KPI System installer (`handyman-kpi-system-[version]-setup.exe`) from the company portal or IT department
2. Save the installer to a location you can easily access, like your Desktop or Downloads folder

### Step 2: Run the Installer

1. Right-click on the installer file and select "Run as administrator"
2. If you see a User Account Control (UAC) prompt, click "Yes" to allow the installation

### Step 3: Welcome Screen

1. The installer welcome screen will appear
2. Click "Next" to continue

### Step 4: License Agreement

1. Read the software license agreement carefully
2. Select "I accept the agreement" if you agree to the terms
3. Click "Next" to continue

### Step 5: Select Installation Location

1. Choose where you want to install the Handyman KPI System
2. The default location is `C:\Program Files\Handyman KPI System`
3. Click "Next" to continue with the default location or "Browse" to select a different folder

### Step 6: Database Configuration

1. Select the database type you want to use:
   - **SQLite** (default): Best for single-user installations
   - **MySQL**: For multi-user environments with an existing MySQL server
   - **PostgreSQL**: For enterprise environments with an existing PostgreSQL server

2. For SQLite:
   - The installer will automatically set up the database
   
3. For MySQL or PostgreSQL:
   - Enter the server address (hostname)
   - Enter the database name
   - Enter the username and password
   - Click "Test Connection" to verify your settings

4. Click "Next" to continue

### Step 7: Select Components

1. Choose which components to install:
   - **Core Application** (required)
   - **Documentation**
   - **Sample Data**
   - **Administrative Tools**

2. Click "Next" to continue

### Step 8: Start Menu Folder

1. Choose the Start Menu folder where shortcuts will be created
2. Click "Next" to continue

### Step 9: Ready to Install

1. Review the installation settings summary
2. Click "Install" to begin the installation process

### Step 10: Installation Progress

1. The installer will copy files and configure your system
2. This may take several minutes to complete

### Step 11: Complete the Setup

1. When the installation is complete, you'll see a confirmation screen
2. You can choose to:
   - Launch the Handyman KPI System now
   - View the README file
   - Create a desktop shortcut
3. Click "Finish" to complete the installation

## First-Time Setup

When you first launch the Handyman KPI System, you'll need to complete a few additional setup steps:

1. **Create Administrator Account**
   - Set up the main administrator username and password
   - This account will have full access to all features

2. **Company Information**
   - Enter your company's name and contact information
   - Upload your company logo (optional)

3. **System Configuration**
   - Set your preferred options for reports and notifications
   - Configure backup schedules
   - Set user permissions

## Troubleshooting

### Common Installation Issues

1. **"Installation failed" error**
   - Make sure you're running as administrator
   - Temporarily disable antivirus and firewall
   - Check that your system meets the minimum requirements

2. **Database connection errors**
   - Verify that the database server is running
   - Double-check the hostname, username, and password
   - Make sure the database user has the necessary permissions

3. **"Missing component" errors**
   - Run the installer again and select "Repair"
   - Try downloading a fresh copy of the installer

## Getting Help

If you encounter issues not covered in this guide:

1. Contact your IT department
2. Email support@handyman-kpi.com
3. Call technical support at 1-800-555-1234 (Monday-Friday, 9am-5pm ET)
