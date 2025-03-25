"""
Windows build script for the Handyman KPI System Installer.

This module provides the WindowsBuilder class for creating a Windows installer
for the Handyman KPI System.
"""
import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Dict

class WindowsBuilder:
    """Build script for creating Windows installer."""
    
    def __init__(self, repo_url: str, version: str, output_dir: Optional[str] = None):
        """Initialize Windows builder.
        
        Args:
            repo_url: URL of the GitHub repository
            version: Version number for the installer
            output_dir: Output directory for the installer
        """
        self.repo_url = repo_url
        self.version = version
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), '../dist')
        self.temp_dir = tempfile.mkdtemp(prefix='handyman-kpi-build-')
        self.python_dir = os.path.join(self.temp_dir, 'python')
        self.app_dir = os.path.join(self.temp_dir, 'app')
        self.installer_dir = os.path.join(self.temp_dir, 'installer')
    
    def __del__(self):
        """Clean up temporary directory on deletion."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_directories(self):
        """Create necessary directories."""
        os.makedirs(self.python_dir, exist_ok=True)
        os.makedirs(self.app_dir, exist_ok=True)
        os.makedirs(self.installer_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def download_python(self):
        """Download embedded Python distribution."""
        python_url = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
        python_zip = os.path.join(self.temp_dir, "python.zip")
        
        # Download Python
        subprocess.check_call([
            "powershell", 
            "-Command", 
            f"Invoke-WebRequest -Uri {python_url} -OutFile {python_zip}"
        ])
        
        # Extract Python
        subprocess.check_call([
            "powershell",
            "-Command",
            f"Expand-Archive -Path {python_zip} -DestinationPath {self.python_dir}"
        ])
        
        # Download pip
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        get_pip_script = os.path.join(self.temp_dir, "get-pip.py")
        
        subprocess.check_call([
            "powershell", 
            "-Command", 
            f"Invoke-WebRequest -Uri {get_pip_url} -OutFile {get_pip_script}"
        ])
        
        # Install pip
        python_exe = os.path.join(self.python_dir, "python.exe")
        subprocess.check_call([python_exe, get_pip_script])
        
        # Enable pip modules
        site_packages = os.path.join(self.python_dir, "python310._pth")
        with open(site_packages, "a") as f:
            f.write("\nimport site\n")
    
    def clone_repository(self):
        """Clone the repository."""
        subprocess.check_call([
            "git",
            "clone",
            self.repo_url,
            self.app_dir
        ])
    
    def install_dependencies(self):
        """Install Python dependencies."""
        python_exe = os.path.join(self.python_dir, "python.exe")
        pip_exe = os.path.join(self.python_dir, "Scripts", "pip.exe")
        requirements = os.path.join(self.app_dir, "requirements.txt")
        
        subprocess.check_call([pip_exe, "install", "-r", requirements])
    
    def build_inno_setup(self):
        """Build the installer using Inno Setup."""
        # Copy installer files
        installer_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                         '../platforms/windows/inno/installer.iss')
        installer_script = os.path.join(self.installer_dir, "installer.iss")
        
        shutil.copy(installer_template, installer_script)
        
        # Update version
        with open(installer_script, "r") as f:
            content = f.read()
        
        content = content.replace("{{VERSION}}", self.version)
        content = content.replace("{{APP_DIR}}", self.app_dir.replace("\\", "\\\\"))
        content = content.replace("{{PYTHON_DIR}}", self.python_dir.replace("\\", "\\\\"))
        content = content.replace("{{OUTPUT_DIR}}", self.output_dir.replace("\\", "\\\\"))
        
        with open(installer_script, "w") as f:
            f.write(content)
        
        # Run Inno Setup compiler
        iscc_path = self._find_inno_setup()
        if not iscc_path:
            raise RuntimeError("Inno Setup Compiler (ISCC) not found")
        
        subprocess.check_call([iscc_path, installer_script])
    
    def _find_inno_setup(self) -> Optional[str]:
        """Find Inno Setup compiler."""
        # Common installation paths
        paths = [
            r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
            r'C:\Program Files\Inno Setup 6\ISCC.exe',
            r'C:\Program Files (x86)\Inno Setup 5\ISCC.exe',
            r'C:\Program Files\Inno Setup 5\ISCC.exe'
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def build(self) -> str:
        """Build the Windows installer.
        
        Returns:
            str: Path to the created installer
        """
        self.create_directories()
        self.download_python()
        self.clone_repository()
        self.install_dependencies()
        self.build_inno_setup()
        
        # Find the created installer
        installer_path = None
        for file in os.listdir(self.output_dir):
            if file.endswith('.exe') and 'handyman-kpi-system' in file:
                installer_path = os.path.join(self.output_dir, file)
                break
        
        if not installer_path:
            raise RuntimeError("Installer not found in output directory")
        
        return installer_path