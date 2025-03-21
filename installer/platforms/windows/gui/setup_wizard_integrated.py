"""Setup wizard for the Handyman KPI System Windows installer.

This module provides a graphical user interface for setting up the Handyman KPI System,
including database configuration, admin account creation, and application settings.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional, Callable

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))\n
from installer.core.config import InstallerConfig
from installer.core.environment import Environment
from installer.platforms.windows.environment import WindowsEnvironment
from installer.shared.database.initializer import DatabaseInitializer


class SetupWizard:
    """Setup wizard for the Handyman KPI System."""
    
    def __init__(self, config: Optional[InstallerConfig] = None):
        """Initialize setup wizard.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or InstallerConfig()
        self.environment = WindowsEnvironment()
        self.db_initializer = DatabaseInitializer()
        
        # Create root window
        self.root = tk.Tk()
        self.root.title("Handyman KPI System Setup")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # Create styles
        self.create_styles()