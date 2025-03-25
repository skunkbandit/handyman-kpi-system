"""
File System Utilities for the KPI System Installer (Part 3)

Configuration file handling and other file utilities.
"""

import os
import shutil
import tempfile
from pathlib import Path
import datetime
import configparser
import time

from .logging_utils import get_logger
from .error_utils import InstallerError, ErrorSeverity

logger = get_logger(__name__)


def read_ini_file(file_path, encoding='utf-8'):
    """
    Read and parse an INI configuration file with proper error handling.
    
    Args:
        file_path (str or Path): Path to the file
        encoding (str): Character encoding to use
        
    Returns:
        configparser.ConfigParser: Parsed configuration
        
    Raises:
        InstallerError: If the file cannot be read or parsed
    """
    path = Path(file_path)
    
    try:
        if not path.exists():
            raise InstallerError(f"Configuration file does not exist: {path}")
            
        if not path.is_file():
            raise InstallerError(f"Path is not a file: {path}")
            
        config = configparser.ConfigParser()
        config.read(path, encoding=encoding)
        
        return config
        
    except configparser.Error as e:
        raise InstallerError(
            f"Failed to parse INI file: {path}",
            details=str(e),
            recovery_hint="The file may not be a valid INI configuration file."
        ) from e
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to read INI file: {path}",
            details=str(e)
        ) from e


def write_ini_file(file_path, config, encoding='utf-8', backup=True, overwrite=True):
    """
    Write a configuration to an INI file with proper error handling.
    
    Args:
        file_path (str or Path): Path to the file
        config (configparser.ConfigParser): Configuration to write
        encoding (str): Character encoding to use
        backup (bool): Whether to create a backup of the existing file
        overwrite (bool): Whether to overwrite the file if it exists
        
    Returns:
        Path: Path to the written file
        
    Raises:
        InstallerError: If the configuration cannot be written
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
            config.write(f)
            
        logger.debug(f"Wrote configuration to file: {path}")
        return path
        
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to write INI file: {path}",
            details=str(e)
        ) from e


def create_temp_directory(prefix='kpi_installer_'):
    """
    Create a temporary directory with proper error handling.
    
    Args:
        prefix (str): Prefix for the directory name
        
    Returns:
        Path: Path to the created temporary directory
        
    Raises:
        InstallerError: If the directory cannot be created
    """
    try:
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        logger.debug(f"Created temporary directory: {temp_dir}")
        return Path(temp_dir)
        
    except Exception as e:
        raise InstallerError(
            "Failed to create temporary directory",
            details=str(e)
        ) from e


def extract_archive(archive_path, extract_to=None, archive_type=None):
    """
    Extract an archive file (zip, tar, etc.) with proper error handling.
    
    Args:
        archive_path (str or Path): Path to the archive file
        extract_to (str or Path, optional): Directory to extract to. If None, creates a temp directory.
        archive_type (str, optional): Type of archive ('zip', 'tar', 'gztar', etc.). If None, inferred from extension.
        
    Returns:
        Path: Path to the directory containing the extracted files
        
    Raises:
        InstallerError: If the archive cannot be extracted
    """
    path = Path(archive_path)
    
    try:
        if not path.exists():
            raise InstallerError(f"Archive file does not exist: {path}")
            
        if not path.is_file():
            raise InstallerError(f"Path is not a file: {path}")
            
        # Determine archive type if not specified
        if archive_type is None:
            suffix = path.suffix.lower()
            if suffix == '.zip':
                archive_type = 'zip'
            elif suffix in ('.tar', '.gz', '.bz2', '.xz'):
                archive_type = 'tar'
                if suffix == '.gz':
                    archive_type = 'gztar'
                elif suffix == '.bz2':
                    archive_type = 'bztar'
                elif suffix == '.xz':
                    archive_type = 'xztar'
            else:
                raise InstallerError(
                    f"Could not determine archive type from extension: {suffix}",
                    recovery_hint="Please specify the archive type explicitly."
                )
        
        # Create extraction directory if needed
        if extract_to is None:
            extract_to = create_temp_directory()
        else:
            from .file_utils import ensure_directory
            extract_to = ensure_directory(extract_to)
            
        # Extract the archive
        shutil.unpack_archive(path, extract_to, archive_type)
        logger.info(f"Extracted {path} to {extract_to}")
        
        return Path(extract_to)
        
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to extract archive: {path}",
            details=str(e)
        ) from e


def create_archive(source_dir, archive_path, archive_type=None, base_dir=None):
    """
    Create an archive file (zip, tar, etc.) with proper error handling.
    
    Args:
        source_dir (str or Path): Directory to archive
        archive_path (str or Path): Path to the output archive file
        archive_type (str, optional): Type of archive ('zip', 'tar', 'gztar', etc.). If None, inferred from extension.
        base_dir (str, optional): Base directory name stored in the archive
        
    Returns:
        Path: Path to the created archive
        
    Raises:
        InstallerError: If the archive cannot be created
    """
    source = Path(source_dir)
    dest = Path(archive_path)
    
    try:
        if not source.exists():
            raise InstallerError(f"Source directory does not exist: {source}")
            
        if not source.is_dir():
            raise InstallerError(f"Source path is not a directory: {source}")
            
        # Create destination directory if needed
        from .file_utils import ensure_directory
        ensure_directory(dest.parent)
        
        # Determine archive type if not specified
        if archive_type is None:
            suffix = dest.suffix.lower()
            if suffix == '.zip':
                archive_type = 'zip'
            elif suffix == '.tar':
                archive_type = 'tar'
            elif suffix == '.gz' or suffix == '.tgz':
                archive_type = 'gztar'
            elif suffix == '.bz2' or suffix == '.tbz2':
                archive_type = 'bztar'
            elif suffix == '.xz' or suffix == '.txz':
                archive_type = 'xztar'
            else:
                raise InstallerError(
                    f"Could not determine archive type from extension: {suffix}",
                    recovery_hint="Please specify the archive type explicitly."
                )
        
        # Create the archive
        shutil.make_archive(str(dest.with_suffix('')), archive_type, source, base_dir)
        logger.info(f"Created {archive_type} archive: {dest}")
        
        return dest
        
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to create archive: {dest}",
            details=str(e)
        ) from e


def find_files(directory, pattern='*', recursive=True):
    """
    Find files matching a pattern in a directory.
    
    Args:
        directory (str or Path): Directory to search in
        pattern (str): Glob pattern for matching files
        recursive (bool): Whether to search recursively in subdirectories
        
    Returns:
        list: List of Path objects for matching files
        
    Raises:
        InstallerError: If the directory cannot be searched
    """
    path = Path(directory)
    
    try:
        if not path.exists():
            raise InstallerError(f"Directory does not exist: {path}")
            
        if not path.is_dir():
            raise InstallerError(f"Path is not a directory: {path}")
            
        # Find matching files
        if recursive:
            matches = list(path.glob(f'**/{pattern}'))
        else:
            matches = list(path.glob(pattern))
            
        # Filter out directories
        files = [f for f in matches if f.is_file()]
        
        logger.debug(f"Found {len(files)} files matching '{pattern}' in {path}")
        return files
        
    except InstallerError:
        # Re-raise installer errors
        raise
    except Exception as e:
        # Convert other exceptions to InstallerError
        raise InstallerError(
            f"Failed to search for files in {path}",
            details=str(e)
        ) from e
