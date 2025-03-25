# Windows Installer Changelog

## Version 1.0.6 (2025-03-20) - Shortcut Fix

### Fixed
- Resolved shortcut creation permission errors
- Changed installation privilege model to use `lowest` instead of `admin`
- Updated shortcut creation to use user-specific desktop
- Changed default installation directory to use LocalAppData
- Created a consistent permission model focusing on per-user installation

## Version 1.0.5 (2025-03-20) - Import Fix

### Fixed
- Resolved Flask app import errors by fixing module structure
- Fixed app module to properly expose Flask app object
- Enhanced import error handling with fallback methods
- Added detailed error reporting for troubleshooting
- Fixed installer privileges warning by using `PrivilegesRequiredOverridesAllowed`

## Version 1.0.4 (2025-03-20) - Permission Fix

### Fixed
- Resolved Windows path permission issues by moving data storage to AppData
- Improved directory and file creation with better error handling
- Added detailed logging of paths and operations
- Enhanced error messages with specific guidance for permission issues

## Version 1.0.3 (2025-03-20) - Dependency Fixes

### Fixed
- Resolved tkinter dependency issue by replacing GUI wizard with console-based setup
- Simplified Python package dependencies in build script
- Added fallback options for missing modules
- Implemented more robust error handling with detailed diagnostics

## Version 1.0.2 (2025-03-20) - Application Launch Fixes

### Fixed
- Resolved issue with application not staying open after launch
- Fixed batch file to prevent console window from closing immediately
- Updated Flask application structure to match demo requirements
- Improved browser launch timing with a delay and separate thread
- Enhanced error handling with detailed diagnostic information

## Version 1.0.1 (2025-03-20) - Resource and Icon Fixes

### Fixed
- Resolved issue with missing `logo.png` file by creating placeholder resources
- Fixed icon creation error by providing a pre-created icon file
- Removed invalid icon file references from the Inno Setup script
- Corrected Inno Setup compilation errors by ensuring all required files exist
- Updated installer script to use `{autopf}` for better Windows compatibility

### Added
- Created complete basic application structure for testing
- Added detailed error handling in launcher script
- Implemented improved setup wizard for first-time users
- Created comprehensive documentation of installation process

### Changed
- Modified build script to use pre-created resources instead of downloading
- Updated launcher to use Waitress as the WSGI server
- Improved application startup experience

## Version 1.0.0 (2025-03-19) - Initial Release

### Features
- Single-click installation of Handyman KPI System
- Self-contained Python environment
- Database setup wizard
- Desktop and Start Menu shortcuts
- Support for SQLite, MySQL, and PostgreSQL databases
