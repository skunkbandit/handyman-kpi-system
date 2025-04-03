# Changelog

All notable changes to the Handyman KPI System will be documented in this file.

## [1.2.1] - 2025-04-03

### Fixed
- Fixed installer build script to correctly include all necessary directories
- Updated run.py with robust module loading to prevent "module 'app' has no attribute 'create_app'" error
- Improved handling of Python path and module imports for more reliable application startup
- Enhanced logging for better troubleshooting of startup issues

### Added
- Comprehensive build script documentation in docs/installer/
- Improved error handling in application startup
- More detailed troubleshooting information in README

## [1.2.0] - 2025-03-25

### Added
- Database now stored in user's AppData folder (no admin rights needed for daily use)
- Automatic database initialization with default admin user
- Browser access option via desktop shortcut
- Improved desktop shortcuts for easier access
- WeasyPrint dependency handled automatically during installation

### Fixed
- Eliminated console window when running the application
- Fixed template and form issues in the user interface
- Resolved CSRF token validation errors
- Fixed employee-user linking in database schema
- Corrected date handling in reports and evaluations

## [1.1.0] - 2025-03-10

### Added
- Support for custom evaluation templates
- Enhanced reporting capabilities with PDF export
- Improved dashboard with visual performance indicators
- User permission management system

### Changed
- Redesigned employee profile interface
- Optimized database queries for better performance
- Improved mobile responsiveness for all views

### Fixed
- Corrected calculation errors in performance metrics
- Fixed pagination issues in employee listings
- Resolved login session persistence problems

## [1.0.0] - 2025-02-15

### Initial Release
- Core KPI tracking functionality
- Employee management across 5 skill tiers
- Basic reporting capabilities
- User authentication and role-based access control
- Dashboard with key metrics visualization
