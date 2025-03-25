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
