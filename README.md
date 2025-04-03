# Handyman KPI System

A comprehensive KPI (Key Performance Indicator) tracking system for handyman businesses with tiered skill structure (apprentice, handyman, craftsman, master craftsman, lead craftsman) and performance evaluation.

## New Version 1.2.0 - Improved Installation Experience

The latest version of the Handyman KPI System includes significant improvements to the installation process and overall reliability:

- Database now stored in user's AppData folder (no admin rights needed for daily use)
- No console window appears when running the application
- Automatic database initialization with default admin user
- Improved desktop shortcuts and browser access option
- WeasyPrint dependency handled automatically
- Fixed template and form issues

## Installation

### System Requirements

- Windows 10 or 11
- Python 3.8 or higher (must be installed beforehand)
- 500MB disk space
- Internet connection (for downloading dependencies)

### Installation Steps

1. Download the installer from [Releases](https://github.com/skunkbandit/handyman-kpi-system/releases)
2. Run the installer and follow the on-screen instructions
3. After installation completes, the application will start automatically
4. Log in with the default credentials:
   - Username: `admin`
   - Password: `admin`
5. **Important**: Change the default password immediately after first login

### Alternative Installation Methods

If you prefer not to use the installer, you can clone this repository and run the application directly:

```bash
git clone https://github.com/skunkbandit/handyman-kpi-system.git
cd handyman-kpi-system
python -m pip install -r requirements.txt
python handyman_kpi_launcher_detached.py
```

## Features

- **Employee Management**: Track employees across 5 skill tiers
- **Performance Evaluation**: Comprehensive KPI tracking system
- **Reporting**: Generate detailed reports on employee performance
- **Dashboard**: Visual overview of team performance metrics
- **User Management**: Role-based access control

## User Roles

- **Admin**: Full access to all features and settings
- **Manager**: Can manage employees and evaluations
- **Employee**: Can view their own evaluations and reports

## Documentation

For detailed documentation, please refer to the [User Guide](docs/user_guide.md) and [Admin Guide](docs/admin_guide.md).

## Troubleshooting

### Common Issues

1. **Application doesn't start**
   - Make sure Python is installed and added to PATH
   - Check the logs in `%LOCALAPPDATA%\Handyman KPI System\logs`
   - If you see `AttributeError: module 'app' has no attribute 'create_app'`, run the [App Import Fix](docs/APP_IMPORT_FIX.md)

2. **Database errors**
   - The database is located at `%LOCALAPPDATA%\Handyman KPI System\database\kpi_system.db`
   - If database is corrupt, delete it and restart the application to create a new one

3. **PDF generation issues**
   - Make sure GTK3 Runtime is installed (included with the installer)
   - If PDF reports fail, check logs for specific errors

4. **Installer build issues**
   - If you're building the installer, use the `build_installer_complete.bat` script
   - See the [installer build documentation](docs/installer/build-scripts-guide.md) for details

### Known Issues and Solutions

| Issue | Description | Solution |
|-------|-------------|----------|
| App Import Error | `AttributeError: module 'app' has no attribute 'create_app'` | Run `python fix_app_import.py` and then the resulting batch file |
| WeasyPrint Issues | PDF generation fails | Make sure GTK3 Runtime is installed |
| Missing Files After Install | Installer doesn't include all necessary files | Use the latest `build_installer_complete.bat` to create installer |

### Getting Help

If you encounter any issues, please:

1. Check the logs in `%LOCALAPPDATA%\Handyman KPI System\logs`
2. Open an issue on our [GitHub repository](https://github.com/skunkbandit/handyman-kpi-system/issues)
3. Include any relevant error messages and log files

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
