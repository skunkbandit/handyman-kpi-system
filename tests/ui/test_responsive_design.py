"""
UI tests for responsive design across the application.

This module tests that the application's responsive design works correctly
on various screen sizes (mobile, tablet, desktop).
"""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base import UITestBase

class TestResponsiveDesign(UITestBase):
    """Test the responsive design of the application."""
    
    def setup_method(self):
        """Set up the test environment."""
        super().setup()
    
    def teardown_method(self):
        """Clean up after the test."""
        super().teardown()
    
    def test_dashboard_responsive(self, app, live_server):
        """Test that the dashboard is responsive across different screen sizes."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to dashboard
        self.navigate_to('dashboard.index')
        
        # Define breakpoints to test
        breakpoints = [
            (375, 667),    # Mobile portrait
            (768, 1024),   # Tablet portrait
            (1366, 768),   # Laptop
            (1920, 1080)   # Large desktop
        ]
        
        # Test each breakpoint
        for width, height in breakpoints:
            self.driver.set_window_size(width, height)
            time.sleep(1)  # Allow time for responsive adjustments
            
            # Take screenshot
            self.take_screenshot(f"dashboard-{width}x{height}")
            
            # Check that core elements are visible
            assert self.is_element_visible('.dashboard-stats')
            assert self.is_element_visible('.chart-container')
            
            # On mobile, check if the sidebar collapses
            if width < 768:
                # Sidebar should be collapsed or hidden
                assert not self.is_element_visible('.sidebar.expanded') or not self.is_element_visible('.sidebar')
                
                # Menu toggle should be visible
                assert self.is_element_visible('.menu-toggle')
                
                # Click menu toggle to expand sidebar
                menu_toggle = self.driver.find_element(By.CSS_SELECTOR, '.menu-toggle')
                menu_toggle.click()
                time.sleep(0.5)
                
                # Now sidebar should be visible
                assert self.is_element_visible('.sidebar.expanded') or self.is_element_visible('.sidebar.show')
                self.take_screenshot(f"dashboard-menu-open-{width}x{height}")
            else:
                # On larger screens, sidebar should be visible by default
                assert self.is_element_visible('.sidebar')
    
    def test_employee_list_responsive(self, app, live_server):
        """Test that the employee list page is responsive."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to employee list
        self.navigate_to('employees.index')
        
        # Test on different screen sizes
        breakpoints = [
            (375, 667),    # Mobile portrait
            (768, 1024),   # Tablet portrait
            (1366, 768),   # Laptop
            (1920, 1080)   # Large desktop
        ]
        
        for width, height in breakpoints:
            self.driver.set_window_size(width, height)
            time.sleep(1)
            
            self.take_screenshot(f"employee-list-{width}x{height}")
            
            # Table or card view should be visible
            assert self.is_element_visible('table.employee-table') or self.is_element_visible('.employee-card-view')
            
            # On small screens, check if card view is used instead of table
            if width < 768:
                # Card view might be shown instead of table
                if self.is_element_visible('.employee-card-view'):
                    # Check card elements
                    assert self.is_element_visible('.employee-card')
                elif self.is_element_visible('table.employee-table'):
                    # Or table might be horizontally scrollable
                    assert self.is_element_visible('.table-responsive')
            else:
                # On larger screens, full table should be visible
                assert self.is_element_visible('table.employee-table')
    
    def test_forms_responsive(self, app, live_server):
        """Test that forms are responsive and usable on different screen sizes."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to employee creation form
        self.navigate_to('employees.create')
        
        # Test on different screen sizes
        breakpoints = [
            (375, 667),    # Mobile portrait
            (768, 1024),   # Tablet portrait
            (1366, 768)    # Laptop
        ]
        
        for width, height in breakpoints:
            self.driver.set_window_size(width, height)
            time.sleep(1)
            
            self.take_screenshot(f"employee-form-{width}x{height}")
            
            # Form elements should be visible and properly sized
            form = self.wait_for_element('form')
            assert form is not None
            
            # Check critical form fields
            assert self.is_element_visible('#first_name')
            assert self.is_element_visible('#last_name')
            assert self.is_element_visible('#tier')
            
            # On mobile, form should stack vertically
            if width < 768:
                # Get a form group element
                form_group = self.driver.find_element(By.CSS_SELECTOR, '.form-group')
                
                # Check that its width is close to full width
                # We'll look at the width ratio between form group and form
                form_width = form.size['width']
                group_width = form_group.size['width']
                
                # On mobile, the ratio should be close to 1 (stacked layout)
                # Allow some margin for padding/margins
                ratio = group_width / form_width
                assert ratio > 0.9, f"Form not properly stacked on mobile (width ratio: {ratio})"
    
    def test_navigation_responsive(self, app, live_server):
        """Test that navigation elements are responsive and adapt to screen size."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Test on different screen sizes
        breakpoints = [
            (375, 667),    # Mobile portrait
            (768, 1024),   # Tablet portrait
            (1366, 768)    # Laptop
        ]
        
        for width, height in breakpoints:
            self.driver.set_window_size(width, height)
            time.sleep(1)
            
            self.take_screenshot(f"navigation-{width}x{height}")
            
            # Navigation should always be accessible
            assert self.is_element_visible('nav') or self.is_element_visible('.navbar')
            
            # On mobile, check for responsive behavior
            if width < 768:
                # If there's a burger menu, it should be visible
                if self.is_element_visible('.navbar-toggler'):
                    toggler = self.driver.find_element(By.CSS_SELECTOR, '.navbar-toggler')
                    
                    # Nav links might be collapsed
                    nav_links_visible = self.is_element_visible('.navbar-collapse.show')
                    if not nav_links_visible:
                        # Click toggler to expand
                        toggler.click()
                        time.sleep(0.5)
                        
                        # Now links should be visible
                        assert self.is_element_visible('.navbar-collapse.show') or self.is_element_visible('.navbar-nav')
                        self.take_screenshot(f"navigation-expanded-{width}x{height}")
    
    def test_data_tables_responsive(self, app, live_server):
        """Test that data tables are responsive and adapt to screen size."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to evaluations list
        self.navigate_to('evaluations.index')
        
        # Test on different screen sizes
        breakpoints = [
            (375, 667),    # Mobile portrait
            (768, 1024),   # Tablet portrait
            (1366, 768)    # Laptop
        ]
        
        for width, height in breakpoints:
            self.driver.set_window_size(width, height)
            time.sleep(1)
            
            self.take_screenshot(f"data-table-{width}x{height}")
            
            # Data should be visible in some form
            visible = (
                self.is_element_visible('table') or 
                self.is_element_visible('.data-cards') or
                self.is_element_visible('.table-responsive')
            )
            assert visible, "Data not visible at this resolution"
            
            # On mobile, tables might become scrollable horizontally
            if width < 768:
                if self.is_element_visible('table'):
                    # Table should be in a responsive container
                    parent_elements = self.driver.find_elements(
                        By.XPATH, 
                        "//table/ancestor::*[contains(@class, 'table-responsive') or contains(@class, 'overflow-auto')]"
                    )
                    assert len(parent_elements) > 0, "Table not in responsive container on mobile"
