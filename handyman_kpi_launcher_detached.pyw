#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Detached Launcher for Handyman KPI System
# This launcher starts the Flask application without showing a console window

import os
import sys
import subprocess
import logging
import time
from datetime import datetime
import threading
from pathlib import Path

# Set up logging
def setup_logging():
    # Get app data directory
    app_data_dir = os.path.join(
        os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
        "Handyman KPI System"
    )
    
    # Create log directory
    log_dir = os.path.join(app_data_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up logging to file
    log_file = os.path.join(log_dir, f"kpi_system_{datetime.now().strftime('%Y%m%d')}.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return app_data_dir

# Find the Python executable in the installation directory
def get_python_path():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for python.exe in the installation directory
    python_path = os.path.join(script_dir, "python", "pythonw.exe")
    if os.path.exists(python_path):
        return python_path
    
    # If not found, look for python in the PATH
    try:
        python_path = subprocess.check_output(["where", "pythonw"]).decode().strip().split("\n")[0]
        return python_path
    except:
        # If all else fails, try to use sys.executable
        if sys.executable and os.path.exists(sys.executable):
            # Get pythonw.exe instead of python.exe
            python_dir = os.path.dirname(sys.executable)
            pythonw_path = os.path.join(python_dir, "pythonw.exe")
            if os.path.exists(pythonw_path):
                return pythonw_path
            return sys.executable
    
    return None

# Find the backend run script
def get_backend_script():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for various backend run scripts
    possible_scripts = [
        os.path.join(script_dir, "kpi-system", "backend", "run.py"),
        os.path.join(script_dir, "kpi-system", "run.py"),
        os.path.join(script_dir, "backend_run.py"),
        os.path.join(script_dir, "fixed_backend_run.py"),
        os.path.join(script_dir, "final_backend_run.py")
    ]
    
    for script in possible_scripts:
        if os.path.exists(script):
            return script
    
    return None

# Run the backend in a separate thread
def run_backend_thread(python_path, backend_script):
    logging.info(f"Starting backend with: {python_path} {backend_script}")
    
    try:
        # Set creation flags to run without showing a window
        startupinfo = None
        if os.name == 'nt':
            DETACHED_PROCESS = 0x00000008
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
            
            # Use subprocess.Popen with CREATE_NO_WINDOW flag
            process = subprocess.Popen(
                [python_path, backend_script],
                creationflags=subprocess.CREATE_NO_WINDOW | DETACHED_PROCESS,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                shell=False
            )
        else:
            # For non-Windows platforms
            process = subprocess.Popen(
                [python_path, backend_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
        
        logging.info(f"Backend process started with PID: {process.pid}")
        
        # Start threads to read output without blocking
        def read_output(pipe, prefix):
            for line in iter(pipe.readline, b''):
                logging.info(f"{prefix}: {line.decode().strip()}")
        
        threading.Thread(target=read_output, args=(process.stdout, "STDOUT"), daemon=True).start()
        threading.Thread(target=read_output, args=(process.stderr, "STDERR"), daemon=True).start()
        
        # Check if the process is running
        time.sleep(1)
        if process.poll() is None:
            logging.info("Backend process is running successfully")
        else:
            logging.error(f"Backend process exited with code: {process.returncode}")
        
        return process
    
    except Exception as e:
        logging.error(f"Error starting backend: {e}")
        return None
