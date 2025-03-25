"""
Windows-specific environment management for the Handyman KPI System Installer.

This module provides classes and functions for managing the Windows environment,
including registry access, shortcuts, and system integration.
"""

import os
import sys
import subprocess
import winreg
from typing import List, Dict, Optional, Tuple, Any

from ...core.environment import Environment as BaseEnvironment


class WindowsEnvironment(BaseEnvironment):
    """Windows-specific environment setup and validation."""
    
    @staticmethod
    def get_app_directory() -> str:
        """Get the application directory on Windows.
        
        Returns:
            str: Application directory
        """
        # If running as a bundled executable (frozen)
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        
        # If running from source code
        # Navigate up from installer/platforms/windows to the application root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        platforms_dir = os.path.dirname(current_dir)
        installer_dir = os.path.dirname(platforms_dir)
        return os.path.dirname(installer_dir)
    
    @staticmethod
    def get_program_files_directory() -> str:
        """Get the Program Files directory.
        
        Returns:
            str: Program Files directory
        """
        return os.environ.get('ProgramFiles', r'C:\Program Files')
    
    @staticmethod
    def get_appdata_directory() -> str:
        """Get the AppData directory.
        
        Returns:
            str: AppData directory
        """
        return os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
    
    @staticmethod
    def get_localappdata_directory() -> str:
        """Get the Local AppData directory.
        
        Returns:
            str: Local AppData directory
        """
        return os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    
    @staticmethod
    def get_desktop_directory() -> str:
        """Get the Desktop directory.
        
        Returns:
            str: Desktop directory
        """
        return os.path.join(os.path.expanduser('~'), 'Desktop')
    
    @staticmethod
    def get_start_menu_directory() -> str:
        """Get the Start Menu Programs directory.
        
        Returns:
            str: Start Menu Programs directory
        """
        return os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')),
            'Microsoft\\Windows\\Start Menu\\Programs'
        )
    
    @staticmethod
    def get_data_directory() -> str:
        """Get the data directory for the application.
        
        Returns:
            str: Data directory
        """
        app_dir = WindowsEnvironment.get_app_directory()
        return os.path.join(app_dir, 'data')
    
    @staticmethod
    def get_config_directory() -> str:
        """Get the configuration directory for the application.
        
        Returns:
            str: Configuration directory
        """
        app_dir = WindowsEnvironment.get_app_directory()
        return os.path.join(app_dir, 'config')
    
    @staticmethod
    def get_log_directory() -> str:
        """Get the log directory for the application.
        
        Returns:
            str: Log directory
        """
        app_dir = WindowsEnvironment.get_app_directory()
        return os.path.join(app_dir, 'logs')
    
    @staticmethod
    def is_admin() -> bool:
        """Check if the current user has administrator privileges.
        
        Returns:
            bool: True if the user has administrator privileges, False otherwise
        """
        try:
            # Check for administrator privileges
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    @staticmethod
    def create_desktop_shortcut(target_path: str, shortcut_name: str, 
                               description: str = "", icon_path: Optional[str] = None,
                               arguments: str = "") -> bool:
        """Create a desktop shortcut on Windows.
        
        Args:
            target_path: Path to the target executable
            shortcut_name: Name of the shortcut
            description: Description of the shortcut
            icon_path: Path to the icon file, or None to use the target's icon
            arguments: Command-line arguments for the target
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            desktop = WindowsEnvironment.get_desktop_directory()
            shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
            
            # Use Windows Script Host to create the shortcut
            ps_script = f"""
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{target_path}"
            $Shortcut.WorkingDirectory = "{os.path.dirname(target_path)}"
            $Shortcut.Description = "{description}"
            """
            
            if arguments:
                ps_script += f'$Shortcut.Arguments = "{arguments}"\n'
            
            if icon_path:
                ps_script += f'$Shortcut.IconLocation = "{icon_path}"\n'
            
            ps_script += '$Shortcut.Save()\n'
            
            # Execute PowerShell script
            subprocess.run(["powershell", "-Command", ps_script], check=True)
            
            return os.path.exists(shortcut_path)
        
        except Exception:
            return False
    
    @staticmethod
    def create_start_menu_shortcut(target_path: str, shortcut_name: str, 
                                  folder: Optional[str] = None,
                                  description: str = "", icon_path: Optional[str] = None,
                                  arguments: str = "") -> bool:
        """Create a Start Menu shortcut on Windows.
        
        Args:
            target_path: Path to the target executable
            shortcut_name: Name of the shortcut
            folder: Folder in Start Menu, or None for root
            description: Description of the shortcut
            icon_path: Path to the icon file, or None to use the target's icon
            arguments: Command-line arguments for the target
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            start_menu = WindowsEnvironment.get_start_menu_directory()
            
            if folder:
                start_menu = os.path.join(start_menu, folder)
                os.makedirs(start_menu, exist_ok=True)
            
            shortcut_path = os.path.join(start_menu, f"{shortcut_name}.lnk")
            
            # Use Windows Script Host to create the shortcut
            ps_script = f"""
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{target_path}"
            $Shortcut.WorkingDirectory = "{os.path.dirname(target_path)}"
            $Shortcut.Description = "{description}"
            """
            
            if arguments:
                ps_script += f'$Shortcut.Arguments = "{arguments}"\n'
            
            if icon_path:
                ps_script += f'$Shortcut.IconLocation = "{icon_path}"\n'
            
            ps_script += '$Shortcut.Save()\n'
            
            # Execute PowerShell script
            subprocess.run(["powershell", "-Command", ps_script], check=True)
            
            return os.path.exists(shortcut_path)
        
        except Exception:
            return False
    
    @staticmethod
    def create_registry_entry(key: str, name: str, value: str, value_type: str = "REG_SZ") -> bool:
        """Create a registry entry on Windows.
        
        Args:
            key: Registry key (e.g., 'HKEY_CURRENT_USER\\Software\\MyApp')
            name: Name of the registry value
            value: Value to set
            value_type: Type of the registry value (REG_SZ, REG_DWORD, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Parse registry key
            root_key_str, subkey = key.split('\\', 1)
            
            # Map root key string to registry key
            root_key_map = {
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKCR': winreg.HKEY_CLASSES_ROOT,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKCU': winreg.HKEY_CURRENT_USER,
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKLM': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKU': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
                'HKCC': winreg.HKEY_CURRENT_CONFIG
            }
            
            root_key = root_key_map.get(root_key_str)
            if not root_key:
                raise ValueError(f"Invalid registry root key: {root_key_str}")
            
            # Create or open registry key
            reg_key = winreg.CreateKey(root_key, subkey)
            
            # Set value based on type
            if value_type == "REG_SZ":
                winreg.SetValueEx(reg_key, name, 0, winreg.REG_SZ, value)
            elif value_type == "REG_DWORD":
                winreg.SetValueEx(reg_key, name, 0, winreg.REG_DWORD, int(value))
            elif value_type == "REG_BINARY":
                winreg.SetValueEx(reg_key, name, 0, winreg.REG_BINARY, bytes.fromhex(value))
            elif value_type == "REG_EXPAND_SZ":
                winreg.SetValueEx(reg_key, name, 0, winreg.REG_EXPAND_SZ, value)
            elif value_type == "REG_MULTI_SZ":
                winreg.SetValueEx(reg_key, name, 0, winreg.REG_MULTI_SZ, value.split('|'))
            else:
                raise ValueError(f"Unsupported registry value type: {value_type}")
            
            # Close key
            winreg.CloseKey(reg_key)
            
            return True
        
        except Exception:
            return False
    
    @staticmethod
    def get_registry_value(key: str, name: str) -> Optional[Any]:
        """Get a registry value on Windows.
        
        Args:
            key: Registry key (e.g., 'HKEY_CURRENT_USER\\Software\\MyApp')
            name: Name of the registry value
            
        Returns:
            Optional[Any]: Registry value or None if not found
        """
        try:
            # Parse registry key
            root_key_str, subkey = key.split('\\', 1)
            
            # Map root key string to registry key
            root_key_map = {
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKCR': winreg.HKEY_CLASSES_ROOT,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKCU': winreg.HKEY_CURRENT_USER,
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKLM': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKU': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
                'HKCC': winreg.HKEY_CURRENT_CONFIG
            }
            
            root_key = root_key_map.get(root_key_str)
            if not root_key:
                raise ValueError(f"Invalid registry root key: {root_key_str}")
            
            # Open registry key
            reg_key = winreg.OpenKey(root_key, subkey)
            
            # Get value
            value, value_type = winreg.QueryValueEx(reg_key, name)
            
            # Close key
            winreg.CloseKey(reg_key)
            
            return value
        
        except Exception:
            return None
    
    @staticmethod
    def setup_environment() -> bool:
        """Set up the Windows environment for the application.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Set current directory to app directory
            app_dir = WindowsEnvironment.get_app_directory()
            os.chdir(app_dir)
            
            # Create necessary directories
            data_dir = WindowsEnvironment.get_data_directory()
            config_dir = WindowsEnvironment.get_config_directory()
            log_dir = WindowsEnvironment.get_log_directory()
            
            os.makedirs(data_dir, exist_ok=True)
            os.makedirs(config_dir, exist_ok=True)
            os.makedirs(log_dir, exist_ok=True)
            
            # Add app directory to PATH if not already there
            path_env = os.environ.get('PATH', '')
            
            if app_dir not in path_env.split(os.pathsep):
                os.environ['PATH'] = app_dir + os.pathsep + path_env
            
            return True
        
        except Exception:
            return False