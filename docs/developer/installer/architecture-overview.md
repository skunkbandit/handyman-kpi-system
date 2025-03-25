# Handyman KPI System Installer Architecture Overview

This document provides a high-level overview of the modular installer architecture for the Handyman KPI System.

## Design Principles

The installer architecture is built around the following principles:

1. **Modularity**: Components are designed to be self-contained with clear interfaces
2. **Platform Independence**: Core functionality is separated from platform-specific implementation
3. **Extensibility**: New platforms and features can be added without modifying existing code
4. **Maintainability**: Common functionality is centralized to reduce duplication
5. **Testability**: Components are designed to be easily testable in isolation

## Architecture Layers

The installer is organized into four main layers:

1. **Core Layer**: Platform-agnostic core functionality
2. **Platform Layer**: Platform-specific implementations
3. **Shared Layer**: Common utilities and resources
4. **Build Layer**: Tools for generating installers

### Core Layer

The Core Layer provides the foundation of the installer and includes platform-agnostic functionality:

- **Configuration Management**: Handles reading, validating, and writing configuration
- **Database Management**: Manages database initialization and schema updates
- **Environment Management**: Manages environment setup and validation
- **Verification**: Verifies the installation process

### Platform Layer

The Platform Layer contains platform-specific implementations:

- **Windows**: Windows-specific components
  - **GUI**: Windows GUI components for setup wizard
  - **Inno**: Inno Setup integration
  - **Environment**: Windows environment handling
- **Future Platforms**: Space for additional platforms (Linux, macOS, etc.)

### Shared Layer

The Shared Layer contains utilities and resources used across the installer:

- **Database Adapters**: Database-specific adapters (SQLite, MySQL, PostgreSQL)
- **Configuration Templates**: Default configuration templates
- **Utilities**: Shared utility functions for logging, error handling, etc.

### Build Layer

The Build Layer contains tools for generating installers:

- **Windows Builder**: Builds a Windows installer package
- **Future Builders**: Space for additional builders (Docker, etc.)

## Component Diagram

```
                    ┌────────────────────────────────────────┐
                    │           Entry Point (__main__)        │
                    └───────────────────┬────────────────────┘
                                        │
                    ┌───────────────────▼────────────────────┐
                    │                Core Layer               │
                    │  ┌───────────┐ ┌──────────┐ ┌────────┐ │
                    │  │  Config   │ │ Database │ │  Env   │ │
                    │  └───────────┘ └──────────┘ └────────┘ │
                    └───────────────────┬────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
┌───────▼───────┐             ┌─────────▼─────────┐           ┌─────────▼─────────┐
│ Platform Layer │             │    Shared Layer   │           │    Build Layer    │
│   ┌─────────┐  │             │  ┌─────────────┐  │           │   ┌────────────┐  │
│   │ Windows │  │             │  │   Database  │  │           │   │  Windows   │  │
│   │  ┌─────┐│  │             │  │   Adapters  │  │           │   │  Builder   │  │
│   │  │ GUI ││  │◄────────────┼──┼─►           │  │◄──────────┼───┼►           │  │
│   │  └─────┘│  │             │  └─────────────┘  │           │   └────────────┘  │
│   │  ┌─────┐│  │             │  ┌─────────────┐  │           │                   │
│   │  │Inno ││  │◄────────────┼──┼─► Config    │  │           │                   │
│   │  └─────┘│  │             │  │ Templates   │  │           │                   │
│   └─────────┘  │             │  └─────────────┘  │           │                   │
└───────────────┘             └───────────────────┘           └───────────────────┘
```

## Key Components

### Core Components

#### InstallerConfig

The `InstallerConfig` class manages installer configuration:

- Reads configuration from files, command line, or environment variables
- Validates configuration values
- Provides default values where appropriate
- Handles platform-specific configuration

#### DatabaseManager

The `DatabaseManager` class manages database operations:

- Initializes the database with the appropriate schema
- Handles database upgrades
- Verifies database connection and permissions
- Provides adapters for different database types

#### EnvironmentManager

The `EnvironmentManager` class manages environment setup:

- Verifies system requirements
- Sets up required directories
- Configures environment variables
- Checks dependencies

### Platform Components

#### Windows Components

##### SetupWizard

The `SetupWizard` class provides a graphical interface for Windows installation:

- Collects user input for installation options
- Validates input values
- Guides users through the installation process
- Provides feedback on installation progress

##### InnoSetup

The `InnoSetup` module handles integration with Inno Setup:

- Generates Inno Setup scripts from templates
- Processes configuration variables
- Executes the Inno Setup compiler
- Customizes installer appearance and behavior

### Shared Components

#### Database Adapters

Database adapters provide database-specific functionality:

- `SQLiteAdapter`: For SQLite databases
- `MySQLAdapter`: For MySQL databases
- `PostgreSQLAdapter`: For PostgreSQL databases

Each adapter implements a common interface defined by the `BaseDatabaseAdapter` class.

