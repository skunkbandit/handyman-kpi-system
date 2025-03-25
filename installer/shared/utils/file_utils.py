"""
File System Utilities for the KPI System Installer

This module provides utilities for common file system operations
across different platforms, with proper error handling and logging.
"""

import os
import shutil
import tempfile
from pathlib import Path
import datetime
import json
import configparser
import time
import hashlib

from .logging_utils import get_logger
from .error_utils import InstallerError, ErrorSeverity

logger = get_logger(__name__)


def ensure_directory(directory_path, create=True, check_writeable=True):
    """
    Ensure a directory exists and is writeable.
    
    Args:
        directory_path (str or Path): Path to the directory
        create (bool): Whether to create the directory if it doesn't exist
        check_writeable (bool): Whether to check if the directory is writeable
        
    Returns:
        Path: Path object for the directory
        
    Raises:
        InstallerError: If the directory cannot be created or accessed
    """
    path = Path(directory_path)
    
    try:
        # Create directory if it doesn't exist
        if not path.exists():
            if create:
                path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {path}")
            else:
                raise InstallerError(
                    f"Directory does not exist: {path}",
                    details="The specified directory could not be found and creation was not requested."
                )
        
        # Check if it's a directory
        if not path.is_dir():
            raise InstallerError(
                f"Path exists but is not a directory: {path}",
                details="The specified path exists but is a file, not a directory."
            )
            
        # Check if the directory is writeable
        if check_writeable:
            if not os.access(path, os.W_OK):
                raise InstallerError(
                    f"Directory is not writeable: {path}",
                    details="The installer needs write access to this directory.",
                    recovery_hint="Please check permissions or choose a different directory."
                )
                
        return path
        
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to ensure directory: {path}",
            details=str(e),
            recovery_hint="Check that the path is valid and accessible."
        ) from e


def safe_copy_file(src, dest, backup=True, overwrite=True):
    """
    Safely copy a file with backup and overwrite options.
    
    Args:
        src (str or Path): Source file path
        dest (str or Path): Destination file path
        backup (bool): Whether to create a backup of the existing destination file
        overwrite (bool): Whether to overwrite the destination file if it exists
        
    Returns:
        Path: Path to the copied file
        
    Raises:
        InstallerError: If the copy operation fails
    """
    src_path = Path(src)
    dest_path = Path(dest)
    
    try:
        # Check source file
        if not src_path.exists():
            raise InstallerError(
                f"Source file does not exist: {src_path}",
                severity=ErrorSeverity.ERROR
            )
            
        if not src_path.is_file():
            raise InstallerError(
                f"Source path is not a file: {src_path}",
                severity=ErrorSeverity.ERROR
            )
            
        # Create destination directory if needed
        ensure_directory(dest_path.parent)
        
        # Check if destination exists
        if dest_path.exists():
            if not overwrite:
                logger.info(f"File {dest_path} already exists and overwrite is disabled.")
                return dest_path
                
            if backup:
                # Create backup with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = dest_path.with_suffix(f"{dest_path.suffix}.{timestamp}.bak")
                shutil.copy2(dest_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
        
        # Copy the file
        shutil.copy2(src_path, dest_path)
        logger.debug(f"Copied {src_path} to {dest_path}")
        return dest_path
        
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to copy file from {src_path} to {dest_path}",
            details=str(e)
        ) from e


def safe_move_file(src, dest, backup=True, overwrite=True):
    """
    Safely move a file with backup and overwrite options.
    
    Args:
        src (str or Path): Source file path
        dest (str or Path): Destination file path
        backup (bool): Whether to create a backup of the existing destination file
        overwrite (bool): Whether to overwrite the destination file if it exists
        
    Returns:
        Path: Path to the moved file
        
    Raises:
        InstallerError: If the move operation fails
    """
    src_path = Path(src)
    dest_path = Path(dest)
    
    try:
        # Copy the file first
        safe_copy_file(src_path, dest_path, backup, overwrite)
        
        # Delete the source file
        os.remove(src_path)
        logger.debug(f"Removed source file after move: {src_path}")
        
        return dest_path
        
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to move file from {src_path} to {dest_path}",
            details=str(e)
        ) from e


def calculate_file_hash(file_path, algorithm='sha256'):
    """
    Calculate the hash of a file using the specified algorithm.
    
    Args:
        file_path (str or Path): Path to the file
        algorithm (str): Hash algorithm to use (md5, sha1, sha256, sha512)
        
    Returns:
        str: Hexadecimal digest of the file hash
        
    Raises:
        InstallerError: If the file cannot be accessed or the hash cannot be calculated
    """
    path = Path(file_path)
    
    try:
        if not path.exists():
            raise InstallerError(f"File does not exist: {path}")
            
        if not path.is_file():
            raise InstallerError(f"Path is not a file: {path}")
            
        # Select hash algorithm
        if algorithm.lower() == 'md5':
            hash_obj = hashlib.md5()
        elif algorithm.lower() == 'sha1':
            hash_obj = hashlib.sha1()
        elif algorithm.lower() == 'sha256':
            hash_obj = hashlib.sha256()
        elif algorithm.lower() == 'sha512':
            hash_obj = hashlib.sha512()
        else:
            raise InstallerError(f"Unsupported hash algorithm: {algorithm}")
            
        # Calculate hash
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
        
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to calculate {algorithm} hash for {path}",
            details=str(e)
        ) from e
