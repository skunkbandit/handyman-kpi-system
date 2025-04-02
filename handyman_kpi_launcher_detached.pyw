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