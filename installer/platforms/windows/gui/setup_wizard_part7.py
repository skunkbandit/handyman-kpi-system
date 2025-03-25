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
        
        # Create admin user
        if not self.db_initializer.create_admin_user(username, password, email):
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
