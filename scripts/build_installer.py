"""
Build script for the Handyman KPI System Windows installer.

This script simplifies the installer build process by:
1. Creating necessary installer resource files
2. Building the Windows installer using the existing build module
3. Handling common errors and providing detailed feedback

Requirements:
- Python 3.8 or higher
- Inno Setup 6 or higher
- Git
- PIL (Python Imaging Library) for image generation
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def ensure_resources_exist():
    """Ensure all required installer resources exist."""
    # First check if the image generation script exists
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_installer_images.py")
    
    if not os.path.exists(script_path):
        print("Error: Image generation script not found.")
        return False
    
    # Run the image generation script
    try:
        print("Generating installer resource files...")
        subprocess.check_call([sys.executable, script_path])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating installer resources: {e}")
        try:
            # Try to install PIL if it's missing
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            print("Pillow package installed. Retrying image generation...")
            subprocess.check_call([sys.executable, script_path])
            return True
        except subprocess.CalledProcessError as e2:
            print(f"Failed to generate installer resources: {e2}")
            return False

def copy_resources_to_temp(temp_dir):
    """Copy resources to the temporary directory."""
    print(f"Copying resources to temporary directory: {temp_dir}")
    
    # Create resources directory in temp
    resources_dir = os.path.join(temp_dir, "app", "resources")
    os.makedirs(os.path.join(resources_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(resources_dir, "icons"), exist_ok=True)
    
    # Get source paths
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_images_dir = os.path.join(proj_dir, "resources", "images")
    src_icons_dir = os.path.join(proj_dir, "resources", "icons")
    
    # Copy images
    for img_file in ["wizard-image.bmp", "wizard-image-large.bmp"]:
        src_path = os.path.join(src_images_dir, img_file)
        dst_path = os.path.join(resources_dir, "images", img_file)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"Copied {img_file} to {dst_path}")
        else:
            print(f"Warning: {img_file} not found at {src_path}")
    
    # Copy icons
    icon_file = "handyman_kpi.ico"
    src_path = os.path.join(src_icons_dir, icon_file)
    dst_path = os.path.join(resources_dir, "icons", icon_file)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Copied {icon_file} to {dst_path}")
    else:
        print(f"Warning: {icon_file} not found at {src_path}")
    
    # Create dummy LICENSE file if it doesn't exist
    license_path = os.path.join(temp_dir, "app", "LICENSE")
    if not os.path.exists(license_path):
        with open(license_path, "w") as f:
            f.write("MIT License\n\nCopyright (c) 2025 Handyman KPI System\n\nPermission is hereby granted...")
        print("Created placeholder LICENSE file")
    
    return True

def build_installer():
    """Build the Windows installer."""
    print("Building Handyman KPI System installer...")
    
    # Ensure resources exist
    if not ensure_resources_exist():
        print("Failed to ensure resources exist. Aborting build.")
        return False
    
    try:
        # Import the Windows builder
        from installer.build.windows import WindowsBuilder
        
        # Intercept the build method to add our custom resource copying
        original_build = WindowsBuilder.build
        
        def patched_build(self):
            print("Running patched build method with resource copying...")
            # Create directories
            self.create_directories()
            
            # Download Python
            self.download_python()
            
            # Clone repository
            self.clone_repository()
            
            # Copy resources to temp directory
            copy_resources_to_temp(self.temp_dir)
            
            # Install dependencies
            self.install_dependencies()
            
            # Build Inno Setup
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
        
        # Patch the build method
        WindowsBuilder.build = patched_build
        
        # Create builder instance
        builder = WindowsBuilder(
            repo_url="https://github.com/skunkbandit/handyman-kpi-system",
            version="1.0.0",
            output_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "installer", "dist")
        )
        
        # Build the installer
        installer_path = builder.build()
        print(f"Windows installer created: {installer_path}")
        return True
    
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this script from the project root directory.")
        return False
    
    except Exception as e:
        print(f"Error building installer: {e}")
        return False

def create_build_batch_file():
    """Create a batch file to build the installer."""
    print("Creating build batch file...")
    
    # Get the project root directory
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the batch file
    batch_path = os.path.join(proj_dir, "build_installer.bat")
    
    with open(batch_path, "w") as f:
        f.write("@echo off\n")
        f.write("echo Building Handyman KPI System installer...\n")
        f.write("\n")
        f.write(":: Activate virtual environment if it exists\n")
        f.write("if exist venv\\Scripts\\activate.bat (\n")
        f.write("    call venv\\Scripts\\activate.bat\n")
        f.write(")\n")
        f.write("\n")
        f.write(":: Install required packages\n")
        f.write("pip install pillow\n")
        f.write("\n")
        f.write(":: Run the build script\n")
        f.write("python scripts\\build_installer.py\n")
        f.write("\n")
        f.write(":: Check if the build was successful\n")
        f.write("if %errorlevel% neq 0 (\n")
        f.write("    echo Error building installer!\n")
        f.write("    pause\n")
        f.write("    exit /b %errorlevel%\n")
        f.write(")\n")
        f.write("\n")
        f.write("echo Installer built successfully!\n")
        f.write("pause\n")
    
    print(f"Created build batch file: {batch_path}")
    return batch_path

def main():
    """Main function."""
    print("Handyman KPI System Installer Builder")
    print("===================================")
    
    # Create the build batch file
    batch_path = create_build_batch_file()
    
    # Ask the user if they want to build the installer now
    choice = input("\nDo you want to build the installer now? (y/n): ")
    
    if choice.lower() in ['y', 'yes']:
        print("\nBuilding installer...")
        if build_installer():
            print("\nInstaller built successfully!")
        else:
            print("\nFailed to build installer.")
            sys.exit(1)
    else:
        print(f"\nInstaller not built. You can build it later by running {batch_path}")
    
    print("\nDone.")

if __name__ == "__main__":
    main()
