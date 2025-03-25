#!/usr/bin/env python3
"""
Verify the installation of the Handyman KPI System.

This script performs various checks to ensure the application is installed
correctly and can function properly.
"""

import os
import sys
import sqlite3
import configparser
import importlib
import subprocess
import socket
from pathlib import Path
import webbrowser
import time

class InstallationVerifier:
    """Verify installation of the Handyman KPI System."""

    def __init__(self):
        """Initialize the verifier."""
        # Get application directory
        self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.app_dir, 'config', 'config.ini')
        self.db_dir = os.path.join(self.app_dir, 'database')
        self.python_dir = os.path.join(self.app_dir, 'python')
        
        # Status tracking
        self.issues = []
        self.print_separator()
        print("Handyman KPI System - Installation Verification")
        self.print_separator()
        print(f"Application directory: {self.app_dir}")
        print()
    
    def print_separator(self):
        """Print a separator line."""
        print("=" * 60)
    
    def check_config_file(self):
        """Check if config file exists and can be read."""
        print("Checking configuration file...")
        
        if not os.path.exists(self.config_path):
            self.issues.append("Config file not found")
            print("  [FAIL] Config file not found")
            return False
        
        try:
            config = configparser.ConfigParser()
            config.read(self.config_path)
            
            # Check if required sections exist
            required_sections = ['GENERAL', 'SERVER', 'DATABASE']
            missing_sections = [s for s in required_sections if s not in config.sections()]
            
            if missing_sections:
                self.issues.append(f"Missing config sections: {', '.join(missing_sections)}")
                print(f"  [FAIL] Missing config sections: {', '.join(missing_sections)}")
                return False
            
            print("  [OK] Config file exists and contains required sections")
            return True
        
        except Exception as e:
            self.issues.append(f"Error reading config file: {e}")
            print(f"  [FAIL] Error reading config file: {e}")
            return False
    
    def check_database(self):
        """Check if database can be accessed."""
        print("Checking database...")
        
        try:
            config = configparser.ConfigParser()
            config.read(self.config_path)
            
            db_type = config['DATABASE']['type']
            
            if db_type == 'sqlite':
                db_path = os.path.join(self.db_dir, config['DATABASE']['path'])
                
                if not os.path.exists(db_path):
                    self.issues.append("SQLite database file not found")
                    print("  [FAIL] SQLite database file not found")
                    return False
                
                # Try to connect to the database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if users table exists and has at least one user
                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='users'")
                if cursor.fetchone()[0] == 0:
                    self.issues.append("Users table not found in database")
                    print("  [FAIL] Users table not found in database")
                    conn.close()
                    return False
                
                cursor.execute("SELECT count(*) FROM users")
                user_count = cursor.fetchone()[0]
                conn.close()
                
                if user_count == 0:
                    self.issues.append("No users found in database")
                    print("  [FAIL] No users found in database")
                    return False
                
                print(f"  [OK] SQLite database exists and contains {user_count} user(s)")
                return True
            
            else:
                # For MySQL and PostgreSQL, we'll just check if the required modules are installed
                if db_type == 'mysql':
                    required_module = 'pymysql'
                elif db_type == 'postgresql':
                    required_module = 'psycopg2'
                
                try:
                    importlib.import_module(required_module)
                    print(f"  [OK] {db_type.capitalize()} support is available")
                    return True
                except ImportError:
                    self.issues.append(f"{required_module} module not found")
                    print(f"  [FAIL] {required_module} module not found")
                    return False
        
        except Exception as e:
            self.issues.append(f"Error checking database: {e}")
            print(f"  [FAIL] Error checking database: {e}")
            return False
    
    def check_python_packages(self):
        """Check if required Python packages are installed."""
        print("Checking Python packages...")
        
        required_packages = [
            'flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf',
            'werkzeug', 'jinja2', 'sqlalchemy', 'wtforms',
            'email_validator', 'weasyprint', 'xlsxwriter', 'waitress'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                importlib.import_module(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.issues.append(f"Missing Python packages: {', '.join(missing_packages)}")
            print(f"  [FAIL] Missing Python packages: {', '.join(missing_packages)}")
            return False
        
        print(f"  [OK] All required Python packages are installed")
        return True
    
    def check_port_availability(self):
        """Check if the configured port is available."""
        print("Checking port availability...")
        
        try:
            config = configparser.ConfigParser()
            config.read(self.config_path)
            
            host = config['SERVER'].get('host', '127.0.0.1')
            port = int(config['SERVER'].get('port', '8080'))
            
            # Check if port is already in use
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            try:
                s.bind((host, port))
                print(f"  [OK] Port {port} is available")
                result = True
            except socket.error:
                self.issues.append(f"Port {port} is already in use")
                print(f"  [FAIL] Port {port} is already in use")
                result = False
            finally:
                s.close()
            
            return result
        
        except Exception as e:
            self.issues.append(f"Error checking port availability: {e}")
            print(f"  [FAIL] Error checking port availability: {e}")
            return False
    
    def check_file_permissions(self):
        """Check if we have necessary file permissions."""
        print("Checking file permissions...")
        
        # List of directories to check
        directories = [
            self.app_dir,
            self.db_dir,
            os.path.join(self.app_dir, 'config')
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                self.issues.append(f"Directory not found: {directory}")
                print(f"  [FAIL] Directory not found: {directory}")
                continue
            
            # Check if we can write to the directory
            test_file = os.path.join(directory, 'test_write.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                self.issues.append(f"Cannot write to directory {directory}: {e}")
                print(f"  [FAIL] Cannot write to directory {directory}: {e}")
                return False
        
        print("  [OK] All necessary directories are writable")
        return True
    
    def run_all_checks(self):
        """Run all verification checks."""
        checks = [
            self.check_config_file,
            self.check_database,
            self.check_python_packages,
            self.check_port_availability,
            self.check_file_permissions
        ]
        
        all_passed = True
        
        for check in checks:
            passed = check()
            all_passed = all_passed and passed
            print()
        
        self.print_separator()
        
        if all_passed:
            print("All checks passed. Installation appears to be complete.")
            print("You can now run the application.")
        else:
            print("Some checks failed:")
            for issue in self.issues:
                print(f"  - {issue}")
            print("\nPlease fix these issues to ensure proper operation.")
        
        self.print_separator()
        return all_passed

if __name__ == "__main__":
    verifier = InstallationVerifier()
    verifier.run_all_checks()
