"""
Error Handling Utilities for the KPI System Installer

This module provides standardized error handling, custom exceptions,
and utilities for graceful failure recovery during installation.
"""

import sys
import traceback
from enum import Enum, auto

from .logging_utils import get_logger

logger = get_logger(__name__)


class ErrorSeverity(Enum):
    """Enumeration of error severity levels"""
    WARNING = auto()     # Non-critical issues, installation can continue
    ERROR = auto()       # Serious issues, current operation should abort but installation might continue
    CRITICAL = auto()    # Fatal issues, installation should abort
    

class InstallerError(Exception):
    """Base exception class for all installer-related errors"""
    
    def __init__(self, message, severity=ErrorSeverity.ERROR, details=None, recovery_hint=None):
        """
        Initialize a new installer error.
        
        Args:
            message (str): Primary error message
            severity (ErrorSeverity): Severity level of the error
            details (str, optional): Detailed explanation of the error
            recovery_hint (str, optional): Suggestion for how to recover from the error
        """
        self.message = message
        self.severity = severity
        self.details = details
        self.recovery_hint = recovery_hint
        super().__init__(message)
    
    def __str__(self):
        """String representation of the error"""
        result = f"{self.severity.name}: {self.message}"
        if self.details:
            result += f"\nDetails: {self.details}"
        if self.recovery_hint:
            result += f"\nRecovery hint: {self.recovery_hint}"
        return result


class ConfigurationError(InstallerError):
    """Error related to configuration processing"""
    pass


class DatabaseError(InstallerError):
    """Error related to database operations"""
    pass


class EnvironmentError(InstallerError):
    """Error related to environment setup/verification"""
    pass


class GUIError(InstallerError):
    """Error related to GUI operations"""
    pass


class BuildError(InstallerError):
    """Error related to installer build process"""
    pass


class ValidationError(InstallerError):
    """Error related to input validation"""
    pass


# Error handling utility functions
def handle_exception(exc, exit_on_error=False, gui_context=None):
    """
    Central exception handler for installer operations.
    
    Args:
        exc (Exception): The exception to handle
        exit_on_error (bool): Whether to exit the application on error
        gui_context (object, optional): GUI context for displaying errors
        
    Returns:
        bool: True if the error was handled, False otherwise
    """
    if isinstance(exc, InstallerError):
        # Handle custom installer errors
        if exc.severity == ErrorSeverity.WARNING:
            logger.warning(str(exc))
            if gui_context:
                display_gui_warning(gui_context, exc)
            return True
            
        elif exc.severity == ErrorSeverity.ERROR:
            logger.error(str(exc))
            if gui_context:
                display_gui_error(gui_context, exc)
            if exit_on_error:
                sys.exit(1)
            return True
            
        elif exc.severity == ErrorSeverity.CRITICAL:
            logger.critical(str(exc))
            if gui_context:
                display_gui_critical(gui_context, exc)
            if exit_on_error:
                sys.exit(2)
            return True
    else:
        # Handle unexpected exceptions
        error_info = {
            'type': type(exc).__name__,
            'message': str(exc),
            'traceback': traceback.format_exc()
        }
        
        logger.error(f"Unexpected error: {error_info['type']}: {error_info['message']}")
        logger.debug(f"Traceback: {error_info['traceback']}")
        
        if gui_context:
            display_gui_unexpected(gui_context, error_info)
        
        if exit_on_error:
            sys.exit(3)
        
        return False


def validate_with_feedback(validation_func, value, error_message=None):
    """
    Validate a value and provide appropriate feedback.
    
    Args:
        validation_func (callable): Function that validates the value and returns bool
        value: The value to validate
        error_message (str, optional): Custom error message
        
    Returns:
        tuple: (is_valid, feedback_message)
    """
    try:
        is_valid = validation_func(value)
        if is_valid:
            return True, "Validation successful"
        else:
            msg = error_message or f"Validation failed for value: {value}"
            return False, msg
    except Exception as e:
        msg = error_message or f"Validation error: {str(e)}"
        logger.error(msg)
        return False, msg


# GUI error display functions
def display_gui_warning(gui_context, error):
    """Display a warning message in the GUI"""
    if hasattr(gui_context, 'show_warning'):
        gui_context.show_warning(error.message, error.details)
    # If no GUI context or method, do nothing


def display_gui_error(gui_context, error):
    """Display an error message in the GUI"""
    if hasattr(gui_context, 'show_error'):
        gui_context.show_error(error.message, error.details, error.recovery_hint)


def display_gui_critical(gui_context, error):
    """Display a critical error message in the GUI"""
    if hasattr(gui_context, 'show_critical_error'):
        gui_context.show_critical_error(error.message, error.details, error.recovery_hint)
    else:
        # Fall back to regular error display
        display_gui_error(gui_context, error)


def display_gui_unexpected(gui_context, error_info):
    """Display information about an unexpected error in the GUI"""
    if hasattr(gui_context, 'show_unexpected_error'):
        gui_context.show_unexpected_error(
            error_info['type'], 
            error_info['message'],
            error_info.get('traceback', '')
        )
    elif hasattr(gui_context, 'show_error'):
        # Fall back to regular error display
        gui_context.show_error(
            f"Unexpected error: {error_info['type']}",
            error_info['message']
        )
