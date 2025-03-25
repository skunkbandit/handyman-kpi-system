"""Logging Utilities for the KPI System Installer

This module provides standardized logging functionality for the entire installer system,
with consistent formatting, log levels, and output handling.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path


class InstallerLogger:
    """
    A specialized logger for the KPI System Installer that provides:
    - Consistent formatting
    - File and console output
    - Adjustable log levels
    - Platform-specific log paths
    """

    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, name, log_dir=None, log_level=None, console_output=True, file_output=True):
        """
        Initialize a new installer logger instance.
        
        Args:
            name (str): Name of the logger, typically the module name
            log_dir (str, optional): Directory to store log files. If None, uses platform-specific default
            log_level (int, optional): Logging level. Defaults to INFO.
            console_output (bool): Whether to output logs to console
            file_output (bool): Whether to output logs to file
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.log_level = log_level or self.DEFAULT_LOG_LEVEL
        self.logger.setLevel(self.log_level)
        self.log_dir = self._get_log_directory(log_dir)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Add handlers
        if console_output:
            self._add_console_handler()
        
        if file_output:
            self._add_file_handler()
    
    def _get_log_directory(self, log_dir=None):
        """
        Determine the appropriate log directory.
        
        Args:
            log_dir (str, optional): User-specified log directory
            
        Returns:
            Path: The log directory path
        """
        if log_dir:
            path = Path(log_dir)
        else:
            # Platform-specific default log directory
            if sys.platform == 'win32':
                path = Path(os.environ.get('APPDATA', '')) / 'HandymanKPI' / 'logs'
            elif sys.platform == 'darwin':
                path = Path.home() / 'Library' / 'Logs' / 'HandymanKPI'
            else:  # Linux and other Unix-like systems
                path = Path('/var/log/handymankpi')
                
                # Fall back to user's home directory if system dir isn't writable
                if not os.access(path.parent, os.W_OK):
                    path = Path.home() / '.handymankpi' / 'logs'
        
        # Create log directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def _add_console_handler(self):
        """Add a handler for console output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        formatter = logging.Formatter(self.DEFAULT_LOG_FORMAT, datefmt=self.LOG_DATE_FORMAT)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self):
        """Add a handler for file output"""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"installer_{today}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(self.log_level)
        formatter = logging.Formatter(self.DEFAULT_LOG_FORMAT, datefmt=self.LOG_DATE_FORMAT)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message, *args, **kwargs):
        """Log a debug message"""
        self.logger.debug(message, *args, **kwargs)
        
    def info(self, message, *args, **kwargs):
        """Log an info message"""
        self.logger.info(message, *args, **kwargs)
        
    def warning(self, message, *args, **kwargs):
        """Log a warning message"""
        self.logger.warning(message, *args, **kwargs)
        
    def error(self, message, *args, **kwargs):
        """Log an error message"""
        self.logger.error(message, *args, **kwargs)
        
    def critical(self, message, *args, **kwargs):
        """Log a critical message"""
        self.logger.critical(message, *args, **kwargs)
    
    def set_level(self, level):
        """
        Change the logging level
        
        Args:
            level: A logging level (e.g., logging.DEBUG, logging.INFO)
        """
        self.log_level = level
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


# Factory function to easily get a logger
def get_logger(name, log_dir=None, log_level=None, console_output=True, file_output=True):
    """
    Get a configured logger for the specified module.
    
    Args:
        name (str): Name of the logger, typically the module name
        log_dir (str, optional): Directory to store log files
        log_level (int, optional): Logging level
        console_output (bool): Whether to output logs to console
        file_output (bool): Whether to output logs to file
        
    Returns:
        InstallerLogger: A configured logger instance
    """
    return InstallerLogger(name, log_dir, log_level, console_output, file_output)