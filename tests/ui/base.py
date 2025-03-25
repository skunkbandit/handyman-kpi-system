"""
Base module for UI testing with Selenium.

This module provides base classes and helper functions for UI testing
with Selenium. It sets up the WebDriver, provides common actions, and
handles test cleanup.
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from flask import url_for

# Configure logger
logger = logging.getLogger(__name__)

class UITestBase:
    """Base class for UI tests with Selenium."""
    
    def __init__(self, app, live_server, options=None):
        """
        Initialize the UI test base.
        
        Args:
            app: Flask application instance
            live_server: Live server fixture
            options (dict, optional): WebDriver options
        """
        self.app = app
        self.live_server = live_server
        self.driver = None
        self.wait = None
        self.options = options or {}
        
        # Default timeout
        self.timeout = self.options.get('timeout', 10)
        
        # Screenshot directory
        self.screenshot_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'screenshots'
        ))
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def setup(self):
        """Set up the WebDriver for testing."""
        try:
            # Setup Chrome driver (can be extended for other browsers)
            chrome_options = webdriver.ChromeOptions()
            
            # Add headless option if specified
            if self.options.get('headless', True):
                chrome_options.add_argument('--headless')
            
            # Add other common options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Initialize the driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.timeout)
            
            logger.info("WebDriver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    def teardown(self):
        """Clean up resources after testing."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    def url_for(self, endpoint, **kwargs):
        """
        Generate URL for the given endpoint.
        
        Args:
            endpoint (str): Flask endpoint
            **kwargs: Endpoint parameters
            
        Returns:
            str: Full URL
        """
        with self.app.test_request_context():
            path = url_for(endpoint, **kwargs)
            return f"{self.live_server.url}{path}"
    
    def navigate_to(self, endpoint, **kwargs):
        """
        Navigate to the specified endpoint.
        
        Args:
            endpoint (str): Flask endpoint
            **kwargs: Endpoint parameters
        """
        url = self.url_for(endpoint, **kwargs)
        self.driver.get(url)
        logger.info(f"Navigated to {url}")
    
    def wait_for_element(self, locator, locator_type=By.CSS_SELECTOR, timeout=None):
        """
        Wait for an element to be visible.
        
        Args:
            locator (str): Element locator
            locator_type: Type of locator (default: CSS_SELECTOR)
            timeout (int, optional): Timeout in seconds
            
        Returns:
            WebElement: The found element
        """
        timeout = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located((locator_type, locator)))
    
    def wait_for_clickable(self, locator, locator_type=By.CSS_SELECTOR, timeout=None):
        """
        Wait for an element to be clickable.
        
        Args:
            locator (str): Element locator
            locator_type: Type of locator (default: CSS_SELECTOR)
            timeout (int, optional): Timeout in seconds
            
        Returns:
            WebElement: The found element
        """
        timeout = timeout or self.timeout
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.element_to_be_clickable((locator_type, locator)))
    
    def fill_form(self, form_data):
        """
        Fill a form with the provided data.
        
        Args:
            form_data (dict): Dictionary mapping field names/IDs to values
        """
        for selector, value in form_data.items():
            try:
                # Handle different form elements
                element = self.driver.find_element(By.ID, selector)
                element_type = element.get_attribute('type')
                
                if element_type == 'checkbox':
                    current_state = element.is_selected()
                    if (value and not current_state) or (not value and current_state):
                        element.click()
                elif element_type == 'radio':
                    # For radio buttons, find the one with matching value
                    radio_group = self.driver.find_elements(By.NAME, element.get_attribute('name'))
                    for radio in radio_group:
                        if radio.get_attribute('value') == str(value):
                            radio.click()
                            break
                elif element.tag_name == 'select':
                    # For select elements, find option with matching value
                    from selenium.webdriver.support.ui import Select
                    select = Select(element)
                    select.select_by_value(str(value))
                else:
                    # Clear and fill text input
                    element.clear()
                    element.send_keys(value)
                
                logger.info(f"Filled form field '{selector}' with value '{value}'")
            except NoSuchElementException:
                logger.warning(f"Form field '{selector}' not found")
            except Exception as e:
                logger.error(f"Error filling form field '{selector}': {e}")
    
    def submit_form(self, form_selector='form', button_selector=None):
        """
        Submit a form.
        
        Args:
            form_selector (str): CSS selector for the form
            button_selector (str, optional): CSS selector for the submit button.
                If None, submit the form directly.
        """
        try:
            if button_selector:
                # Click the submit button
                button = self.wait_for_clickable(button_selector)
                button.click()
                logger.info(f"Clicked submit button '{button_selector}'")
            else:
                # Submit the form directly
                form = self.driver.find_element(By.CSS_SELECTOR, form_selector)
                form.submit()
                logger.info(f"Submitted form '{form_selector}'")
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            raise
    
    def take_screenshot(self, name=None):
        """
        Take a screenshot of the current page.
        
        Args:
            name (str, optional): Name for the screenshot file.
                If None, generate a name based on the current time.
                
        Returns:
            str: Path to the screenshot file
        """
        if not self.driver:
            logger.warning("Cannot take screenshot: WebDriver not initialized")
            return None
            
        try:
            # Generate filename
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            name = name or f"screenshot-{timestamp}"
            filename = f"{name}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # Take screenshot
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
    
    def check_responsive_layout(self, breakpoints=None):
        """
        Test responsive layout by resizing the browser window.
        
        Args:
            breakpoints (list, optional): List of (width, height) tuples to test.
                If None, use default breakpoints.
                
        Returns:
            list: List of dictionaries with results for each breakpoint
        """
        if not self.driver:
            logger.warning("Cannot check responsive layout: WebDriver not initialized")
            return []
            
        # Default breakpoints: Mobile, tablet, desktop
        breakpoints = breakpoints or [
            (375, 667),   # Mobile portrait
            (768, 1024),  # Tablet portrait
            (1366, 768),  # Desktop
            (1920, 1080)  # Large desktop
        ]
        
        results = []
        original_size = self.driver.get_window_size()
        
        try:
            for width, height in breakpoints:
                # Resize window
                self.driver.set_window_size(width, height)
                logger.info(f"Resized window to {width}x{height}")
                
                # Wait for any responsive adjustments
                time.sleep(1)
                
                # Take screenshot
                screenshot_name = f"responsive-{width}x{height}"
                screenshot_path = self.take_screenshot(screenshot_name)
                
                # Check for elements that should be visible/hidden at this breakpoint
                # This will depend on your specific application's responsive design
                
                results.append({
                    'width': width,
                    'height': height,
                    'screenshot': screenshot_path,
                    'elements_visible': {}  # To be filled with visibility check results
                })
            
            # Restore original window size
            self.driver.set_window_size(original_size['width'], original_size['height'])
            return results
        except Exception as e:
            logger.error(f"Error checking responsive layout: {e}")
            # Restore original window size
            self.driver.set_window_size(original_size['width'], original_size['height'])
            return []
    
    def is_element_visible(self, locator, locator_type=By.CSS_SELECTOR):
        """
        Check if an element is visible on the page.
        
        Args:
            locator (str): Element locator
            locator_type: Type of locator (default: CSS_SELECTOR)
            
        Returns:
            bool: True if the element is visible, False otherwise
        """
        try:
            element = self.driver.find_element(locator_type, locator)
            return element.is_displayed()
        except NoSuchElementException:
            return False
        except Exception as e:
            logger.error(f"Error checking element visibility: {e}")
            return False
    
    def login(self, username, password):
        """
        Log in to the application.
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            bool: True if login was successful, False otherwise
        """
        try:
            # Navigate to login page
            self.navigate_to('auth.login')
            
            # Fill login form
            self.fill_form({
                'username': username,
                'password': password
            })
            
            # Submit the form
            self.submit_form(button_selector='button[type="submit"]')
            
            # Check if login was successful
            # This will depend on your application's behavior after login
            # For example, checking for a dashboard element or a welcome message
            try:
                self.wait_for_element('.user-profile-menu', timeout=5)
                logger.info(f"Successfully logged in as {username}")
                return True
            except TimeoutException:
                logger.warning(f"Login failed for user {username}")
                return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
