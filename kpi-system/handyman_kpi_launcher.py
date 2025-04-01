"""
Handyman KPI System Launcher

This script serves as the main entry point for the installed Handyman KPI application.
It locates the embedded Python interpreter and launches the main application.
"""
import os
import sys
import subprocess
import logging
import traceback

# Set up logging
def setup_logging():
    # For PyInstaller bundle, log to the Program Files directory
    if hasattr(sys, '_MEIPASS'):
        # We're running from a PyInstaller bundle
        base_dir = os.path.dirname(sys.executable)
        log_dir = os.path.join(base_dir, "logs")
    else:
        # We're running as a regular Python script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(base_dir, "logs")
    
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "launcher.log")
    
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

def main():
    """Launch the Handyman KPI application."""
    try:
        # Initialize logging
        setup_logging()
        logging.info("Starting Handyman KPI System...")
        
        # Get the installation directory - we know this will be where the executable is located
        # CRITICAL: When installed, the launcher is in Program Files/Handyman KPI System/
        # and Python is in Program Files/Handyman KPI System/python/
        if hasattr(sys, '_MEIPASS'):
            # We're running from a PyInstaller bundle (installed application)
            base_dir = os.path.dirname(sys.executable)
            logging.info(f"Running from PyInstaller bundle. Base directory: {base_dir}")
        else:
            # We're running as a regular Python script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logging.info(f"Running as script. Base directory: {base_dir}")
        
        logging.info(f"Base directory: {base_dir}")
        
        # Path to the Python executable (in the installation directory)
        python_path = os.path.join(base_dir, "python", "python.exe")
        
        # Path to the main application script - assuming it's in the same directory
        # as the installation, under kpi-system/backend/run.py
        app_script = os.path.join(base_dir, "kpi-system", "backend", "run.py")
        
        # If the app script doesn't exist, check for it directly in the backend subdirectory
        if not os.path.exists(app_script):
            app_script = os.path.join(base_dir, "backend", "run.py")
        
        # Log paths for debugging
        logging.info(f"Python path: {python_path}")
        logging.info(f"Application script: {app_script}")
        
        # Ensure the Python path exists
        if not os.path.exists(python_path):
            logging.error(f"Python executable not found at {python_path}")
            print(f"Error: Python executable not found at {python_path}")
            print("Looking in alternate locations...")
            
            # List contents of the base directory to help diagnose
            logging.info(f"Contents of base directory ({base_dir}):")
            try:
                for item in os.listdir(base_dir):
                    logging.info(f"  {item}")
                    if os.path.isdir(os.path.join(base_dir, item)):
                        try:
                            subdir_contents = os.listdir(os.path.join(base_dir, item))
                            for subitem in subdir_contents:
                                logging.info(f"    {item}/{subitem}")
                        except Exception as e:
                            logging.error(f"Error listing contents of {item}: {e}")
            except Exception as e:
                logging.error(f"Error listing directory contents: {e}")
            
            input("Press Enter to exit...")
            return 1
        
        # Ensure the app script exists
        if not os.path.exists(app_script):
            logging.error(f"Application script not found at {app_script}")
            print(f"Error: Application script not found at {app_script}")
            print("Looking in alternate locations...")
            
            # List available Python scripts in the installation directory
            logging.info("Searching for Python scripts in installation directory...")
            found_scripts = []
            
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.py'):
                        rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                        logging.info(f"  Found Python script: {rel_path}")
                        found_scripts.append(os.path.join(root, file))
            
            # Try to find a run.py file
            run_scripts = [script for script in found_scripts if os.path.basename(script) == 'run.py']
            if run_scripts:
                app_script = run_scripts[0]
                logging.info(f"Using run.py script: {app_script}")
                print(f"Found application script at: {app_script}")
            else:
                logging.error("No run.py script found in installation directory")
                print("Error: Could not find application script in installation directory.")
                input("Press Enter to exit...")
                return 1
        
        # Set Python path environment
        env = os.environ.copy()
        
        # CRITICAL FIX: Properly set the Python paths for import resolution
        # We need to add both the backend directory and its parent directory to the path
        backend_dir = os.path.dirname(app_script)  # This is the backend directory
        app_module_dir = os.path.join(backend_dir, "app")  # This is where the app module should be
        parent_dir = os.path.dirname(backend_dir)  # Parent directory of backend, needed for some imports
        
        # Create a PYTHONPATH value that includes both directories
        python_path_value = os.pathsep.join([backend_dir, app_module_dir, parent_dir])
        env["PYTHONPATH"] = python_path_value
        
        logging.info(f"Set PYTHONPATH to: {python_path_value}")
        
        # Launch the application
        logging.info("Launching application...")
        print(f"Launching application with Python: {python_path}")
        print(f"Running script: {app_script}")
        
        try:
            # First approach - use subprocess.run with check=True to raise exceptions
            subprocess.run([python_path, app_script], env=env, check=True)
            logging.info("Application closed normally")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running script: {e}")
            
            # Second approach - try running with -m flag to help with module imports
            logging.info("Trying alternative approach with module import...")
            try:
                # Get the module name from the script path (relative to the parent directory)
                script_rel_path = os.path.relpath(app_script, parent_dir)
                module_path = script_rel_path.replace(os.path.sep, '.').replace('.py', '')
                
                logging.info(f"Running as module: {module_path}")
                subprocess.run([python_path, "-m", module_path], env=env, check=True)
                logging.info("Application closed normally using module approach")
            except subprocess.CalledProcessError as inner_e:
                logging.error(f"Error running script as module: {inner_e}")
                raise
        
    except Exception as e:
        logging.error(f"Error launching application: {e}")
        logging.error(traceback.format_exc())
        print(f"Error launching application: {e}")
        print("See logs for details.")
        input("Press Enter to exit...")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Catch any uncaught exceptions
        print(f"Critical error in launcher: {e}")
        print("See logs for details.")
        try:
            logging.error(f"Critical error in launcher: {e}")
            logging.error(traceback.format_exc())
        except:
            pass
        input("Press Enter to exit...")
        sys.exit(1)
