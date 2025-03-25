# Handyman KPI System Modular Installer

This package provides a modular, platform-agnostic approach to installing the Handyman KPI System across different environments.

## Architecture

The installer is designed with a component-based architecture to maximize code reuse and minimize maintenance issues:

```
installer/
├── build/                  # Build system tools
│   ├── windows.py             # Windows installer builder
│   └── __init__.py
├── core/                   # Core installer components (platform-agnostic)
│   ├── config.py              # Configuration management
│   ├── database.py            # Database initialization
│   ├── environment.py         # Environment setup
│   ├── verification.py        # Installation verification
│   └── __init__.py
├── platforms/              # Platform-specific components
│   ├── windows/            # Windows-specific components
│   │   ├── environment.py     # Windows environment handler
│   │   ├── gui/               # Windows GUI components
│   │   │   ├── setup_wizard_integrated.py  # Main setup wizard
│   │   │   └── __init__.py
│   │   ├── inno/              # Inno Setup specific files
│   │   │   └── installer.iss  # Inno Setup script template
│   │   ├── scripts/           # Windows-specific scripts
│   │   └── __init__.py
│   └── __init__.py
├── shared/                 # Shared resources and utilities
│   ├── database/              # Database initialization and migration
│   │   ├── adapters/          # Database adapters
│   │   │   ├── sqlite.py      # SQLite adapter
│   │   │   ├── mysql.py       # MySQL adapter
│   │   │   ├── postgresql.py  # PostgreSQL adapter
│   │   │   └── __init__.py
│   │   ├── initializer.py     # Database initialization
│   │   ├── schema_sqlite.sql  # SQLite schema
│   │   ├── schema_mysql.sql   # MySQL schema
│   │   ├── schema_postgresql.sql # PostgreSQL schema
│   │   └── __init__.py
│   ├── config_templates/      # Configuration templates
│   │   └── default_config.ini # Default configuration
│   ├── utils/                 # Shared utilities
│   └── __init__.py
├── __main__.py             # Main entry point
├── test_database_adapters.py  # Database adapter tests
├── test_database_integration.py # Database integration tests
├── test_windows_builder.py   # Windows builder tests
└── __init__.py             # Package initialization
```

## Components

### Core Components

* **InstallerConfig**: Manages configuration across different installation methods
* **DatabaseManager**: Handles database initialization and management
* **EnvironmentManager**: Manages environment setup and validation
* **VerificationManager**: Verifies the installation process

### Build System

* **WindowsBuilder**: Builds a Windows installer package using Inno Setup

### Platform-Specific Components

* **WindowsEnvironment**: Handles Windows-specific environment setup
* **SetupWizard**: Graphical setup wizard for Windows installation
* **InnoSetup**: Contains Inno Setup specific files for building Windows installers

### Shared Components

* **Database Adapters**: Provides database-specific adapters
* **Database Initializer**: Initializes databases with correct schema
* **Configuration Templates**: Contains default configuration templates
* **Utilities**: Shared utility functions

## Usage

### Command-Line Usage

The installer can be run as a Python module with various commands:

```bash
# Launch the setup wizard (Windows)
python -m installer wizard --platform windows

# Build a Windows installer
python -m installer windows --version 1.0.0 --output-dir ./dist

# Run with a custom configuration file
python -m installer wizard --config ./my_config.ini
```

### Windows Installation

To create a Windows installer:

1. Ensure Inno Setup 6 or later is installed
2. Run the Windows builder:
   ```bash
   python -m installer windows --version 1.0.0
   ```
3. The installer will be created in the `dist` directory

### Database Configuration

The installer supports multiple database types:

- **SQLite**: Recommended for single-user deployments
- **MySQL**: For multi-user deployments
- **PostgreSQL**: For enterprise deployments

## Development

### Prerequisites

* Python 3.8 or higher
* Required Python packages: `sqlite3`, `tkinter` (for GUI components)
* Inno Setup 6 or later (for Windows installer)

### Installing for Development

1. Clone the repository:
   ```
   git clone https://github.com/skunkbandit/handyman-kpi-system.git
   ```

2. Navigate to the project directory:
   ```
   cd handyman-kpi-system
   ```

3. Install in development mode:
   ```
   pip install -e .
   ```

### Running Tests

To run the tests:

```bash
# Run database adapter tests
python -m installer.test_database_adapters

# Run database integration tests
python -m installer.test_database_integration

# Run Windows builder tests
python -m installer.test_windows_builder
```

## Status and Roadmap

### Current Status

- Core installer components are implemented
- Windows setup wizard is implemented
- Database initialization is functional
- Windows installer build system is implemented

### Roadmap

- Implement Docker image builder
- Add Linux installation support
- Add macOS installation support
- Enhance test coverage
- Implement silent installation mode

## License

See the LICENSE file for details.