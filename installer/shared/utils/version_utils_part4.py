"""
Version and Platform Utilities for the KPI System Installer (Part 4)

Environment compatibility checking utilities.
"""

import platform

from .logging_utils import get_logger
from .error_utils import InstallerError, ErrorSeverity

logger = get_logger(__name__)


def check_environment_compatibility():
    """
    Check if the current environment is compatible with the KPI System.
    
    Returns:
        tuple: (is_compatible, issues) where issues is a list of compatibility issues
    """
    try:
        from .version_utils import is_windows, is_64bit, check_python_version, format_version, get_python_version, get_os_info, is_linux, is_macos
        from .version_utils_part2 import check_dependency_installed, get_dependency_version
        
        issues = []
        
        # Check Python version
        if not check_python_version(min_version=(3, 8), max_version=(3, 11)):
            current = get_python_version()
            issues.append(f"Python version {format_version(current)} is not supported. Version 3.8 to 3.11 is required.")
            
        # Check operating system
        os_info = get_os_info()
        if os_info['system'] not in ('Windows', 'Linux', 'Darwin'):
            issues.append(f"Operating system {os_info['system']} is not supported. Windows, Linux, or macOS is required.")
            
        # Windows-specific checks
        if is_windows():
            # Check Windows version
            try:
                win_version = float(f"{os_info['release']}")
                if win_version < 10:
                    issues.append(f"Windows version {os_info['release']} is not supported. Windows 10 or later is required.")
            except:
                logger.warning(f"Could not determine Windows version from release string: {os_info['release']}")
                
        # Linux-specific checks
        elif is_linux():
            # Example: Check for systemd
            if not check_dependency_installed('systemctl'):
                issues.append("systemd is not available, which is required for service management on Linux.")
                
        # macOS-specific checks
        elif is_macos():
            try:
                mac_version = float('.'.join(os_info['release'].split('.')[:2]))
                if mac_version < 10.14:
                    issues.append(f"macOS version {os_info['release']} is not supported. macOS 10.14 or later is required.")
            except:
                logger.warning(f"Could not determine macOS version from release string: {os_info['release']}")
                
        # Architecture checks
        if not is_64bit():
            issues.append("32-bit systems are not supported. 64-bit operating system is required.")
            
        # Check for required dependencies
        dependencies = []
        
        if is_windows():
            dependencies.append(('Inno Setup', 'iscc', '--version', r'(\d+\.\d+(\.\d+)?)'))
        else:
            dependencies.append(('PostgreSQL Client', 'psql', '--version', r'psql \(PostgreSQL\) (\d+\.\d+(\.\d+)?)'))
            
        for dep_name, dep_exe, version_arg, version_regex in dependencies:
            if not check_dependency_installed(dep_exe):
                issues.append(f"{dep_name} is not installed or not in PATH.")
            else:
                version_str = get_dependency_version(dep_exe, version_arg, version_regex)
                if version_str is None:
                    issues.append(f"Failed to determine version of {dep_name}.")
                    
        # Return compatibility result
        is_compatible = len(issues) == 0
        return is_compatible, issues
        
    except Exception as e:
        logger.error(f"Error checking environment compatibility: {e}")
        return False, [f"Error checking environment compatibility: {str(e)}"]


def get_compatibility_report():
    """
    Generate a detailed compatibility report for the current environment.
    
    Returns:
        dict: Compatibility report with system information and issues
    """
    try:
        from .version_utils import get_os_info, get_python_version, format_version, is_windows, is_linux, is_macos, is_64bit
        from .version_utils_part2 import check_admin_privileges
        from .version_utils_part3 import get_application_version, get_installer_version
        
        # Get basic environment information
        os_info = get_os_info()
        python_version = format_version(get_python_version())
        
        # Check compatibility
        is_compatible, issues = check_environment_compatibility()
        
        # Build the report
        report = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'environment': {
                'os': {
                    'system': os_info['system'],
                    'release': os_info['release'],
                    'version': os_info['version'],
                    'architecture': os_info['machine'],
                    'is_64bit': is_64bit()
                },
                'python': {
                    'version': python_version,
                    'executable': __import__('sys').executable,
                    'path': __import__('sys').path,
                },
                'user': {
                    'admin_privileges': check_admin_privileges(),
                    'home_directory': str(__import__('pathlib').Path.home()),
                    'temp_directory': __import__('tempfile').gettempdir()
                }
            },
            'application': {
                'app_version': get_application_version(),
                'installer_version': get_installer_version()
            },
            'compatibility': {
                'is_compatible': is_compatible,
                'issues': issues
            }
        }
        
        # Add platform-specific information
        if is_windows():
            try:
                import winreg
                report['environment']['os']['windows'] = {
                    'edition': os_info.get('edition', 'Unknown'),
                    'product_id': __import__('subprocess').check_output('wmic os get serialnumber').decode().strip().split('\n')[-1]
                }
            except:
                report['environment']['os']['windows'] = {
                    'edition': os_info.get('edition', 'Unknown')
                }
                
        elif is_linux():
            try:
                report['environment']['os']['linux'] = {
                    'distribution': os_info.get('distribution', 'Unknown'),
                    'distribution_version': os_info.get('distribution_version', 'Unknown')
                }
            except:
                pass
                
        elif is_macos():
            try:
                report['environment']['os']['macos'] = {
                    'product_version': __import__('subprocess').check_output(['sw_vers', '-productVersion']).decode().strip()
                }
            except:
                pass
                
        return report
        
    except Exception as e:
        logger.error(f"Error generating compatibility report: {e}")
        return {
            'error': str(e),
            'compatibility': {
                'is_compatible': False,
                'issues': [f"Error generating compatibility report: {str(e)}"]
            }
        }
