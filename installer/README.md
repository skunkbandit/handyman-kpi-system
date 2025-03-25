# Handyman KPI System Modular Installer

This package provides a modular, platform-agnostic approach to installing the Handyman KPI System across different environments.

## Architecture

The installer is designed with a component-based architecture to maximize code reuse and minimize maintenance issues:

```
installer/
├── core/                  # Core installer components (platform-agnostic)
│   ├── config.py             # Configuration management
│   ├── database.py           # Database initialization
│   ├── environment.py        # Environment setup
│   ├── verification.py       # Installation verification
│   └── __init__.py
├── platforms/             # Platform-specific components
│   ├── windows/           # Windows-specific components
│   │   ├── environment.py    # Windows environment handler
│   │   ├── gui/              # Windows GUI components
│   │   ├── inno/             # Inno Setup specific files
│   │   ├── scripts/          # Windows-specific scripts
│   │   └── __init__.py
│   └── __init__.py
├── shared/                # Shared resources and utilities
│   ├── database/             # Database initialization and migration
│   │   ├── adapters/         # Database adapters
│   │   │   ├── sqlite.py     # SQLite adapter
│   │   │   ├── mysql.py      # MySQL adapter
│   │   │   ├── postgresql.py # PostgreSQL adapter
│   │   │   └── __init__.py
│   │   ├── schema_sqlite.sql # SQLite schema
│   │   ├── schema_mysql.sql  # MySQL schema
│   │   ├── schema_postgresql.sql # PostgreSQL schema
│   │   └── __init__.py
│   ├── config_templates/     # Configuration templates
│   ├── utils/                # Shared utilities
│   └── __init__.py
└── __init__.py           # Package initialization
```

## Components

### Core Components

* **ConfigManager**: Manages configuration across different installation methods
* **DatabaseManager**: Handles database initialization and management
* **EnvironmentManager**: Manages environment setup and validation
* **VerificationManager**: Verifies the installation process

### Platform-Specific Components

* **WindowsEnvironment**: Handles Windows-specific environment setup
* **WindowsGUI**: Provides GUI components for Windows installers
* **InnoSetup**: Contains Inno Setup specific files

### Shared Components

* **Database Adapters**: Provides database-specific adapters
* **Configuration Templates**: Contains default configuration templates
* **Utilities**: Shared utility functions

## Development

### Prerequisites

* Python 3.8 or higher
* Required Python packages: `sqlite3`, `tkinter` (for GUI components)

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

```
pytest tests/integration/installer
```

## Usage

### Basic Usage

```python
from installer import PlatformEnvironment, InstallerConfig, DatabaseInitializer

# Initialize environment
env = PlatformEnvironment()
env.setup_environment()

# Initialize configuration
config = InstallerConfig()

# Initialize database
db_init = DatabaseInitializer(config)
db_init.initialize_database()
```

## License

See the LICENSE file for details.
