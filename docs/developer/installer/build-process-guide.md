# Windows Installer Build Process Guide

This guide explains how to generate the Windows installer for the Handyman KPI System using the modular installer framework.

## Overview

The Windows installer for the Handyman KPI System is built using a combination of Python scripts and Inno Setup. The process involves:

1. Setting up the build environment
2. Running the installer build script
3. Collecting and packaging dependencies
4. Generating the final installer executable

## Prerequisites

Before you can build the Windows installer, you need to have the following installed:

- Python 3.8 or higher
- Inno Setup 6 or higher (download from [innosetup.com](https://innosetup.com))
- Git (for repository cloning)
- Required Python packages (installed automatically during the build process)

## Build Process

### Method 1: Using the Command-Line Interface

1. **Open Command Prompt or PowerShell**

2. **Navigate to the project directory**
   ```
   cd C:\path\to\handyman-kpi-system
   ```

3. **Run the installer build command**
   ```
   python -m installer windows --version 1.0.0 --output-dir .\dist
   ```

   - `--version` specifies the version number for the installer
   - `--output-dir` specifies where the installer should be saved (optional, defaults to `.\installer\dist`)

4. **Wait for the build process to complete**
   
   This can take several minutes as it:
   - Downloads the embedded Python distribution
   - Clones the repository (if needed)
   - Installs dependencies
   - Generates the Inno Setup script
   - Compiles the installer

5. **Locate the installer**
   
   Once complete, the installer will be available in the specified output directory with a name like:
   ```
   handyman-kpi-system-1.0.0-setup.exe
   ```

### Method 2: Using Python Code

You can also trigger the build process from your own Python code:

```python
from installer.build.windows import WindowsBuilder

# Create a builder instance
builder = WindowsBuilder(
    repo_url="https://github.com/skunkbandit/handyman-kpi-system",
    version="1.0.0",
    output_dir="./dist"
)

# Run the build process
installer_path = builder.build()

print(f"Installer created: {installer_path}")
```

## Build Configuration Options

The Windows builder supports several configuration options:

| Option | Description | Default |
|--------|-------------|---------|
| `repo_url` | GitHub repository URL | https://github.com/skunkbandit/handyman-kpi-system |
| `version` | Version number for the installer | 1.0.0 |
| `output_dir` | Output directory for the installer | ./installer/dist |

## Build Process Details

The build process performs the following steps:

1. **Create temporary directories**
   - Creates a temporary directory for building the installer
   - Sets up subdirectories for Python, app files, and installer components

2. **Download Python embedded distribution**
   - Downloads the Python 3.10 embedded distribution
   - Extracts it to the temporary Python directory
   - Installs pip and enables it in the embedded distribution

3. **Clone the repository**
   - Clones the GitHub repository to the temporary app directory
   - Checks out the specified branch (main by default)

4. **Install dependencies**
   - Installs required Python packages from requirements.txt
   - Ensures all dependencies are available in the embedded Python

5. **Build Inno Setup script**
   - Copies the Inno Setup template
   - Replaces placeholders with actual values (version, paths, etc.)
   - Customizes the installer behavior and appearance

6. **Compile the installer**
   - Runs the Inno Setup compiler (ISCC.exe)
   - Generates the final installer executable
   - Copies it to the specified output directory

## Customizing the Installer

You can customize various aspects of the installer by modifying these files:

1. **Inno Setup Script Template**
   - Located at: `installer/platforms/windows/inno/installer.iss`
   - Controls installer appearance, behavior, and components

2. **Windows Builder Class**
   - Located at: `installer/build/windows.py`
   - Controls the build process and dependencies

## Troubleshooting

### Common Issues

1. **"Inno Setup Compiler (ISCC) not found"**
   - Ensure Inno Setup is installed
   - Add Inno Setup to your PATH environment variable
   - Check the standard installation paths:
     - `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
     - `C:\Program Files\Inno Setup 6\ISCC.exe`

2. **"Error downloading Python distribution"**
   - Check your internet connection
   - Verify the Python URL in the WindowsBuilder class
   - Try downloading the distribution manually

3. **"Unable to clone repository"**
   - Ensure Git is installed and available in your PATH
   - Check your internet connection
   - Verify you have access to the repository

4. **"Error installing dependencies"**
   - Check for any package-specific error messages
   - Ensure required system dependencies are installed
   - Try installing the dependencies manually to identify issues

5. **"Installer not found in output directory"**
   - Check the Inno Setup compiler output for errors
   - Verify the output directory is writable
   - Check for any issues with file permissions

## Testing the Installer

After building the installer, it's recommended to test it in a clean environment:

1. Copy the installer to a clean test machine or virtual machine
2. Run the installer and verify all components are installed correctly
3. Test the application functionality to ensure everything works as expected
