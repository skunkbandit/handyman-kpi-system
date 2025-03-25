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
        
        # Server database configuration
        self.server_frame = ttk.LabelFrame(self.database_tab, text="Server Configuration")
        self.server_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.server_frame.grid_remove()  # Hidden initially
        
        host_label = ttk.Label(self.server_frame, text="Host:")
        host_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        host_entry = ttk.Entry(
            self.server_frame,
            textvariable=self.user_inputs['database']['host'],
            width=20
        )
        host_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        port_label = ttk.Label(self.server_frame, text="Port:")
        port_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        port_entry = ttk.Entry(
            self.server_frame,
            textvariable=self.user_inputs['database']['port'],
            width=10
        )
        port_entry.grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        db_label = ttk.Label(self.server_frame, text="Database Name:")
        db_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        db_entry = ttk.Entry(
            self.server_frame,
            textvariable=self.user_inputs['database']['name'],
            width=20
        )
        db_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        user_label = ttk.Label(self.server_frame, text="Username:")
        user_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        user_entry = ttk.Entry(
            self.server_frame,
            textvariable=self.user_inputs['database']['user'],
            width=20
        )
        user_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        pass_label = ttk.Label(self.server_frame, text="Password:")
        pass_label.grid(row=2, column=2, padx=10, pady=5, sticky="w")
        
        pass_entry = ttk.Entry(
            self.server_frame,
            textvariable=self.user_inputs['database']['password'],
            width=20,
            show="*"
        )
        pass_entry.grid(row=2, column=3, padx=10, pady=5, sticky="w")
        
        # Test connection button
        test_button = ttk.Button(
            self.database_tab,
            text="Test Connection",
            command=self.test_db_connection
        )
        test_button.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        
        # Navigation buttons
        button_frame = ttk.Frame(self.database_tab)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        back_button = ttk.Button(
            button_frame,
            text="Back",
            command=lambda: self.go_to_tab(0)
        )
        back_button.pack(side="left", padx=5)
        
        next_button = ttk.Button(
            button_frame,
            text="Next",
            command=self.save_db_config,
            style="Primary.TButton"
        )
        next_button.pack(side="left", padx=5)
    
    def init_admin_tab(self):
        """Initialize the admin account tab."""
        # Title
        title_label = ttk.Label(
            self.admin_tab,
            text="Administrator Account",
            style="Header.TLabel"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10), padx=10, sticky="w")
        
        # Description
        desc_label = ttk.Label(
            self.admin_tab,
            text="Create an administrator account that will be used to manage the system.",
            wraplength=600
        )
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20), padx=10, sticky="w")
        
        # Username
        username_label = ttk.Label(self.admin_tab, text="Username:")
        username_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        username_entry = ttk.Entry(
            self.admin_tab,
            textvariable=self.user_inputs['admin']['username'],
            width=30
        )
        username_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Password
        password_label = ttk.Label(self.admin_tab, text="Password:")
        password_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        password_entry = ttk.Entry(
            self.admin_tab,
            textvariable=self.user_inputs['admin']['password'],
            show="*",
            width=30
        )
        password_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # Confirm Password
        confirm_password_label = ttk.Label(self.admin_tab, text="Confirm Password:")
        confirm_password_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        confirm_password_entry = ttk.Entry(
            self.admin_tab,
            textvariable=self.user_inputs['admin']['confirm_password'],
            show="*",
            width=30
        )
        confirm_password_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        # Email
        email_label = ttk.Label(self.admin_tab, text="Email:")
        email_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        email_entry = ttk.Entry(
            self.admin_tab,
            textvariable=self.user_inputs['admin']['email'],
            width=30
        )
        email_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        
        # First Name
        first_name_label = ttk.Label(self.admin_tab, text="First Name:")
        first_name_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        
        first_name_entry = ttk.Entry(
            self.admin_tab,
            textvariable=self.user_inputs['admin']['first_name'],
            width=30
        )
        first_name_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")
        
        # Last Name
        last_name_label = ttk.Label(self.admin_tab, text="Last Name:")
        last_name_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
        
        last_name_entry = ttk.Entry(
            self.admin_tab,
            textvariable=self.user_inputs['admin']['last_name'],
            width=30
        )
        last_name_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
        
        # Password requirements
        req_label = ttk.Label(
            self.admin_tab,
            text="Password requirements: At least 8 characters, including uppercase, lowercase, and numbers.",
            wraplength=600,
            font=('Arial', 9),
            foreground='#555555'
        )
        req_label.grid(row=8, column=0, columnspan=2, padx=10, pady=(20, 10), sticky="w")
        
        # Navigation buttons
        button_frame = ttk.Frame(self.admin_tab)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        back_button = ttk.Button(
            button_frame,
            text="Back",
            command=lambda: self.go_to_tab(1)
        )
        back_button.pack(side="left", padx=5)
        
        next_button = ttk.Button(
            button_frame,
            text="Next",
            command=self.save_admin_account,
            style="Primary.TButton"
        )
        next_button.pack(side="left", padx=5)
        
    def init_finish_tab(self):
        """Initialize the finish tab."""
        # Title
        title_label = ttk.Label(
            self.finish_tab,
            text="Setup Complete",
            style="Header.TLabel"
        )
        title_label.pack(pady=(40, 20))
        
        # Description
        desc_label = ttk.Label(
            self.finish_tab,
            text=(
                "The Handyman KPI System has been successfully configured.\n\n"
                "Click 'Finish' to complete the setup and launch the application."
            ),
            wraplength=500,
            justify="center"
        )
        desc_label.pack(pady=20)
        
        # Company name
        company_frame = ttk.Frame(self.finish_tab)
        company_frame.pack(fill=tk.X, padx=20, pady=10)
        
        company_label = ttk.Label(company_frame, text="Company Name:")
        company_label.pack(side=tk.LEFT, padx=5)
        
        company_entry = ttk.Entry(
            company_frame,
            textvariable=self.user_inputs['app']['company_name'],
            width=30
        )
        company_entry.pack(side=tk.LEFT, padx=5)
        
        # Server port
        port_frame = ttk.Frame(self.finish_tab)
        port_frame.pack(fill=tk.X, padx=20, pady=10)
        
        port_label = ttk.Label(port_frame, text="Server Port:")
        port_label.pack(side=tk.LEFT, padx=5)
        
        port_entry = ttk.Entry(
            port_frame,
            textvariable=self.user_inputs['app']['port'],
            width=10
        )
        port_entry.pack(side=tk.LEFT, padx=5)
        
        # Integration options
        options_frame = ttk.LabelFrame(self.finish_tab, text="Application Integration")
        options_frame.pack(padx=20, pady=20, fill="x")
        
        desktop_check = ttk.Checkbutton(
            options_frame,
            text="Create Desktop Shortcut",
            variable=self.user_inputs['app']['create_desktop_shortcut']
        )
        desktop_check.pack(anchor="w", padx=10, pady=5)
        
        startmenu_check = ttk.Checkbutton(
            options_frame,
            text="Create Start Menu Shortcut",
            variable=self.user_inputs['app']['create_start_menu_shortcut']
        )
        startmenu_check.pack(anchor="w", padx=10, pady=5)
        
        autostart_check = ttk.Checkbutton(
            options_frame,
            text="Start Application at System Startup",
            variable=self.user_inputs['app']['auto_start']
        )
        autostart_check.pack(anchor="w", padx=10, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.finish_tab)
        button_frame.pack(pady=30)
        
        back_button = ttk.Button(
            button_frame,
            text="Back",
            command=lambda: self.go_to_tab(2)
        )
        back_button.pack(side="left", padx=5)
        
        finish_button = ttk.Button(
            button_frame,
            text="Finish",
            command=self.finish_setup,
            style="Primary.TButton"
        )
        finish_button.pack(side="left", padx=5)
    
    def go_to_tab(self, tab_index: int) -> None:
        """Navigate to a specific tab.
        
        Args:
            tab_index: Index of the tab to navigate to
        """
        # Enable the target tab
        self.notebook.tab(tab_index, state="normal")
        
        # Select the target tab
        self.notebook.select(tab_index)
    
    def update_db_fields(self) -> None:
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
    
    def browse_db_path(self) -> None:
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
    
    def test_db_connection(self) -> None:
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
    
    def save_db_config(self) -> None:
        """Save database configuration and proceed to next tab."""
        db_type = self.user_inputs['database']['type'].get()
        
        # Build database configuration
        db_config = {'type': db_type}
        
        if db_type == 'sqlite':
            db_path = self.user_inputs['database']['path'].get()
            
            if not db_path:
                messagebox.showerror("Error", "Please enter a database path")
                return
            
            db_config['path'] = db_path
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        else:
            host = self.user_inputs['database']['host'].get()
            port = self.user_inputs['database']['port'].get()
            name = self.user_inputs['database']['name'].get()
            user = self.user_inputs['database']['user'].get()
            password = self.user_inputs['database']['password'].get()
            
            if not host or not port or not name or not user:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            db_config['host'] = host
            db_config['port'] = port
            db_config['name'] = name
            db_config['user'] = user
            db_config['password'] = password
        
        # Test connection
        status, error = self.db_initializer.test_database_connection(db_config)
        
        if not status:
            if not messagebox.askyesno(
                "Connection Failed",
                f"Database connection failed: {error}\n\nProceed anyway?"
            ):
                return
        
        # Save configuration
        self.config.set_database_config(db_config)
        self.config.save()
        
        # Initialize database
        if messagebox.askyesno(
            "Initialize Database",
            "Do you want to initialize the database with default schema and data?"
        ):
            if not self.db_initializer.initialize_database(db_config):
                messagebox.showerror(
                    "Error",
                    "Failed to initialize database. You may need to initialize it manually later."
                )
        
        # Proceed to next tab
        self.go_to_tab(2)
    
    def save_admin_account(self) -> None:
        """Save admin account and proceed to next tab."""
        username = self.user_inputs['admin']['username'].get()
        password = self.user_inputs['admin']['password'].get()
        confirm_password = self.user_inputs['admin']['confirm_password'].get()
        email = self.user_inputs['admin']['email'].get()
        
        # Validate inputs
        if not username or not password or not confirm_password or not email:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return
        
        # Check password complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            messagebox.showerror(
                "Error",
                "Password must include uppercase, lowercase, and numeric characters"
            )
            return
        
        # Get database configuration
        db_config = self.config.get_database_config()
        
        # Create admin user
        if not self.db_initializer.create_admin_user(username, password, email, db_config):
            if not messagebox.askyesno(
                "Creation Failed",
                "Failed to create admin user. Proceed anyway?"
            ):
                return
        
        # Save admin configuration in settings
        self.config.set('app', 'admin_username', username)
        self.config.set('app', 'admin_email', email)
        
        # Save first and last name if provided
        first_name = self.user_inputs['admin']['first_name'].get()
        last_name = self.user_inputs['admin']['last_name'].get()
        
        if first_name:
            self.config.set('app', 'admin_first_name', first_name)
        
        if last_name:
            self.config.set('app', 'admin_last_name', last_name)
        
        self.config.save()
        
        # Proceed to next tab
        self.go_to_tab(3)
    
    def finish_setup(self) -> None:
        """Complete the setup process."""
        # Save application settings
        company_name = self.user_inputs['app']['company_name'].get()
        port = self.user_inputs['app']['port'].get()
        
        self.config.set('app', 'company_name', company_name)
        self.config.set('server', 'port', port)
        self.config.save()
        
        # Create shortcuts if requested
        app_dir = self.environment.get_app_directory()
        exe_path = os.path.join(app_dir, 'handyman_kpi.exe')
        
        # If not found, use Python script
        if not os.path.exists(exe_path):
            exe_path = os.path.join(app_dir, 'run_app.bat')
            if not os.path.exists(exe_path):
                exe_path = os.path.join(app_dir, 'app.py')
        
        # Create desktop shortcut
        if self.user_inputs['app']['create_desktop_shortcut'].get():
            self.environment.create_desktop_shortcut(
                target_path=exe_path,
                shortcut_name="Handyman KPI System",
                description="Launch Handyman KPI System"
            )
        
        # Create start menu shortcut
        if self.user_inputs['app']['create_start_menu_shortcut'].get():
            self.environment.create_start_menu_shortcut(
                target_path=exe_path,
                shortcut_name="Handyman KPI System",
                folder="Handyman KPI System",
                description="Launch Handyman KPI System"
            )
        
        # Set up auto-start if requested
        if self.user_inputs['app']['auto_start'].get():
            startup_dir = os.path.join(
                os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming')),
                'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
            )
            
            self.environment.create_start_menu_shortcut(
                target_path=exe_path,
                shortcut_name="Handyman KPI System",
                folder="Startup",
                description="Launch Handyman KPI System"
            )
        
        # Show success message
        messagebox.showinfo(
            "Setup Complete",
            "The Handyman KPI System has been successfully set up.\n\n"
            "Click OK to close the setup wizard and launch the application."
        )
        
        # Close wizard
        self.root.destroy()
        
        # Launch application
        try:
            if os.path.exists(exe_path):
                subprocess.Popen([exe_path])
            else:
                messagebox.showinfo(
                    "Application Not Found",
                    "The application executable was not found. "
                    "Please launch the application manually."
                )
        except Exception as e:
            messagebox.showerror(
                "Launch Error",
                f"Error launching application: {str(e)}"
            )
    
    def run(self) -> None:
        """Run the setup wizard."""
        self.root.mainloop()
