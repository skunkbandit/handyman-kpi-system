"""
Setup wizard for the Handyman KPI System Windows installer.

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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

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
    
    def init_welcome_tab(self):
        """Initialize the welcome tab."""
        # Welcome message
        welcome_label = ttk.Label(
            self.welcome_tab, 
            text="Welcome to the Handyman KPI System Setup Wizard",
            style="Header.TLabel"
        )
        welcome_label.pack(pady=(40, 20))
        
        # Description
        desc_label = ttk.Label(
            self.welcome_tab,
            text=(
                "This wizard will guide you through the setup process for the "
                "Handyman KPI System. You will configure the database and create "
                "an administrator account.\n\n"
                "Click 'Next' to begin."
            ),
            wraplength=600,
            justify="center"
        )
        desc_label.pack(pady=20)
        
        # Next button
        next_button = ttk.Button(
            self.welcome_tab,
            text="Next",
            command=lambda: self.go_to_tab(1),
            style="Primary.TButton"
        )
        next_button.pack(pady=20)
        
    def init_database_tab(self):
        """Initialize the database configuration tab."""
        # Title
        title_label = ttk.Label(
            self.database_tab,
            text="Database Configuration",
            style="Header.TLabel"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(20, 10), padx=10, sticky="w")
        
        # Description
        desc_label = ttk.Label(
            self.database_tab,
            text="Select the database type and configure its settings. SQLite is recommended for single-user deployments.",
            wraplength=600
        )
        desc_label.grid(row=1, column=0, columnspan=3, pady=(0, 20), padx=10, sticky="w")
        
        # Database type
        type_label = ttk.Label(self.database_tab, text="Database Type:")
        type_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        type_frame = ttk.Frame(self.database_tab)
        type_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="w")
        
        sqlite_radio = ttk.Radiobutton(
            type_frame, 
            text="SQLite (Recommended for single-user)",
            variable=self.user_inputs['database']['type'],
            value='sqlite',
            command=self.update_db_fields
        )
        sqlite_radio.pack(anchor="w")
        
        mysql_radio = ttk.Radiobutton(
            type_frame, 
            text="MySQL",
            variable=self.user_inputs['database']['type'],
            value='mysql',
            command=self.update_db_fields
        )
        mysql_radio.pack(anchor="w")
        
        postgres_radio = ttk.Radiobutton(
            type_frame, 
            text="PostgreSQL",
            variable=self.user_inputs['database']['type'],
            value='postgresql',
            command=self.update_db_fields
        )
        postgres_radio.pack(anchor="w")
        
        # SQLite configuration
        self.sqlite_frame = ttk.LabelFrame(self.database_tab, text="SQLite Configuration")
        self.sqlite_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        
        path_label = ttk.Label(self.sqlite_frame, text="Database File:")
        path_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        path_entry = ttk.Entry(
            self.sqlite_frame,
            textvariable=self.user_inputs['database']['path'],
            width=40
        )
        path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        path_button = ttk.Button(
            self.sqlite_frame,
            text="Browse...",
            command=self.browse_db_path
        )
        path_button.grid(row=0, column=2, padx=10, pady=5, sticky="w")
    
    def update_db_fields(self):
        """Update database configuration fields based on selected type."""
        db_type = self.user_inputs['database']['type'].get()
        
        if db_type == 'sqlite':
            self.sqlite_frame.grid()
            self.server_frame.grid_remove()
        else:
            self.sqlite_frame.grid_remove()
            self.server_frame.grid()
            
            # Update port based on database type
            if db_type == 'mysql':
                self.user_inputs['database']['port'].set('3306')
            elif db_type == 'postgresql':
                self.user_inputs['database']['port'].set('5432')
    
    def browse_db_path(self):
        """Open file dialog to browse for database path."""
        initialdir = os.path.dirname(self.user_inputs['database']['path'].get())
        
        db_path = filedialog.asksaveasfilename(
            title="Select Database Location",
            initialdir=initialdir,
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        
        if db_path:
            self.user_inputs['database']['path'].set(db_path)
    
    def test_db_connection(self):
        """Test database connection with current settings."""
        db_type = self.user_inputs['database']['type'].get()
        
        # Build database configuration
        db_config = {'type': db_type}
        
        if db_type == 'sqlite':
            db_config['path'] = self.user_inputs['database']['path'].get()
        else:
            db_config['host'] = self.user_inputs['database']['host'].get()
            db_config['port'] = self.user_inputs['database']['port'].get()
            db_config['name'] = self.user_inputs['database']['name'].get()
            db_config['user'] = self.user_inputs['database']['user'].get()
            db_config['password'] = self.user_inputs['database']['password'].get()
        
        # Test connection
        status, error = self.db_initializer.test_database_connection(db_config)
        
        if status:
            messagebox.showinfo("Success", "Database connection successful!")
        else:
            messagebox.showerror("Error", f"Failed to connect to database\n\n{error}")
            
    def go_to_tab(self, tab_index: int) -> None:
        """Navigate to a specific tab.
        
        Args:
            tab_index: Index of the tab to navigate to
        """
        # Enable the target tab
        self.notebook.tab(tab_index, state="normal")
        
        # Select the target tab
        self.notebook.select(tab_index)
    
    def run(self) -> None:
        """Run the setup wizard."""
        self.root.mainloop()
