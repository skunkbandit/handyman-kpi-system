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
