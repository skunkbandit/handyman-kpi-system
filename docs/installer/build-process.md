# Handyman KPI System Installer Build Process

This document explains how to build the Windows installer for the Handyman KPI System using the improved build script.

## Prerequisites

Before building the installer, ensure you have the following prerequisites installed:

1. **Inno Setup** - Download from [jrsoftware.org/isinfo.php](https://jrsoftware.org/isinfo.php) (version 5 or 6)
2. **Python 3.8+** - Must be installed and added to PATH
3. **Git** - For version control (optional but recommended)

## Building the Installer

### Method 1: Using the Automated Build Script

The easiest way to build the installer is using the improved build script:

1. Open a command prompt in the project root directory
2. Run the following command:

```batch
build_installer_fixed.bat
```

This script will:
- Automatically detect Inno Setup location
- Create all necessary directories
- Check for required files
- Download dependencies if needed
- Generate the configuration for the installer
- Build the installer with all available components

The resulting installer will be located at:

```
installer\output\handyman-kpi-system-setup.exe
```

### Method 2: Manual Build Process

If you need more control over the build process, you can follow these steps:

1. Create the necessary directories:
   - `installer\output`
   - `wheels`
   - `installers`

2. Ensure the following required files exist:
   - `handyman_kpi_launcher_detached.py`
   - `initialize_database.py`

3. Download dependencies:
   - Run `python scripts\download_wheels.py` to get Python wheel files
   - Download GTK3 Runtime installer and place in `installers` directory

4. Create a configuration file with your desired settings:
   - Define which components to include
   - Specify paths for resources

5. Run the Inno Setup compiler with your configuration:
   - `iscc "scripts\installer.iss"`

## Installer Components

The build process can include the following components based on their availability:

| Component | Directory/File | Purpose | Required? |
|-----------|---------------|---------|-----------|
| Core Files | `handyman_kpi_launcher_detached.py` and `initialize_database.py` | Main application launcher and database initializer | Yes |
| KPI System | `kpi-system` directory | Core application code and resources | Recommended |
| Resources | `resources` directory | Icons, images, and other resource files | Recommended |
| Wheels | `wheels` directory | Python package dependencies | Recommended |
| GTK3 Runtime | `installers\gtk3-runtime-installer.exe` | Required for WeasyPrint and PDF generation | Recommended |
| Scripts | `scripts\install_weasyprint.bat` and `scripts\create_shortcuts.ps1` | Installation helper scripts | Recommended |
| Documentation | `README.md` and `LICENSE` | User documentation and license | Optional |

## Troubleshooting

### Common Issues

1. **"Inno Setup Compiler (iscc.exe) not found"**
   - Make sure Inno Setup is installed
   - Add the Inno Setup directory to your PATH environment variable
   - Alternatively, input the full path to iscc.exe when prompted

2. **"Required file not found" errors**
   - Ensure all required files exist in the project root
   - Clone the repository again if files are missing

3. **"Failed to build installer"**
   - Check the Inno Setup compiler output for specific errors
   - Ensure you have write permissions to the output directory
   - Make sure no other process is using the output file

4. **WeasyPrint Installation Failures**
   - Ensure Python is correctly installed
   - Try installing WeasyPrint manually: `pip install weasyprint`
   - Check that GTK3 Runtime is properly downloaded

## Advanced Configuration

For advanced users who need to customize the installer:

1. Edit `scripts\installer_fixed.iss` to change:
   - Installer appearance
   - Default installation directory
   - Application metadata
   - Custom installation actions

2. Modify the build script to:
   - Include additional files
   - Configure optional components
   - Customize post-installation steps

## Version History

The build script creates dated backup copies of successful builds in:
```
installer\output\handyman-kpi-system-setup-YYYYMMDD.exe
```

This helps with version tracking and rollback if needed.

## Deployment

After building a successful installer:

1. Test the installer on a clean system
2. Verify all components are installed correctly
3. Check that the application runs properly
4. Push the installer to GitHub releases for distribution

## Need Help?

If you encounter issues not covered in this document, please:

1. Check the project's GitHub issues page
2. Create a new issue with detailed error information
3. Contact the project maintainers for support