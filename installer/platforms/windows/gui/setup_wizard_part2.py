    def setup_styles(self):
        """Set up styles for the wizard."""
        style = ttk.Style()
        
        # Configure the notebook style
        style.configure('TNotebook', tabposition='n')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10))
        
        # Configure the frame style
        style.configure('TFrame', background='#f0f0f0')
        
        # Configure the label style
        style.configure('TLabel', font=('Arial', 10), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background='#f0f0f0')
        style.configure('Subheader.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        
        # Configure the button style
        style.configure('TButton', font=('Arial', 10))
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
    
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
        
        # Company logo
        try:
            logo_path = os.path.join(self.environment.get_app_directory(), 'resources', 'logo.png')
            if os.path.exists(logo_path):
                logo_image = tk.PhotoImage(file=logo_path)
                logo_label = ttk.Label(self.welcome_tab, image=logo_image)
                logo_label.image = logo_image  # Keep a reference to avoid garbage collection
                logo_label.pack(pady=20)
        except Exception:
            pass
        
        # Description
        desc_label = ttk.Label(
            self.welcome_tab,
            text=(
                "This wizard will guide you through the setup process for the "
                "Handyman KPI System. You will configure the database and create "
                "an administrator account.\n\n"
                "Click 'Next' to begin."
            ),
            wraplength=500,
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
