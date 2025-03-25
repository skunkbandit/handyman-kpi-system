#!/usr/bin/env python3
"""
Initialize configuration file from template.

This script creates a new configuration file from a template,
replacing placeholder values with appropriate values.
"""

import os
import sys
import secrets
import configparser
from pathlib import Path

def get_script_dir():
    """Get the directory containing this script."""
    return os.path.dirname(os.path.abspath(__file__))

def get_app_dir():
    """Get the application directory."""
    return os.path.dirname(os.path.dirname(get_script_dir()))

def init_config():
    """Initialize configuration file from template."""
    app_dir = get_app_dir()
    config_dir = os.path.join(app_dir, 'config')
    template_path = os.path.join(config_dir, 'config.ini.template')
    config_path = os.path.join(config_dir, 'config.ini')
    
    # Check if template exists
    if not os.path.exists(template_path):
        print(f"Error: Template file not found: {template_path}")
        return False
    
    # Check if config already exists
    if os.path.exists(config_path):
        # Config already exists, no need to create it
        return True
    
    try:
        # Read template
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Replace placeholders
        content = template_content.replace('${RANDOM_SECRET_KEY}', secrets.token_hex(32))
        
        # Write config file
        with open(config_path, 'w') as f:
            f.write(content)
        
        print(f"Configuration file created: {config_path}")
        return True
        
    except Exception as e:
        print(f"Error creating configuration file: {e}")
        return False

if __name__ == "__main__":
    init_config()
