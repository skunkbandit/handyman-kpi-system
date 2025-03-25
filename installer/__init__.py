# Handyman KPI System Installer Package

"""
Installer package for the Handyman KPI System.

This package provides a modular design for installing the Handyman KPI System
across multiple platforms while maintaining a consistent experience.
"""

from .platforms import PlatformEnvironment
from .core.config import InstallerConfig
from .core.database import DatabaseInitializer
from .core.verification import InstallationVerifier

__version__ = '1.0.0'
__author__ = 'Handyman KPI System Team'

__all__ = [
    'PlatformEnvironment',
    'InstallerConfig',
    'DatabaseInitializer',
    'InstallationVerifier',
]
