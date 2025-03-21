# Handyman KPI System

A comprehensive performance tracking and evaluation system for handyman businesses with tiered employee structures.

## Overview

This application helps handyman businesses track employee performance across different skill categories and tool proficiencies. It supports the company's five-tier system:
- Apprentice
- Handyman
- Craftsman 
- Master Craftsman
- Lead Craftsman

The system allows for regular evaluations, progress tracking, skill gap analysis, and comprehensive reporting.

## Features

- **Employee Management**: Track employee information, skill levels, and career progression
- **Skill Evaluation**: Rate employee proficiency in various skill categories
- **Tool Proficiency**: Track tools employees can operate and own
- **Performance Dashboard**: Visual analytics of employee and team performance 
- **Comprehensive Reports**: Generate PDF and Excel reports for performance reviews and analysis
- **Authentication System**: Secure login with role-based permissions and user management
- **Multi-Database Support**: Works with SQLite, MySQL, and PostgreSQL

## Technical Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Data Visualization**: Chart.js
- **Database**: SQLite (development), MySQL/PostgreSQL (production)
- **Reporting**: WeasyPrint (PDF generation), XlsxWriter (Excel export)
- **Authentication**: Flask-Login, Flask-WTF for CSRF protection
- **Installation**: Modular installer with multi-database support
- **Testing**: pytest, coverage, Selenium

## Project Structure

```
handyman-kpi-system/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints and views
│   │   ├── static/         # CSS, JS, images
│   │   ├── templates/      # HTML templates
│   │   ├── middleware/     # Application middleware (access control)
│   │   ├── utils/          # Utility functions
│   │   └── __init__.py     # Application initialization
│   └── run.py              # Application entry point
├── database/
│   ├── schema.sql          # Database schema
│   ├── migrate_auth.py     # Authentication migration script
│   └── init_data.sql       # Initial data
├── installer/
│   ├── core/               # Core installer functionality
│   ├── platforms/          # Platform-specific extensions
│   │   ├── windows/        # Windows-specific components
│   │   └── docker/         # Docker-specific components (future)
│   ├── shared/             # Shared resources
│   │   ├── database/       # Database adapters and schemas
│   │   └── utils/          # Shared utilities
│   └── build/              # Build scripts
├── docs/                   # Documentation
├── tests/                  # Test suite
│   ├── unit/               # Unit tests for models
│   ├── integration/        # Integration tests for routes
│   ├── ui/                 # UI tests with Selenium
│   ├── conftest.py         # Test configuration
│   └── run_tests.py        # Test runner script
└── scripts/                # Utility scripts
```

## Reporting Module

The system provides four main report types:

1. **Employee Performance Report**: Individual employee evaluations for performance reviews
2. **Team Performance Report**: Comparative analysis across employees
3. **Skills Analysis Report**: Deep dive into skill distribution
4. **Tool Inventory Report**: Tool proficiency and ownership tracking

Reports can be exported as PDF documents or Excel spreadsheets for further analysis.

## Authentication System

The system implements a comprehensive authentication system with the following features:

- **User Authentication**: Secure login/logout with session management
- **Role-Based Access Control**: Three permission levels
  - **Admin**: Full system access including user management
  - **Manager**: Access to all employees and reporting
  - **Employee**: Limited access to personal data and evaluations
- **Security Features**:
  - Password hashing with Werkzeug
  - CSRF protection with Flask-WTF
  - Rate limiting for login attempts
  - Secure password reset mechanism
  - Force password change functionality

## Installation System

The system features a modular installer architecture with support for multiple installation methods:

- **Windows Installer**: GUI-based setup wizard
- **Docker Deployment**: Container-based installation (coming soon)
- **Source Installation**: Manual installation from source code

### Database Support

The installer supports multiple database backends:

- **SQLite**: Recommended for single-user deployments
- **MySQL**: For multi-user deployments with moderate load
- **PostgreSQL**: For high-performance production environments

The modular adapter system allows each database type to use optimized schemas and configurations while maintaining a consistent API.

## Testing

The system includes a comprehensive testing framework with multiple layers of tests:

### Unit Tests
- Tests for individual models and components
- Validation of business rules and constraints
- Comprehensive validation of model relationships
- Database adapter and initializer testing

### Integration Tests
- Tests for authentication routes and user management
- Employee and evaluation management workflow testing
- Dashboard and reporting functionality verification
- Database migration testing

### UI Tests
- Selenium-based tests for frontend components
- Responsive design verification
- Form validation testing
- Dynamic component interaction testing

### Running Tests
Tests can be run using the included test runner script:

```
python tests/run_tests.py
```

For detailed coverage reports:

```
python tests/run_tests.py --cov
```

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment tool (optional but recommended)

### Setup
1. Clone the repository
   ```
   git clone https://github.com/skunkbandit/handyman-kpi-system.git
   cd handyman-kpi-system
   ```

2. Create and activate a virtual environment (optional)
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database
   ```
   python scripts/init_database.py
   ```

5. Run the application
   ```
   python backend/run.py
   ```

6. Open a web browser and navigate to `http://localhost:5000`

## Usage

Detailed usage instructions and admin documentation are available in the [User Guide](docs/user_guide.md).

## License

[MIT License](LICENSE)

## Contact

For support or questions, please open an issue on this repository.
