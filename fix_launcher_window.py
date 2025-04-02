# Launcher Window Fix Script

import os
import sys
import shutil
import logging
import subprocess
import winreg
import ctypes
from pathlib import Path

# Windows specific constants
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008

# Configure logging
def setup_logging():
    app_data_dir = os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
        "Handyman KPI System"
    )
    
    # Create log directory
    log_dir = os.path.join(app_data_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up logging
    log_file = os.path.join(log_dir, "launcher_fix.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)
    
    return app_data_dir

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def find_install_directory():
    """Find the KPI System installation directory."""
    possible_paths = [
        r"C:\Program Files\Handyman KPI System",
        r"C:\Handyman KPI System",
        r"C:\Users\dtest\KPI Project"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            # Check if it contains the launcher
            launcher_path = os.path.join(path, "kpi-system", "handyman_kpi_launcher.py")
            if os.path.exists(launcher_path):
                logging.info(f"Found KPI System at: {path}")
                return path
    
    # Try to find via registry
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Handyman KPI System") as key:
            install_dir = winreg.QueryValueEx(key, "InstallPath")[0]
            if os.path.exists(install_dir):
                logging.info(f"Found KPI System via registry at: {install_dir}")
                return install_dir
    except:
        pass
    
    logging.warning("Could not find KPI System installation directory")
    return None

def create_detached_launcher():
    """Create a detached launcher script."""
    try:
        # Create launcher in the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        new_launcher_path = os.path.join(script_dir, "handyman_kpi_launcher_detached.py")
        
        # Create the new detached launcher
        detached_launcher_content = """\"""\
        Detached Launcher for Handyman KPI System

        This launcher starts the application as a detached process with no console window.
        \"""\

        import os
        import sys
        import json
        import time
        import logging
        import subprocess
        import ctypes
        from pathlib import Path

        # Windows process creation flags
        CREATE_NO_WINDOW = 0x08000000
        DETACHED_PROCESS = 0x00000008

        def setup_logging():
            \"\"\"Configure logging to file.\"\"\"
            app_data_dir = os.path.join(
                os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
                "Handyman KPI System"
            )
            
            log_dir = os.path.join(app_data_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "launcher.log")
            
            logging.basicConfig(
                filename=log_file,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            return app_data_dir

        def find_flask_app():
            \"\"\"Find the path to the Flask application.\"\"\"
            # Get script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Check if we're in the project root or in a subdirectory
            if os.path.exists(os.path.join(script_dir, "kpi-system")):
                backend_path = os.path.join(script_dir, "kpi-system", "backend")
            elif os.path.basename(script_dir) == "kpi-system":
                backend_path = os.path.join(script_dir, "backend")
            else:
                # Try one level up
                parent_dir = os.path.dirname(script_dir)
                if os.path.exists(os.path.join(parent_dir, "kpi-system")):
                    backend_path = os.path.join(parent_dir, "kpi-system", "backend")
                else:
                    # Last resort: check if we're in the backend directory
                    if os.path.basename(script_dir) == "backend":
                        backend_path = script_dir
                    else:
                        # Try finding the installation directory from registry
                        try:
                            import winreg
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Handyman KPI System") as key:
                                install_dir = winreg.QueryValueEx(key, "InstallPath")[0]
                                backend_path = os.path.join(install_dir, "kpi-system", "backend")
                        except:
                            logging.error("Could not find backend directory")
                            backend_path = None
            
            if backend_path and os.path.exists(backend_path):
                logging.info(f"Found backend directory: {backend_path}")
                run_py = os.path.join(backend_path, "run.py")
                if os.path.exists(run_py):
                    return run_py
            
            logging.error("Could not locate run.py")
            return None

        def check_python_installation():
            \"\"\"Check Python installation and environment.\"\"\"
            python_exe = sys.executable
            logging.info(f"Python executable: {python_exe}")
            
            # Check for pythonw.exe
            if python_exe.endswith("python.exe"):
                pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
                if os.path.exists(pythonw_exe):
                    logging.info(f"Using pythonw.exe: {pythonw_exe}")
                    return pythonw_exe
            
            return python_exe

        def get_database_path(app_data_dir):
            \"\"\"Get the database path.\"\"\"
            config_file = os.path.join(app_data_dir, "config", "database.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        if 'path' in config:
                            db_path = config['path']
                            logging.info(f"Database path from config: {db_path}")
                            return db_path
                except Exception as e:
                    logging.error(f"Error reading config file: {e}")
            
            # Default path
            db_path = os.path.join(app_data_dir, "database", "kpi_system.db")
            logging.info(f"Using default database path: {db_path}")
            return db_path

        def initialize_database_if_needed(app_data_dir, python_exe):
            \"\"\"Initialize database if it doesn't exist.\"\"\"
            db_path = get_database_path(app_data_dir)
            
            if not os.path.exists(db_path):
                logging.warning(f"Database file not found: {db_path}")
                
                # Find initialize_database.py
                script_dir = os.path.dirname(os.path.abspath(__file__))
                init_db_script = os.path.join(script_dir, "initialize_database.py")
                
                if not os.path.exists(init_db_script):
                    # Try one level up
                    init_db_script = os.path.join(os.path.dirname(script_dir), "initialize_database.py")
                
                if os.path.exists(init_db_script):
                    logging.info(f"Running database initialization: {init_db_script}")
                    try:
                        subprocess.run([python_exe, init_db_script], check=True)
                        logging.info("Database initialized successfully")
                    except Exception as e:
                        logging.error(f"Error initializing database: {e}")
                        return False
                else:
                    logging.error("Could not find initialize_database.py")
                    return False
            
            return True

        def launch_app(flask_app_path, python_exe):
            \"\"\"Launch the Flask application as a detached process.\"\"\"
            try:
                # Use subprocess.Popen to create a detached process
                process = subprocess.Popen(
                    [python_exe, flask_app_path],
                    creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
                    close_fds=True,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait a moment to see if the process crashes immediately
                time.sleep(1)
                if process.poll() is not None:
                    logging.error(f"Application failed to start: Exit code {process.returncode}")
                    stderr = process.stderr.read().decode('utf-8', errors='ignore')
                    logging.error(f"Error output: {stderr}")
                    return False
                
                logging.info(f"Started application with PID: {process.pid}")
                return True
            
            except Exception as e:
                logging.error(f"Error launching application: {e}")
                return False

        def create_browser_shortcut():
            \"\"\"Create a desktop shortcut to access the application via web browser.\"\"\"
            try:
                # Only create if we have access to the Desktop folder
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                if not os.path.exists(desktop_path):
                    return
                
                shortcut_path = os.path.join(desktop_path, "Handyman KPI System (Browser).url")
                with open(shortcut_path, 'w') as f:
                    f.write("[InternetShortcut]\\n")
                    f.write("URL=http://localhost:5000\\n")
                    f.write("IconIndex=0\\n")
                
                logging.info(f"Created browser shortcut: {shortcut_path}")
            except Exception as e:
                logging.error(f"Error creating browser shortcut: {e}")

        def main():
            \"\"\"Main function to start the KPI System.\"\"\"
            try:
                # Configure logging
                app_data_dir = setup_logging()
                logging.info("Starting Handyman KPI System launcher...")
                
                # Find the Flask application
                flask_app_path = find_flask_app()
                if not flask_app_path:
                    logging.error("Cannot find Flask application")
                    return 1
                
                # Check Python installation
                python_exe = check_python_installation()
                
                # Initialize database if needed
                if not initialize_database_if_needed(app_data_dir, python_exe):
                    logging.warning("Continuing despite database initialization issues")
                
                # Launch the application
                if not launch_app(flask_app_path, python_exe):
                    logging.error("Failed to launch application")
                    return 1
                
                # Create browser shortcut
                create_browser_shortcut()
                
                logging.info("Application launched successfully")
                return 0
            
            except Exception as e:
                logging.error(f"Unhandled error in launcher: {e}")
                return 1

        if __name__ == "__main__":
            sys.exit(main())
        """
        
        with open(new_launcher_path, 'w') as f:
            f.write(detached_launcher_content)
        
        logging.info(f"Created detached launcher at: {new_launcher_path}")
        return True
    
    except Exception as e:
        logging.error(f"Error creating detached launcher: {e}")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut to launch the application."""
    try:
        # Get current user's desktop path
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop_path, "Handyman KPI System.lnk")
        
        # Find Python and pythonw paths
        python_dir = os.path.dirname(sys.executable)
        pythonw_exe = os.path.join(python_dir, "pythonw.exe")
        
        if not os.path.exists(pythonw_exe):
            logging.error(f"pythonw.exe not found at: {pythonw_exe}")
            return False
        
        # Find the launcher
        script_dir = os.path.dirname(os.path.abspath(__file__))
        detached_launcher = os.path.join(script_dir, "handyman_kpi_launcher_detached.py")
        
        if not os.path.exists(detached_launcher):
            logging.error(f"Detached launcher not found at: {detached_launcher}")
            return False
        
        # Get icon path - try some common locations
        icon_path = None
        icon_locations = [
            os.path.join(script_dir, "kpi-system", "frontend", "static", "img", "logo.ico"),
            os.path.join(script_dir, "kpi-system", "frontend", "static", "img", "favicon.ico"),
            os.path.join(script_dir, "resources", "logo.ico")
        ]
        
        for path in icon_locations:
            if os.path.exists(path):
                icon_path = path
                break
        
        if not icon_path:
            # Use Python icon as fallback
            icon_path = pythonw_exe
        
        # Create PowerShell command for shortcut creation
        ps_command = f"""
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
        $Shortcut.TargetPath = '{pythonw_exe}'
        $Shortcut.Arguments = '"{detached_launcher}"'
        $Shortcut.WorkingDirectory = '{script_dir}'
        $Shortcut.IconLocation = '{icon_path}'
        $Shortcut.Description = 'Handyman KPI System'
        $Shortcut.WindowStyle = 7
        $Shortcut.Save()
        """
        
        # Execute PowerShell command
        subprocess.run(["powershell", "-Command", ps_command], check=True, capture_output=True)
        
        logging.info(f"Created desktop shortcut: {shortcut_path}")
        return True
    
    except Exception as e:
        logging.error(f"Error creating desktop shortcut: {e}")
        return False

def create_browser_shortcut():
    """Create a desktop shortcut for browser access."""
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop_path, "Handyman KPI System (Browser).url")
        
        with open(shortcut_path, 'w') as f:
            f.write("[InternetShortcut]\n")
            f.write("URL=http://localhost:5000\n")
            f.write("IconIndex=0\n")
        
        logging.info(f"Created browser shortcut: {shortcut_path}")
        return True
    
    except Exception as e:
        logging.error(f"Error creating browser shortcut: {e}")
        return False

def generate_admin_deployment_instructions(install_dir):
    """Generate instructions for deploying the fix with admin privileges."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Prepare the launcher paths
    launcher_src = os.path.join(script_dir, "handyman_kpi_launcher_detached.py")
    launcher_dst = os.path.join(install_dir, "handyman_kpi_launcher_detached.py")
    
    # Create the instructions
    instructions = f"""
===================================================
HANDYMAN KPI SYSTEM - DEPLOYMENT INSTRUCTIONS
===================================================

The detached launcher has been created at:
{launcher_src}

To complete the installation, please run these commands with admin privileges:

1. Open a Command Prompt as Administrator and execute:

copy "{launcher_src}" "{launcher_dst}"

===================================================

After deployment, use the desktop shortcuts to launch the application.
The regular shortcut uses the detached launcher with no console window.
The "(Browser)" shortcut opens the application directly in your web browser.

Default login credentials:
Username: admin
Password: admin

Thank you for using Handyman KPI System!
"""
    
    # Save the instructions to a file
    instruction_file = os.path.join(script_dir, "deployment_instructions.txt")
    with open(instruction_file, 'w') as f:
        f.write(instructions)
    
    logging.info(f"Generated deployment instructions at: {instruction_file}")
    return instructions

def main():
    """Main function to fix launcher window."""
    try:
        # Setup logging
        app_data_dir = setup_logging()
        logging.info("Starting launcher window fix...")
        
        # Find installation directory
        install_dir = find_install_directory()
        if not install_dir:
            logging.error("Could not find KPI System installation directory")
            return 1
        
        # Create detached launcher
        if not create_detached_launcher():
            logging.error("Failed to create detached launcher")
            return 1
        
        # Create desktop shortcut
        if not create_desktop_shortcut():
            logging.warning("Failed to create desktop shortcut")
        
        # Create browser shortcut
        if not create_browser_shortcut():
            logging.warning("Failed to create browser shortcut")
        
        # Generate admin deployment instructions
        if install_dir.startswith(r"C:\Program Files"):
            instructions = generate_admin_deployment_instructions(install_dir)
            print(instructions)
        else:
            # If not in Program Files, try to copy directly
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                launcher_src = os.path.join(script_dir, "handyman_kpi_launcher_detached.py")
                launcher_dst = os.path.join(install_dir, "handyman_kpi_launcher_detached.py")
                shutil.copy2(launcher_src, launcher_dst)
                logging.info(f"Deployed launcher to: {launcher_dst}")
            except Exception as e:
                logging.error(f"Error deploying launcher: {e}")
                # Generate instructions anyway
                instructions = generate_admin_deployment_instructions(install_dir)
                print(instructions)
        
        logging.info("Launcher window fix completed successfully")
        print("\nLauncher window fix completed successfully")
        print("Desktop shortcuts have been created to launch the application without a console window")
        return 0
    
    except Exception as e:
        logging.error(f"Error during launcher window fix: {e}")
        print(f"Error during launcher window fix: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
