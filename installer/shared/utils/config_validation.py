"""Configuration Validation Utilities for the KPI System Installer

This module provides utilities for validating configuration files and settings.
"""

from .logging_utils import get_logger

logger = get_logger(__name__)


def validate_config_file(config_dict, required_sections, required_keys=None):
    """
    Validate a configuration dictionary against required sections and keys.
    
    Args:
        config_dict (dict): Configuration dictionary to validate
        required_sections (list): List of section names that must be present
        required_keys (dict, optional): Dictionary mapping section names to lists of required keys
        
    Returns:
        tuple: (is_valid, errors) where errors is a list of validation errors
    """
    errors = []
    
    try:
        # Check required sections
        for section in required_sections:
            if section not in config_dict:
                errors.append(f"Missing required section: {section}")
                
        # Check required keys in each section
        if required_keys:
            for section, keys in required_keys.items():
                if section in config_dict:
                    for key in keys:
                        if key not in config_dict[section]:
                            errors.append(f"Missing required key '{key}' in section '{section}'")
        
        # Return validation result
        is_valid = len(errors) == 0
        return is_valid, errors
        
    except Exception as e:
        # Log but don't raise; return False with errors
        logger.error(f"Error validating configuration: {e}")
        errors.append("Internal validation error")
        return False, errors


def get_with_default(config_dict, section, key, default=None):
    """
    Get a configuration value with a default if not found.
    
    Args:
        config_dict (dict): Configuration dictionary
        section (str): Section name
        key (str): Key name
        default: Default value to return if not found
        
    Returns:
        The configuration value or the default
    """
    try:
        return config_dict.get(section, {}).get(key, default)
    except Exception:
        return default