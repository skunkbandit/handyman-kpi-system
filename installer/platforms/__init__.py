# Platform-specific installer components
import os
import sys
import platform

# Import platform-specific environment handlers
if platform.system().lower() == 'windows':
    from .windows import WindowsEnvironment as PlatformEnvironment
else:
    # Default to base environment for unsupported platforms
    from ..core.environment import Environment as PlatformEnvironment

# Export PlatformEnvironment for easy import
__all__ = ['PlatformEnvironment']
