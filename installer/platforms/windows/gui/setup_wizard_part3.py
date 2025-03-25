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
