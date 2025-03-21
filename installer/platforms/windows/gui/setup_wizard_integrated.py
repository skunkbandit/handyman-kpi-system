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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))  # noqa

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
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        header_label = ttk.Label(
            header_frame,
            text="Handyman KPI System Setup",
            font=("Arial", 16, "bold")
        )
        header_label.pack(side=tk.LEFT)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.welcome_tab = ttk.Frame(self.notebook)
        self.database_tab = ttk.Frame(self.notebook)
        self.admin_tab = ttk.Frame(self.notebook)
        self.finish_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.welcome_tab, text="Welcome")
        self.notebook.add(self.database_tab, text="Database")
        self.notebook.add(self.admin_tab, text="Admin Account")
        self.notebook.add(self.finish_tab, text="Finish")
        
        # Initialize tabs
        self.init_welcome_tab()
        self.init_database_tab()
        self.init_admin_tab()
        self.init_finish_tab()
        
        # Disable tabs (will be enabled as we progress)
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.notebook.tab(3, state="disabled")
        
        # Dictionary to store user inputs
        self.user_inputs = {
            'database': {
                'type': tk.StringVar(value='sqlite'),
                'path': tk.StringVar(value=os.path.join(
                    self.environment.get_app_directory(), 'data', 'database.db')),
                'host': tk.StringVar(value='localhost'),
                'port': tk.StringVar(value='3306'),
                'name': tk.StringVar(value='handyman_kpi'),
                'user': tk.StringVar(value='root'),
                'password': tk.StringVar(value='')
            },
            'admin': {
                'username': tk.StringVar(value='admin'),
                'password': tk.StringVar(value=''),
                'confirm_password': tk.StringVar(value=''),
                'email': tk.StringVar(value='admin@example.com'),
                'first_name': tk.StringVar(value=''),
                'last_name': tk.StringVar(value='')
            },
            'app': {
                'company_name': tk.StringVar(value='Handyman Service Company'),
                'port': tk.StringVar(value='5000'),
                'create_desktop_shortcut': tk.BooleanVar(value=True),
                'create_start_menu_shortcut': tk.BooleanVar(value=True),
                'auto_start': tk.BooleanVar(value=False)
            }
        }
        
        # Center window on screen
        self.center_window()
    
    def create_styles(self):
        """Create styles for the wizard."""
        style = ttk.Style()
        
        # Create a style for headers
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        
        # Create a style for primary buttons
        style.configure("Primary.TButton", font=("Arial", 10, "bold"))
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")