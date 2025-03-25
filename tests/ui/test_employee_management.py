"""
UI tests for employee management functionality.

This module contains UI tests for the employee management interface,
including creating, viewing, editing, and deleting employees.
"""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base import UITestBase

class TestEmployeeManagement(UITestBase):
    """Test employee management UI functionality."""
    
    def setup_method(self):
        """Set up the test environment."""
        super().setup()
        # Create a test user if needed
        
    def teardown_method(self):
        """Clean up after the test."""
        super().teardown()
    
    def test_employee_list_page(self, app, live_server):
        """Test that the employee list page loads and displays correctly."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to employee list page
        self.navigate_to('employees.index')
        
        # Verify page elements
        assert "Employees" in self.driver.title
        
        # Check for employee table
        employee_table = self.wait_for_element('table.employee-table')
        assert employee_table is not None
        
        # Check for add employee button
        add_button = self.wait_for_element('.btn-add-employee')
        assert add_button is not None
        
        # Check for search functionality
        search_input = self.wait_for_element('#employee-search')
        assert search_input is not None
        
        # Take a screenshot
        self.take_screenshot('employee-list')
    
    def test_employee_creation(self, app, live_server):
        """Test creating a new employee."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to employee creation page
        self.navigate_to('employees.create')
        
        # Check form elements
        assert "Add Employee" in self.driver.title
        
        form_elements = [
            'first_name', 'last_name', 'email', 'phone', 
            'hire_date', 'tier', 'status', 'notes'
        ]
        
        for element_id in form_elements:
            assert self.is_element_visible(f'#{element_id}')
        
        # Fill in the form
        employee_data = {
            'first_name': 'Test',
            'last_name': 'Employee',
            'email': 'test.employee@example.com',
            'phone': '555-123-4567',
            'hire_date': '2025-01-15',
            'tier': 'handyman',
            'status': 'active',
            'notes': 'Test employee created for UI testing'
        }
        
        self.fill_form(employee_data)
        
        # Take a screenshot of the filled form
        self.take_screenshot('employee-create-form')
        
        # Submit the form
        self.submit_form(button_selector='button[type="submit"]')
        
        # Verify successful creation
        try:
            self.wait_for_element('.alert-success', timeout=5)
            # Check if redirected to employee list or view page
            assert "Employees" in self.driver.title or "Employee Profile" in self.driver.title
            self.take_screenshot('employee-create-success')
            return True
        except TimeoutException:
            self.take_screenshot('employee-create-error')
            assert False, "Employee creation failed"
    
    def test_employee_view(self, app, live_server):
        """Test viewing an employee profile."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to employee list
        self.navigate_to('employees.index')
        
        # Click on the first employee in the list
        try:
            employee_link = self.wait_for_element('table.employee-table tbody tr:first-child a')
            employee_name = employee_link.text
            employee_link.click()
            
            # Verify employee profile page
            self.wait_for_element('.employee-profile-header')
            assert employee_name in self.driver.page_source
            
            # Check for profile sections
            sections = [
                '.employee-info-card',
                '.employee-skills-card',
                '.employee-tools-card',
                '.employee-evaluations-card'
            ]
            
            for section in sections:
                assert self.is_element_visible(section)
            
            # Take a screenshot
            self.take_screenshot('employee-profile')
        except TimeoutException:
            self.take_screenshot('employee-list-error')
            assert False, "No employees found or could not view employee profile"
    
    def test_employee_edit(self, app, live_server):
        """Test editing an employee."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to employee list
        self.navigate_to('employees.index')
        
        # Click on the first employee in the list
        try:
            employee_link = self.wait_for_element('table.employee-table tbody tr:first-child a')
            employee_link.click()
            
            # Click on edit button
            edit_button = self.wait_for_element('.btn-edit-employee')
            edit_button.click()
            
            # Verify edit form
            assert "Edit Employee" in self.driver.title
            
            # Update some fields
            updated_data = {
                'phone': '555-987-6543',
                'status': 'inactive',
                'notes': 'Updated notes from UI test'
            }
            
            self.fill_form(updated_data)
            
            # Take a screenshot
            self.take_screenshot('employee-edit-form')
            
            # Submit the form
            self.submit_form(button_selector='button[type="submit"]')
            
            # Verify successful update
            try:
                self.wait_for_element('.alert-success', timeout=5)
                # Check if the updates are reflected
                assert updated_data['phone'] in self.driver.page_source
                self.take_screenshot('employee-edit-success')
            except TimeoutException:
                self.take_screenshot('employee-edit-error')
                assert False, "Employee update failed"
        except TimeoutException:
            self.take_screenshot('employee-list-error')
            assert False, "No employees found or could not edit employee"
    
    def test_employee_tier_change(self, app, live_server):
        """Test changing an employee's tier."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to employee list
        self.navigate_to('employees.index')
        
        # Click on the first employee in the list
        try:
            employee_link = self.wait_for_element('table.employee-table tbody tr:first-child a')
            employee_link.click()
            
            # Click on edit button
            edit_button = self.wait_for_element('.btn-edit-employee')
            edit_button.click()
            
            # Check current tier
            current_tier = self.driver.find_element(By.ID, 'tier').get_attribute('value')
            
            # Change to a different tier
            new_tier = 'craftsman' if current_tier != 'craftsman' else 'master_craftsman'
            
            self.fill_form({'tier': new_tier})
            
            # Take a screenshot
            self.take_screenshot('employee-tier-change')
            
            # Submit the form
            self.submit_form(button_selector='button[type="submit"]')
            
            # Verify successful update
            try:
                self.wait_for_element('.alert-success', timeout=5)
                # Navigate back to employee profile
                self.wait_for_element('.employee-profile-header')
                
                # Check if tier badge shows the new tier
                tier_badge = self.wait_for_element('.employee-tier-badge')
                tier_name = new_tier.replace('_', ' ').title()  # Convert to display format
                assert tier_name in tier_badge.text
                
                self.take_screenshot('employee-tier-updated')
            except TimeoutException:
                self.take_screenshot('employee-tier-error')
                assert False, "Employee tier change failed"
        except TimeoutException:
            self.take_screenshot('employee-list-error')
            assert False, "No employees found or could not edit employee"
    
    def test_employee_search(self, app, live_server):
        """Test employee search functionality."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to employee list
        self.navigate_to('employees.index')
        
        # Check if there are employees
        try:
            employee_table = self.wait_for_element('table.employee-table')
            rows_before = len(self.driver.find_elements(By.CSS_SELECTOR, 'table.employee-table tbody tr'))
            
            if rows_before == 0:
                pytest.skip("No employees to search for")
            
            # Get a name to search for
            first_employee = self.driver.find_element(By.CSS_SELECTOR, 'table.employee-table tbody tr:first-child td:nth-child(2)')
            search_term = first_employee.text.split()[0]  # Use first name
            
            # Enter search term
            search_input = self.wait_for_element('#employee-search')
            search_input.clear()
            search_input.send_keys(search_term)
            
            # Wait for search results
            time.sleep(1)  # Allow time for search to process
            
            # Check filtered results
            rows_after = len(self.driver.find_elements(By.CSS_SELECTOR, 'table.employee-table tbody tr'))
            assert rows_after <= rows_before, "Search did not filter results"
            
            # Check if search term is in results
            visible_rows = self.driver.find_elements(By.CSS_SELECTOR, 'table.employee-table tbody tr')
            for row in visible_rows:
                assert search_term in row.text, f"Search term '{search_term}' not found in row text: {row.text}"
            
            # Take a screenshot
            self.take_screenshot('employee-search-results')
            
            # Clear search
            search_input.clear()
            time.sleep(1)  # Allow time for search to reset
            
            # Verify all results are shown again
            rows_after_clear = len(self.driver.find_elements(By.CSS_SELECTOR, 'table.employee-table tbody tr'))
            assert rows_after_clear == rows_before, "Clearing search did not restore original results"
            
        except TimeoutException:
            self.take_screenshot('employee-search-error')
            assert False, "Could not search for employees"
    
    def test_responsive_employee_list(self, app, live_server):
        """Test responsive design of employee list page."""
        # Log in as admin
        self.login('admin', 'admin123')
        
        # Navigate to employee list
        self.navigate_to('employees.index')
        
        # Check responsive layout
        results = self.check_responsive_layout()
        
        # Verify that the table is visible at all breakpoints
        for result in results:
            # Check screenshot path
            assert result['screenshot'] is not None, f"Screenshot failed for {result['width']}x{result['height']}"
            
            # Mobile view might show a different layout
            if result['width'] < 768:
                # Check if mobile card view is used instead of table
                self.driver.set_window_size(result['width'], result['height'])
                assert (self.is_element_visible('table.employee-table') or 
                        self.is_element_visible('.employee-card-view')), "Employee list not visible on mobile"
            else:
                # Larger screens should show the table
                self.driver.set_window_size(result['width'], result['height'])
                assert self.is_element_visible('table.employee-table'), "Employee table not visible on larger screens"
