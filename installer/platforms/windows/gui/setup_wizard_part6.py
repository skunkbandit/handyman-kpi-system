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
