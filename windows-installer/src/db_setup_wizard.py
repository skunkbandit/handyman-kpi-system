#!/usr/bin/env python3
"""
Database Setup Wizard for the Handyman KPI System.

This script provides a GUI for setting up the database connection
on first run of the application.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import configparser
import subprocess
from pathlib import Path

# Add the application directory to the Python path
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(APP_DIR, 'app'))

# Configuration file path
CONFIG_FILE = os.path.join(APP_DIR, 'config', 'config.ini')
CONFIG_DIR = os.path.dirname(CONFIG_FILE)

class DatabaseSetupWizard:
    """
    GUI wizard for database setup.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Handyman KPI System - Database Setup")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Add a nice icon if available
        try:
            self.root.iconbitmap(os.path.join(APP_DIR, 'resources', 'icon.ico'))
        except:
            pass  # Icon not available, use default
        
        # Configuration file path
        self.config_path = CONFIG_FILE
        
        # Create config if it doesn't exist
        self.config = configparser.ConfigParser()
        
        # Set default config values
        self.config['GENERAL'] = {
            'app_name': 'Handyman KPI System',
            'app_version': '1.0.0',
            'debug': 'False'
        }
        
        self.config['SERVER'] = {
            'host': '127.0.0.1',
            'port': '8080'
        }
        
        self.config['DATABASE'] = {
            'type': 'sqlite',
            'path': 'kpi_system.db'
        }
        
        # Create database directory
        self.db_dir = os.path.join(APP_DIR, 'database')
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        
        # Variables
        self.db_type = tk.StringVar(value="sqlite")
        self.db_host = tk.StringVar(value="localhost")
        self.db_port = tk.StringVar(value="3306")  # MySQL default
        self.db_name = tk.StringVar(value="handyman_kpi")
        self.db_user = tk.StringVar(value="")
        self.db_password = tk.StringVar(value="")
        self.admin_username = tk.StringVar(value="admin")
        self.admin_password = tk.StringVar(value="")
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """
        Create the wizard interface.
        """
        # Main frame with notebook (tabs)
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a notebook with tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Welcome tab
        welcome_frame = ttk.Frame(notebook, padding=10)
        notebook.add(welcome_frame, text="Welcome")
        
        # Database tab
        db_frame = ttk.Frame(notebook, padding=10)
        notebook.add(db_frame, text="Database")
        
        # Admin tab
        admin_frame = ttk.Frame(notebook, padding=10)
        notebook.add(admin_frame, text="Admin Account")
        
        # Summary tab
        summary_frame = ttk.Frame(notebook, padding=10)
        notebook.add(summary_frame, text="Summary")
        
        # Configure welcome tab
        ttk.Label(
            welcome_frame, 
            text="Welcome to the Handyman KPI System Setup",
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        ttk.Label(
            welcome_frame,
            text="This wizard will help you set up the database connection and admin account.",
            wraplength=500
        ).pack(pady=10)
        
        ttk.Label(
            welcome_frame,
            text="For most users, we recommend using SQLite which requires no additional setup.",
            wraplength=500
        ).pack(pady=10)
        
        ttk.Label(
            welcome_frame,
            text="If you need multi-user support or have an existing database server, you can configure MySQL or PostgreSQL connections.",
            wraplength=500
        ).pack(pady=10)
        
        ttk.Label(
            welcome_frame,
            text="Click Next to continue.",
            wraplength=500
        ).pack(pady=20)
        
        # Configure database tab
        ttk.Label(
            db_frame, 
            text="Database Configuration",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Database type selection
        ttk.Label(db_frame, text="Database Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        db_type_frame = ttk.Frame(db_frame)
        db_type_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(
            db_type_frame, 
            text="SQLite (Recommended for single-user)",
            variable=self.db_type, 
            value="sqlite",
            command=self.toggle_db_options
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            db_type_frame, 
            text="MySQL",
            variable=self.db_type, 
            value="mysql",
            command=self.toggle_db_options
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            db_type_frame, 
            text="PostgreSQL",
            variable=self.db_type, 
            value="postgresql",
            command=self.toggle_db_options
        ).pack(anchor=tk.W)
        
        # SQLite options
        self.sqlite_frame = ttk.LabelFrame(db_frame, text="SQLite Configuration")
        self.sqlite_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        ttk.Label(
            self.sqlite_frame,
            text="SQLite database will be created automatically in the application folder.",
            wraplength=500
        ).pack(pady=10)
        
        # MySQL/PostgreSQL options
        self.remote_db_frame = ttk.LabelFrame(db_frame, text="Database Connection Details")
        self.remote_db_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # Host
        ttk.Label(self.remote_db_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(self.remote_db_frame, textvariable=self.db_host, width=30).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Port
        ttk.Label(self.remote_db_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(self.remote_db_frame, textvariable=self.db_port, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Database name
        ttk.Label(self.remote_db_frame, text="Database Name:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(self.remote_db_frame, textvariable=self.db_name, width=30).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Username
        ttk.Label(self.remote_db_frame, text="Username:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(self.remote_db_frame, textvariable=self.db_user, width=30).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Password
        ttk.Label(self.remote_db_frame, text="Password:").grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(self.remote_db_frame, textvariable=self.db_password, show="*", width=30).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Test connection button
        ttk.Button(
            db_frame, 
            text="Test Connection", 
            command=self.test_connection
        ).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Configure admin tab
        ttk.Label(
            admin_frame, 
            text="Administrator Account Setup",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        ttk.Label(
            admin_frame,
            text="Please create an administrator account for the system.",
            wraplength=500
        ).grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Admin username
        ttk.Label(admin_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(admin_frame, textvariable=self.admin_username, width=30).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Admin password
        ttk.Label(admin_frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(admin_frame, textvariable=self.admin_password, show="*", width=30).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Password requirements note
        ttk.Label(
            admin_frame,
            text="Note: Password must be at least 8 characters long and include a combination of letters, numbers, and special characters.",
            wraplength=500,
            font=("Arial", 8)
        ).grid(row=4, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        # Configure summary tab
        ttk.Label(
            summary_frame, 
            text="Setup Summary",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, pady=10, sticky=tk.W)
        
        # Summary text
        self.summary_text = tk.Text(summary_frame, width=60, height=15, wrap=tk.WORD)
        self.summary_text.grid(row=1, column=0, pady=10, sticky=tk.W)
        self.summary_text.config(state=tk.DISABLED)
        
        # Navigation buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.prev_button = ttk.Button(
            button_frame, 
            text="Previous",
            command=lambda: notebook.select(notebook.index(notebook.select()) - 1)
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.prev_button.config(state=tk.DISABLED)  # Disabled on first tab
        
        self.next_button = ttk.Button(
            button_frame, 
            text="Next",
            command=lambda: self.next_tab(notebook)
        )
        self.next_button.pack(side=tk.RIGHT, padx=5)
        
        # Bind tab change event to update buttons
        notebook.bind("<<NotebookTabChanged>>", lambda event: self.update_buttons(notebook))
        
        # Initialize UI state
        self.toggle_db_options()
    
    def toggle_db_options(self):
        """
        Show/hide database options based on selected database type.
        """
        if self.db_type.get() == "sqlite":
            self.sqlite_frame.grid()
            self.remote_db_frame.grid_remove()
            # Update port for when switching back
            if self.db_type.get() == "postgresql":
                self.db_port.set("5432")
            else:
                self.db_port.set("3306")
        else:
            self.sqlite_frame.grid_remove()
            self.remote_db_frame.grid()
            # Set appropriate default port
            if self.db_type.get() == "postgresql":
                self.db_port.set("5432")
            else:
                self.db_port.set("3306")
    
    def update_buttons(self, notebook):
        """
        Update button states based on current tab.
        """
        current_tab = notebook.index(notebook.select())
        
        # Enable/disable Previous button
        if current_tab == 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)
        
        # Update Next button text on last tab
        if current_tab == notebook.index("end") - 1:
            self.next_button.config(text="Finish", command=self.save_config)
        else:
            self.next_button.config(text="Next", command=lambda: self.next_tab(notebook))
    
    def next_tab(self, notebook):
        """
        Handle Next button click.
        """
        current_tab = notebook.index(notebook.select())
        
        # Validate current tab before proceeding
        if current_tab == 1:  # Database tab
            if not self.validate_database_tab():
                return
        elif current_tab == 2:  # Admin tab
            if not self.validate_admin_tab():
                return
        
        # If it's the last tab before Summary, update summary
        if current_tab == 2:
            self.update_summary()
        
        # Go to next tab
        notebook.select(current_tab + 1)
    
    def validate_database_tab(self):
        """
        Validate database configuration inputs.
        """
        if self.db_type.get() != "sqlite":
            # Check required fields for MySQL/PostgreSQL
            if not self.db_host.get().strip():
                messagebox.showerror("Validation Error", "Database host is required.")
                return False
            
            if not self.db_port.get().strip():
                messagebox.showerror("Validation Error", "Database port is required.")
                return False
            
            if not self.db_name.get().strip():
                messagebox.showerror("Validation Error", "Database name is required.")
                return False
            
            if not self.db_user.get().strip():
                messagebox.showerror("Validation Error", "Database username is required.")
                return False
        
        return True
    
    def validate_admin_tab(self):
        """
        Validate admin account inputs.
        """
        if not self.admin_username.get().strip():
            messagebox.showerror("Validation Error", "Admin username is required.")
            return False
        
        if not self.admin_password.get().strip():
            messagebox.showerror("Validation Error", "Admin password is required.")
            return False
        
        if len(self.admin_password.get()) < 8:
            messagebox.showerror("Validation Error", "Password must be at least 8 characters long.")
            return False
        
        return True
    
    def update_summary(self):
        """
        Update the summary text with configured options.
        """
        # Enable text widget for editing
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        # Add database configuration summary
        self.summary_text.insert(tk.END, "Database Configuration:\n\n")
        self.summary_text.insert(tk.END, f"Database Type: {self.db_type.get()}\n")
        
        if self.db_type.get() == "sqlite":
            self.summary_text.insert(tk.END, "SQLite database will be created in the application folder.\n")
        else:
            self.summary_text.insert(tk.END, f"Host: {self.db_host.get()}\n")
            self.summary_text.insert(tk.END, f"Port: {self.db_port.get()}\n")
            self.summary_text.insert(tk.END, f"Database Name: {self.db_name.get()}\n")
            self.summary_text.insert(tk.END, f"Username: {self.db_user.get()}\n")
            self.summary_text.insert(tk.END, f"Password: {'*' * len(self.db_password.get())}\n")
        
        # Add admin account summary
        self.summary_text.insert(tk.END, "\nAdmin Account:\n\n")
        self.summary_text.insert(tk.END, f"Username: {self.admin_username.get()}\n")
        self.summary_text.insert(tk.END, f"Password: {'*' * len(self.admin_password.get())}\n")
        
        # Disable text widget
        self.summary_text.config(state=tk.DISABLED)
    
    def test_connection(self):
        """
        Test database connection based on selected type and parameters.
        """
        db_type = self.db_type.get()
        
        try:
            if db_type == "sqlite":
                # Create database directory if it doesn't exist
                if not os.path.exists(self.db_dir):
                    os.makedirs(self.db_dir)
                
                # Test SQLite connection
                db_path = os.path.join(self.db_dir, 'kpi_system.db')
                conn = sqlite3.connect(db_path)
                conn.close()
                messagebox.showinfo("Connection Test", "SQLite connection successful!")
                
            elif db_type == "mysql":
                # Try to import MySQL module
                try:
                    import pymysql
                except ImportError:
                    messagebox.showerror("Module Error", "PyMySQL module not found. Please install it with 'pip install pymysql'.")
                    return
                
                # Test MySQL connection
                conn = pymysql.connect(
                    host=self.db_host.get(),
                    port=int(self.db_port.get()),
                    user=self.db_user.get(),
                    password=self.db_password.get(),
                    db=self.db_name.get()
                )
                conn.close()
                messagebox.showinfo("Connection Test", "MySQL connection successful!")
                
            elif db_type == "postgresql":
                # Try to import PostgreSQL module
                try:
                    import psycopg2
                except ImportError:
                    messagebox.showerror("Module Error", "psycopg2 module not found. Please install it with 'pip install psycopg2-binary'.")
                    return
                
                # Test PostgreSQL connection
                conn = psycopg2.connect(
                    host=self.db_host.get(),
                    port=int(self.db_port.get()),
                    user=self.db_user.get(),
                    password=self.db_password.get(),
                    dbname=self.db_name.get()
                )
                conn.close()
                messagebox.showinfo("Connection Test", "PostgreSQL connection successful!")
                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database: {str(e)}")
    
    def save_config(self):
        """
        Save configuration and initialize the database.
        """
        # Ensure config directory exists
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        # Set database configuration
        db_type = self.db_type.get()
        self.config['DATABASE']['type'] = db_type
        
        if db_type == "sqlite":
            self.config['DATABASE']['path'] = 'kpi_system.db'
        else:
            self.config['DATABASE']['host'] = self.db_host.get()
            self.config['DATABASE']['port'] = self.db_port.get()
            self.config['DATABASE']['name'] = self.db_name.get()
            self.config['DATABASE']['user'] = self.db_user.get()
            self.config['DATABASE']['password'] = self.db_password.get()
        
        # Set admin account info in a separate section for database initialization
        self.config['ADMIN'] = {
            'username': self.admin_username.get(),
            'password': self.admin_password.get()
        }
        
        # Write config file
        with open(self.config_path, 'w') as f:
            self.config.write(f)
        
        # Initialize database
        try:
            self.initialize_database()
            messagebox.showinfo("Setup Complete", 
                               "Configuration saved successfully. The application will now start.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Setup Error", f"Failed to initialize database: {str(e)}")
    
    def initialize_database(self):
        """
        Initialize database based on selected type.
        """
        # Call the database initialization script with the config file path
        script_path = os.path.join(APP_DIR, 'scripts', 'init_database.py')
        
        # Make sure script path exists
        if not os.path.exists(script_path):
            # Try to find it in the repo structure
            alt_script_path = os.path.join(APP_DIR, 'src', 'scripts', 'init_database.py')
            if os.path.exists(alt_script_path):
                script_path = alt_script_path
            else:
                raise FileNotFoundError(f"Database initialization script not found at {script_path}")
        
        # Run the script with the config file path
        subprocess.run([sys.executable, script_path, '--config', self.config_path], check=True)

def run_wizard():
    """
    Run the database setup wizard.
    """
    root = tk.Tk()
    app = DatabaseSetupWizard(root)
    root.mainloop()

if __name__ == "__main__":
    run_wizard()