#### Configuration Templates

Configuration templates provide default configurations for different scenarios:

- `default_config.ini`: Default configuration template
- Additional templates for specific deployment scenarios

#### Utility Modules

Utility modules provide common functionality:

- `logging_utils.py`: Logging utilities
- `error_utils.py`: Error handling utilities
- `file_utils.py`: File system utilities
- `config_utils.py`: Configuration validation utilities
- `version_utils.py`: Version checking utilities

### Build Components

#### WindowsBuilder

The `WindowsBuilder` class builds Windows installers:

- Creates a temporary build environment
- Downloads and sets up an embedded Python distribution
- Clones the repository and installs dependencies
- Generates an Inno Setup script and compiles the installer

## Module Structure

```
installer/
├── build/                  # Build system tools
│   ├── windows.py             # Windows installer builder
│   └── __init__.py
├── core/                   # Core installer components
│   ├── config.py              # Configuration management
│   ├── database.py            # Database initialization
│   ├── environment.py         # Environment setup
│   ├── verification.py        # Installation verification
│   └── __init__.py
├── platforms/              # Platform-specific components
│   ├── windows/            # Windows-specific components
│   │   ├── environment.py     # Windows environment handler
│   │   ├── gui/               # Windows GUI components
│   │   │   ├── setup_wizard.py  # Setup wizard
│   │   │   ├── setup_wizard_integrated.py  # Integrated wizard
│   │   │   └── __init__.py
│   │   ├── inno/              # Inno Setup specific files
│   │   │   └── installer.iss  # Inno Setup script template
│   │   ├── scripts/           # Windows-specific scripts
│   │   └── __init__.py
│   └── __init__.py
├── shared/                 # Shared resources and utilities
│   ├── database/              # Database initialization and migration
│   │   ├── adapters/          # Database adapters
│   │   │   ├── base.py        # Base adapter class
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
│   │   ├── logging_utils.py   # Logging utilities
│   │   ├── error_utils.py     # Error handling utilities
│   │   ├── file_utils.py      # File system utilities
│   │   ├── config_utils.py    # Configuration validation utilities
│   │   ├── version_utils.py   # Version checking utilities
│   │   └── __init__.py
│   └── __init__.py
├── __main__.py             # Main entry point
└── __init__.py             # Package initialization
```

## Control Flow

### Installation Process

1. User runs the installer module with appropriate arguments
2. The `__main__.py` module parses arguments and creates an `InstallerConfig` instance
3. Based on the command, the appropriate component is invoked
   - For `wizard`: The setup wizard is launched
   - For `windows`: The Windows builder is invoked
   - For other commands: The appropriate handler is invoked
4. The component performs its task and returns a result
5. The `__main__.py` module handles the result and exits with an appropriate code

### Wizard Flow

1. User launches the setup wizard
2. The wizard displays a welcome screen
3. The wizard guides the user through configuration screens
   - Database selection and configuration
   - Installation path selection
   - Component selection
   - Additional options
4. The wizard validates user input at each step
5. After collecting all necessary information, the wizard performs the installation
6. The wizard displays a completion screen

### Build Process

1. User invokes the builder with appropriate arguments
2. The builder creates a temporary build environment
3. The builder downloads and sets up an embedded Python distribution
4. The builder clones the repository and installs dependencies
5. The builder generates an Inno Setup script and compiles the installer
6. The builder returns the path to the created installer

## Extension Points

The architecture provides several extension points for future enhancements:

1. **New Platform Support**
   - Add a new directory under `platforms/` for the new platform
   - Implement platform-specific components
   - Update the main entry point to handle the new platform

2. **New Database Adapters**
   - Add a new adapter class under `shared/database/adapters/`
   - Implement the interface defined by `BaseDatabaseAdapter`
   - Update the database manager to use the new adapter

3. **New Builder Tools**
   - Add a new builder class under `build/`
   - Implement the builder interface
   - Update the main entry point to handle the new builder

4. **New Configuration Templates**
   - Add a new template file under `shared/config_templates/`
   - Update the configuration manager to use the new template

## Future Enhancements

Planned future enhancements include:

1. **Docker Support**
   - Add Docker-specific components under `platforms/docker/`
   - Implement a Docker builder under `build/`

2. **Linux Support**
   - Add Linux-specific components under `platforms/linux/`
   - Implement a Linux builder under `build/`

3. **macOS Support**
   - Add macOS-specific components under `platforms/macos/`
   - Implement a macOS builder under `build/`

4. **Enhanced Testing**
   - Add more comprehensive test coverage
   - Implement continuous integration testing

5. **Silent Installation Mode**
   - Add support for silent installation
   - Implement command-line options for unattended installation

## Conclusion

The modular installer architecture provides a flexible and extensible foundation for the Handyman KPI System installer. By separating core functionality from platform-specific implementation, the architecture enables support for multiple platforms while maintaining a consistent installation experience. The design promotes maintainability and testability, making it easier to add new features and fix issues in the future.
