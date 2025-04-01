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
    # Use AppData\Local for logs instead of Program Files directory
    app_data_dir = os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
        "Handyman KPI System"
    )
    
    # Create log directory in AppData
    log_dir = os.path.join(app_data_dir, "logs")
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
    
    # Log the location so we can find it later if needed
    print(f"Log file: {log_file}")
    return app_data_dir

def main():
    """Launch the Handyman KPI application."""
    try:
        # Initialize logging - store the app data directory for future use
        app_data_dir = setup_logging()
        logging.info("Starting Handyman KPI System...")
        
        # Get the installation directory - we know this will be where the executable is located
        if hasattr(sys, '_MEIPASS'):
            # We're running from a PyInstaller bundle
            base_dir = os.path.dirname(sys.executable)
            logging.info(f"Running from PyInstaller bundle. Base directory: {base_dir}")
        else:
            # We're running as a regular Python script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logging.info(f"Running as script. Base directory: {base_dir}")
        
        logging.info(f"Base directory: {base_dir}")
        logging.info(f"App data directory: {app_data_dir}")
        
        # Path to the Python executable (in the installation directory)
        python_path = os.path.join(base_dir, "python", "python.exe")
        
        # Path to the main application script
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
            input("Press Enter to exit...")
            return 1
        
        # Ensure the app script exists
        if not os.path.exists(app_script):
            logging.error(f"Application script not found at {app_script}")
            print(f"Error: Application script not found at {app_script}")
            input("Press Enter to exit...")
            return 1
        
        # Set up paths for Python modules
        backend_dir = os.path.dirname(app_script)  # This is the backend directory
        app_module_dir = os.path.join(backend_dir, "app")  # This is where the app module should be
        parent_dir = os.path.dirname(backend_dir)  # Parent directory of backend
        python_lib_dir = os.path.join(os.path.dirname(python_path), "Lib")  # Python standard library
        site_packages = os.path.join(python_lib_dir, "site-packages")  # Third-party packages
        
        # Set Python path environment
        env = os.environ.copy()
        
        # Create a PYTHONPATH value that includes all necessary directories
        python_path_value = os.pathsep.join([
            backend_dir, 
            app_module_dir, 
            parent_dir,
            python_lib_dir,
            site_packages
        ])
        env["PYTHONPATH"] = python_path_value
        
        # Set environment variables for the application
        env["FLASK_APP"] = "app"
        env["KPI_SYSTEM_APP_DATA"] = app_data_dir
        
        logging.info(f"Set PYTHONPATH to: {python_path_value}")
        logging.info(f"Set KPI_SYSTEM_APP_DATA to: {app_data_dir}")
        
        # Launch the application
        logging.info("Launching application...")
        print(f"Launching application with Python: {python_path}")
        print(f"Running script: {app_script}")
        
        try:
            # Use subprocess.run with captured output
            process = subprocess.run(
                [python_path, app_script], 
                env=env, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Log any output for debugging
            if process.stdout:
                logging.info(f"Application stdout:\n{process.stdout}")
            if process.stderr:
                logging.info(f"Application stderr:\n{process.stderr}")
                
            logging.info("Application closed normally")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error launching application: {e}")
            
            # Log captured output for debugging
            if hasattr(e, 'stdout') and e.stdout:
                logging.info(f"Application stdout:\n{e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                logging.error(f"Application stderr:\n{e.stderr}")
                
            print(f"Error launching application: {e}")
            print("See logs for details.")
            input("Press Enter to exit...")
            return 1
        
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
