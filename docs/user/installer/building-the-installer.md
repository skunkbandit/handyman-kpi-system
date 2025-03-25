# Building the Handyman KPI System Installer

This guide provides simple, step-by-step instructions for building the Windows installer for the Handyman KPI System.

## Prerequisites

Before starting, make sure you have the following installed on your computer:

- [Python 3.8 or higher](https://www.python.org/downloads/)
- [Inno Setup 6 or higher](https://jrsoftware.org/isdl.php)
- [Git](https://git-scm.com/downloads)

## Quick Start Guide

### Step 1: Set Up Your Environment

1. Open Command Prompt or PowerShell
2. Navigate to your project folder:
   ```
   cd C:\path\to\handyman-kpi-system
   ```

### Step 2: Build the Installer

Run the following command:

```
python -m installer windows --version 1.0.0
```

You can change the version number as needed.

### Step 3: Locate the Installer

Once the build process completes:

1. Navigate to the `installer\dist` folder
2. Look for a file named `handyman-kpi-system-1.0.0-setup.exe`
3. This is your installer executable that you can distribute to users

## Additional Options

### Specifying an Output Directory

To save the installer in a different location:

```
python -m installer windows --version 1.0.0 --output-dir C:\path\to\output
```

### Specifying a Custom Configuration

If you have a custom configuration file:

```
python -m installer windows --version 1.0.0 --config my_config.ini
```

## What's Happening Behind the Scenes

When you run the build command, the system:

1. Creates temporary working directories
2. Downloads an embedded version of Python
3. Gathers all required files for the application
4. Installs necessary dependencies
5. Creates an Inno Setup script
6. Compiles the installer executable

## Troubleshooting

If you encounter problems:

- **"Python is not recognized as an internal or external command"**
  - Python may not be installed correctly or not added to your PATH
  - Try reinstalling Python and select the option to add Python to PATH during installation

- **'Inno Setup Compiler (ISCC) not found'**
  - Make sure Inno Setup is installed
  - Check if it's installed in one of these locations:
    - `C:\Program Files (x86)\Inno Setup 6\`
    - `C:\Program Files\Inno Setup 6\`

- **"Error downloading Python distribution"**
  - Check your internet connection
  - Try running the command again

- **"Unable to clone repository"**
  - Ensure Git is installed correctly
  - Check your internet connection

## Getting Help

If you continue to experience problems after trying the troubleshooting steps above, please contact IT support or refer to the detailed developer documentation.
