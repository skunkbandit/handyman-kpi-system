"""
WeasyPrint Dependencies Downloader

This script downloads the necessary wheel files for WeasyPrint and its dependencies
to include in the installer package. This ensures the installer can install WeasyPrint
without requiring internet access or compilation tools.

Usage:
    python download_wheels.py
"""

import os
import sys
import subprocess
import platform
import argparse

# Configuration
WHEELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'wheels')

# Required packages
PACKAGES = [
    'weasyprint',           # Main package
    'cairocffi',            # Cairo bindings
    'cffi',                 # C Foreign Function Interface
    'pycparser',            # C parser in Python
    'cssselect2',           # CSS selectors for Python ElementTree
    'tinycss2',             # CSS parser
    'html5lib',             # HTML parser
    'pyphen',               # Hyphenation library
    'Pillow',               # Python Imaging Library
    'CairoSVG',             # SVG to PNG/PDF converter
    'fonttools'             # Font processing tools
]

def get_python_version():
    """Get the current Python version."""
    major = sys.version_info.major
    minor = sys.version_info.minor
    return f'cp{major}{minor}'

def get_platform():
    """Get the current platform tag."""
    if platform.system() == 'Windows':
        return 'win_amd64' if platform.machine().endswith('64') else 'win32'
    elif platform.system() == 'Linux':
        return 'manylinux1_x86_64' if platform.machine().endswith('64') else 'manylinux1_i686'
    elif platform.system() == 'Darwin':
        return 'macosx_10_9_x86_64'
    else:
        return 'any'

def download_wheels():
    """Download wheels for all required packages."""
    # Create wheels directory if it doesn't exist
    os.makedirs(WHEELS_DIR, exist_ok=True)
    
    # Get Python version and platform
    python_version = get_python_version()
    platform_tag = get_platform()
    
    print(f"Downloading wheels for Python {python_version} on {platform_tag}...")
    
    # Use pip to download wheels
    for package in PACKAGES:
        print(f"\nDownloading {package}...")
        cmd = [
            sys.executable, 
            '-m', 
            'pip', 
            'download', 
            '--only-binary=:all:', 
            '--dest', 
            WHEELS_DIR,
            '--platform', 
            platform_tag,
            '--python-version', 
            python_version[2:],  # Remove 'cp' prefix
            package
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully downloaded {package}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {package}: {e}")
            
            # Try without platform and Python version constraints
            print(f"Trying alternative download method for {package}...")
            alt_cmd = [
                sys.executable,
                '-m',
                'pip',
                'download',
                '--dest',
                WHEELS_DIR,
                package
            ]
            try:
                subprocess.run(alt_cmd, check=True)
                print(f"Successfully downloaded {package} (alternative method)")
            except subprocess.CalledProcessError as e:
                print(f"Failed to download {package} with alternative method: {e}")
                print(f"Please download {package} manually and place the wheel file in the {WHEELS_DIR} directory")

def download_gtk3_runtime():
    """Download GTK3 Runtime installer."""
    installers_dir = os.path.join(os.path.dirname(WHEELS_DIR), 'installers')
    os.makedirs(installers_dir, exist_ok=True)
    
    gtk3_installer_path = os.path.join(installers_dir, 'gtk3-runtime-installer.exe')
    
    if os.path.exists(gtk3_installer_path):
        print(f"GTK3 Runtime installer already exists at: {gtk3_installer_path}")
        return
    
    print("Downloading GTK3 Runtime installer...")
    
    try:
        import urllib.request
        url = "https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe"
        urllib.request.urlretrieve(url, gtk3_installer_path)
        print(f"Successfully downloaded GTK3 Runtime installer to: {gtk3_installer_path}")
    except Exception as e:
        print(f"Failed to download GTK3 Runtime installer: {e}")
        print("Please download GTK3 Runtime installer manually from:")
        print("https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
        print(f"and place it at: {gtk3_installer_path}")

def main():
    """Main function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Download WeasyPrint dependencies.')
    parser.add_argument('--no-gtk', action='store_true', help='Skip downloading GTK3 Runtime installer')
    args = parser.parse_args()
    
    # Download wheels
    download_wheels()
    
    # Download GTK3 Runtime installer
    if not args.no_gtk:
        download_gtk3_runtime()
    
    # Print summary
    print("\nDownload Summary:")
    print(f"Wheels directory: {WHEELS_DIR}")
    print(f"Number of wheel files: {len([f for f in os.listdir(WHEELS_DIR) if f.endswith('.whl')])}")
    
    print("\nNext steps:")
    print("1. Run the installer build script:")
    print("   build_installer.bat")
    print("2. Test the installer on a clean system")

if __name__ == "__main__":
    main()
