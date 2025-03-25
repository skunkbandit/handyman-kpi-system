# Building the Handyman KPI System Installer

This guide provides simple, step-by-step instructions for building the Windows installer for the Handyman KPI System.

## Prerequisites

Before starting, make sure you have the following installed on your computer:

- [Python 3.8 or higher](https://www.python.org/downloads/)
- [Inno Setup 6 or higher](https://jrsoftware.org/isdl.php)
- [Git](https://git-scm.com/downloads)
- Python packages: Pillow (will be installed automatically)

## Quick Start Guide

### Method 1: Using the Batch File (Recommended)

1. Simply run the `build_installer.bat` file in the project root directory:
   ```
   build_installer.bat
   ```

This script will automatically:
- Ensure all resource files exist or create them
- Build the installer with the correct configuration
- Handle common errors and provide clear feedback

### Method 2: Using Python Directly

1. Open Command Prompt or PowerShell
2. Navigate to your project folder:
   ```
   cd C:\path\to\handyman-kpi-system
   ```
3. Run the build script:
   ```
   python scripts\build_installer.py
   ```

### Method 3: Using the Module Directly (Legacy)

For advanced users or compatibility with older scripts:

```
python -m installer windows --version 1.0.0
```

You can change the version number as needed.

## Locating the Installer

Once the build process completes:

1. Navigate to the `installer\dist` folder
2. Look for a file named `handyman-kpi-system-setup.exe`

## Troubleshooting

If you encounter problems:

### Missing Resource Files

If you see errors about missing wizard images or icons:
- The build script should automatically create these files
- If not, run `python scripts\create_installer_images.py` to generate them manually

### Python PATH Warnings

The warnings about Python scripts not being in the PATH are normal and can be safely ignored:
```
WARNING: The script X.exe is installed in 'path' which is not on PATH.
```
These are informational messages and do not affect the build process.

### Inno Setup Not Found

If the build script cannot find Inno Setup:
- Make sure Inno Setup 6 is installed
- Confirm it's installed in one of these locations:
  - `C:\Program Files (x86)\Inno Setup 6\`
  - `C:\Program Files\Inno Setup 6\`

### Other Issues

For other issues:
1. Make sure all prerequisites are installed
2. Check that you're running the scripts from the project root directory
3. Try running in a command prompt with administrator privileges

## Getting Help

If you continue to experience problems after trying the troubleshooting steps above, please contact IT support or refer to the detailed developer documentation.
