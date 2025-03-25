## Build System Modules

### `installer.build.builder_base`

**Purpose**: Provides base functionality for installer builders.

**Classes**:
- `BuilderBase`: Abstract base class for installer builders
  - `__init__(config_manager)`: Initializes with configuration manager
  - `prepare_build_directory()`: Prepares build directory
  - `copy_source_files()`: Copies source files to build directory
  - `create_configuration()`: Creates configuration files
  - `build()`: Executes the build process
  - `clean()`: Cleans up temporary files

**Example Usage**:
```python
from installer.build.builder_base import BuilderBase

class CustomBuilder(BuilderBase):
    def build(self):
        self.prepare_build_directory()
        self.copy_source_files()
        self.create_configuration()
        # Custom build steps
        self.clean()
```

### `installer.build.windows_builder`

**Purpose**: Implements Windows-specific installer builder.

**Classes**:
- `WindowsBuilder`: Builder for Windows installers
  - `__init__(config_manager)`: Initializes with configuration manager
  - `prepare_inno_setup()`: Prepares Inno Setup script
  - `run_inno_compiler()`: Runs Inno Setup compiler
  - `create_windows_shortcuts()`: Creates shortcut definitions
  - `sign_installer()`: Signs the installer executable (if certificate available)

**Example Usage**:
```python
from installer.build.windows_builder import WindowsBuilder
from installer.core.config_manager import ConfigManager

config = ConfigManager('build_config.json')
builder = WindowsBuilder(config)
result = builder.build()

if result.success:
    print(f"Installer created at: {result.output_file}")
else:
    print(f"Build failed: {result.error}")
```

### `installer.build.installer_packager`

**Purpose**: Packages installer components into different formats.

**Classes**:
- `InstallerPackager`: Handles packaging installer components
  - `__init__(config_manager)`: Initializes with configuration manager
  - `package_exe()`: Creates executable installer
  - `package_zip()`: Creates ZIP package
  - `package_msi()`: Creates MSI package (Windows only)

**Example Usage**:
```python
from installer.build.installer_packager import InstallerPackager
from installer.core.config_manager import ConfigManager

config = ConfigManager('package_config.json')
packager = InstallerPackager(config)

# Create different package formats
exe_path = packager.package_exe()
zip_path = packager.package_zip()
msi_path = packager.package_msi()  # Windows only
```

### `installer.build.assets.resource_compiler`

**Purpose**: Compiles resources for inclusion in the installer.

**Classes**:
- `ResourceCompiler`: Compiles and processes resources
  - `__init__(resource_dir, output_dir)`: Initializes with resource directory
  - `compile_images()`: Processes and optimizes images
  - `compile_icons()`: Processes icon files
  - `bundle_resources()`: Bundles resources for inclusion

**Example Usage**:
```python
from installer.build.assets.resource_compiler import ResourceCompiler

compiler = ResourceCompiler("resources", "build/resources")
compiler.compile_images()
compiler.compile_icons()
compiler.bundle_resources()
```

### `installer.build.dependency_manager`

**Purpose**: Manages dependencies for inclusion in the installer.

**Classes**:
- `DependencyManager`: Handles project dependencies
  - `__init__(config_manager)`: Initializes with configuration manager
  - `collect_dependencies()`: Collects required dependencies
  - `download_dependency(name, version)`: Downloads a dependency
  - `verify_dependency(path)`: Verifies dependency integrity
  - `bundle_dependencies()`: Bundles dependencies for inclusion

**Example Usage**:
```python
from installer.build.dependency_manager import DependencyManager
from installer.core.config_manager import ConfigManager

config = ConfigManager()
deps = DependencyManager(config)
deps.collect_dependencies()

# Download specific dependency if needed
deps.download_dependency("requests", "2.25.0")

# Bundle all dependencies
deps.bundle_dependencies()
```

### `installer.build.version_manager`

**Purpose**: Manages version information for the installer.

**Classes**:
- `VersionManager`: Handles versioning for installer builds
  - `__init__(config_manager)`: Initializes with configuration manager
  - `get_current_version()`: Gets current version information
  - `increment_version(level='patch')`: Increments version number
  - `set_version(version)`: Sets specific version
  - `update_version_files()`: Updates version information in files

**Example Usage**:
```python
from installer.build.version_manager import VersionManager
from installer.core.config_manager import ConfigManager

config = ConfigManager()
version = VersionManager(config)

# Get current version
current = version.get_current_version()
print(f"Current version: {current}")

# Increment for new build
version.increment_version('minor')  # Increases middle number
version.update_version_files()
```
