"""
File System Utilities for the KPI System Installer (Part 2)

Additional file operation utilities for the installer system.
"""

import os
import shutil
import tempfile
from pathlib import Path
import datetime
import json
import configparser
import time

from .logging_utils import get_logger
from .error_utils import InstallerError, ErrorSeverity

logger = get_logger(__name__)


def read_text_file(file_path, encoding='utf-8'):
    """
    Read a text file with proper error handling.
    
    Args:
        file_path (str or Path): Path to the file
        encoding (str): Character encoding to use
        
    Returns:
        str: Contents of the file
        
    Raises:
        InstallerError: If the file cannot be read
    """
    path = Path(file_path)
    
    try:
        if not path.exists():
            raise InstallerError(f"File does not exist: {path}")
            
        if not path.is_file():
            raise InstallerError(f"Path is not a file: {path}")
            
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
            
    except UnicodeDecodeError as e:
        raise InstallerError(
            f"Failed to decode file {path} with encoding {encoding}",
            details=str(e),
            recovery_hint="The file may be using a different character encoding."
        ) from e
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to read file: {path}",
            details=str(e)
        ) from e


def write_text_file(file_path, content, encoding='utf-8', backup=True, overwrite=True):
    """
    Write text to a file with proper error handling.
    
    Args:
        file_path (str or Path): Path to the file
        content (str): Content to write
        encoding (str): Character encoding to use
        backup (bool): Whether to create a backup of the existing file
        overwrite (bool): Whether to overwrite the file if it exists
        
    Returns:
        Path: Path to the written file
        
    Raises:
        InstallerError: If the file cannot be written
    """
    path = Path(file_path)
    
    try:
        # Create destination directory if needed
        from .file_utils import ensure_directory
        ensure_directory(path.parent)
        
        # Check if file exists
        if path.exists() and path.is_file():
            if not overwrite:
                logger.info(f"File {path} already exists and overwrite is disabled.")
                return path
                
            if backup:
                # Create backup with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = path.with_suffix(f"{path.suffix}.{timestamp}.bak")
                shutil.copy2(path, backup_path)
                logger.info(f"Created backup: {backup_path}")
        
        # Write the file
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
            
        logger.debug(f"Wrote content to file: {path}")
        return path
        
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to write to file: {path}",
            details=str(e)
        ) from e


def read_json_file(file_path, encoding='utf-8'):
    """
    Read and parse a JSON file with proper error handling.
    
    Args:
        file_path (str or Path): Path to the file
        encoding (str): Character encoding to use
        
    Returns:
        dict or list: Parsed JSON content
        
    Raises:
        InstallerError: If the file cannot be read or parsed
    """
    try:
        content = read_text_file(file_path, encoding)
        return json.loads(content)
        
    except json.JSONDecodeError as e:
        raise InstallerError(
            f"Failed to parse JSON file: {file_path}",
            details=str(e),
            recovery_hint="The file may not contain valid JSON data."
        ) from e
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to read JSON file: {file_path}",
            details=str(e)
        ) from e


def write_json_file(file_path, data, encoding='utf-8', indent=2, backup=True, overwrite=True):
    """
    Write data to a JSON file with proper error handling.
    
    Args:
        file_path (str or Path): Path to the file
        data (dict or list): Data to write as JSON
        encoding (str): Character encoding to use
        indent (int): Number of spaces for indentation
        backup (bool): Whether to create a backup of the existing file
        overwrite (bool): Whether to overwrite the file if it exists
        
    Returns:
        Path: Path to the written file
        
    Raises:
        InstallerError: If the data cannot be written
    """
    try:
        # Convert data to JSON string
        json_content = json.dumps(data, indent=indent, ensure_ascii=False)
        
        # Write to file
        return write_text_file(file_path, json_content, encoding, backup, overwrite)
        
    except TypeError as e:
        raise InstallerError(
            f"Failed to serialize data to JSON",
            details=str(e),
            recovery_hint="The data may contain types that cannot be serialized to JSON."
        ) from e
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to write JSON file: {file_path}",
            details=str(e)
        ) from e
