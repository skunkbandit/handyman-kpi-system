# Windows Builder Module Reference

This document provides a detailed reference for the Windows Builder module used in the Handyman KPI System installer.

## Overview

The `WindowsBuilder` class is responsible for generating Windows installers for the Handyman KPI System. It handles:

- Creating a temporary build environment
- Downloading and setting up an embedded Python distribution
- Cloning the repository and installing dependencies
- Generating an Inno Setup script and compiling the installer

## Module Location

```
installer/build/windows.py
```

## Class Reference

### WindowsBuilder

```python
class WindowsBuilder:
    """Build script for creating Windows installer."""
    
    def __init__(self, repo_url: str, version: str, output_dir: Optional[str] = None):
        """Initialize Windows builder."""
```

#### Constructor Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `repo_url` | `str` | URL of the GitHub repository to clone | Required |
| `version` | `str` | Version number for the installer | Required |
| `output_dir` | `Optional[str]` | Output directory for the installer | `../dist` |

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `repo_url` | `str` | URL of the GitHub repository |
| `version` | `str` | Version number for the installer |
| `output_dir` | `str` | Output directory for the installer |
| `temp_dir` | `str` | Temporary directory for building the installer |
| `python_dir` | `str` | Directory for the embedded Python distribution |
| `app_dir` | `str` | Directory for the application files |
| `installer_dir` | `str` | Directory for the installer files |

#### Methods

##### __del__

```python
def __del__(self):
    """Clean up temporary directory on deletion."""
```

Cleans up the temporary directory when the WindowsBuilder instance is deleted.

##### create_directories

```python
def create_directories(self):
    """Create necessary directories."""
```

Creates all necessary directories for the build process:
- Temporary directory
- Python distribution directory
- Application files directory
- Installer files directory
- Output directory

##### download_python

```python
def download_python(self):
    """Download embedded Python distribution."""
```

Downloads and extracts the embedded Python distribution:
1. Downloads the Python 3.10 embedded distribution
2. Extracts it to the temporary Python directory
3. Downloads and installs pip
4. Configures the embedded Python to use site-packages

##### clone_repository

```python
def clone_repository(self):
    """Clone the repository."""
```

Clones the GitHub repository to the application directory.

##### install_dependencies

```python
def install_dependencies(self):
    """Install Python dependencies."""
```

Installs the required Python dependencies from the repository's requirements.txt file.

##### build_inno_setup

```python
def build_inno_setup(self):
    """Build the installer using Inno Setup."""
```

Builds the installer using Inno Setup:
1. Copies the Inno Setup template
2. Replaces placeholders with actual values
3. Runs the Inno Setup compiler

##### _find_inno_setup

```python
def _find_inno_setup(self) -> Optional[str]:
    """Find Inno Setup compiler."""
```

Searches for the Inno Setup compiler (ISCC.exe) in common installation locations.

**Returns:**
- Path to the Inno Setup compiler, or None if not found

##### build

```python
def build(self) -> str:
    """Build the Windows installer."""
```

Main method to build the Windows installer. It performs all necessary steps:
1. Creates directories
2. Downloads Python
3. Clones the repository
4. Installs dependencies
5. Builds the Inno Setup installer

**Returns:**
- Path to the created installer

## Usage Examples

### Basic Usage

```python
from installer.build.windows import WindowsBuilder

# Create a builder instance
builder = WindowsBuilder(
    repo_url="https://github.com/skunkbandit/handyman-kpi-system",
    version="1.0.0"
)

# Build the installer
installer_path = builder.build()
print(f"Installer created: {installer_path}")
```

### Specifying Output Directory

```python
from installer.build.windows import WindowsBuilder

# Create a builder instance with custom output directory
builder = WindowsBuilder(
    repo_url="https://github.com/skunkbandit/handyman-kpi-system",
    version="1.0.0",
    output_dir="C:/Users/dtest/KPI Project/dist"
)

# Build the installer
installer_path = builder.build()
print(f"Installer created: {installer_path}")
```

## Error Handling

The `WindowsBuilder` class throws exceptions in the following cases:

- **RuntimeError**: "Inno Setup Compiler (ISCC) not found"
  - When the Inno Setup compiler cannot be found
  
- **RuntimeError**: "Installer not found in output directory"
  - When the installer is not created after running the Inno Setup compiler

- **subprocess.CalledProcessError**:
  - When any subprocess call (downloading Python, cloning repository, etc.) fails

- **IOError**, **OSError**, or **PermissionError**:
  - When file operations fail (e.g., creating directories, copying files)

## Dependencies

The WindowsBuilder depends on the following external tools:

- **Inno Setup 6+**: Must be installed on the system
- **Git**: For cloning the repository
- **PowerShell**: For downloading files and extracting archives

## Integration with Other Modules

The WindowsBuilder is typically used by:

- **__main__.py**: Main entry point for the installer
- **test_windows_builder.py**: Tests for the WindowsBuilder

## Best Practices

1. **Error Handling**: Always wrap the `build()` method in a try-except block to handle potential errors
2. **Cleanup**: The WindowsBuilder automatically cleans up temporary files when deleted, but it's a good practice to explicitly call `del builder` after use
3. **Testing**: Run the tests in `test_windows_builder.py` after making any changes to ensure functionality
4. **Customization**: To customize the installer, modify the Inno Setup template rather than the WindowsBuilder code

## Notes and Limitations

- Requires Inno Setup 6 or later to be installed
- Currently only supports Windows platforms
- Uses a fixed Python version (3.10.11) for the embedded distribution
- Requires an internet connection to download the Python distribution and clone the repository
