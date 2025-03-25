# Handyman KPI System - Windows Installer

This directory contains the tools to build a Windows installer package for the Handyman KPI System.

## Overview

The installer provides a simple way for non-technical users to install and run the Handyman KPI System application without needing to understand Docker containers or Python virtual environments.

## Features

- Single-click installation
- Self-contained Python environment
- Automatic database setup wizard
- Desktop and Start Menu shortcuts
- Support for SQLite, MySQL, and PostgreSQL databases
- No command-line knowledge required

## Building the Installer

### Prerequisites

1. Windows 10 or higher
2. [Inno Setup 6](https://jrsoftware.org/isdl.php) or higher installed
3. Git client installed
4. Internet connection for downloading dependencies

### Build Steps

1. Clone this repository: `git clone https://github.com/skunkbandit/handyman-kpi-system.git`
2. Navigate to the windows-installer directory: `cd handyman-kpi-system/windows-installer`
3. Run the build script: `build_installer.bat`
4. The installer will be created in the `output` directory

## Installation Process

When a user runs the installer:

1. Files are copied to the installation directory (default: `C:\Program Files\Handyman KPI System`)
2. Shortcuts are created in the Start Menu and optionally on the Desktop
3. On first run, the Database Setup Wizard launches to configure the database
4. The application runs as a web service in the background, opening a browser window to the application

## Using the Installer Package

The installer package (handyman-kpi-system-setup.exe) can be distributed to users via:

- Direct download
- File sharing
- USB drive
- Company intranet

## Technical Details

The installer package includes:

- Embedded Python 3.10 distribution
- All required Python packages
- Application code
- Database schema files
- Custom launcher scripts
- Database setup wizard

## Troubleshooting

If users encounter issues with the installation:

1. Check if they have admin privileges (required for installation)
2. Verify all dependencies were installed correctly
3. Check the application logs in `%PROGRAMDATA%\Handyman KPI System\logs`
4. Ensure the database connection is properly configured
5. If you encounter resource-related errors during the build process, check the README-FIXES.md file

## Recent Updates

### 2025-03-20: Installer Fixes

The installer build process has been updated to fix the following issues:

1. Fixed missing resource files (logo.png and icon.ico)
2. Added complete basic application structure for testing
3. Updated installer script paths for better Windows compatibility
4. Improved launcher functionality

See README-FIXES.md for more detailed information about these changes.

## License

This installer package is part of the Handyman KPI System project and is released under the same license.
