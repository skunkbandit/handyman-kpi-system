"""Setup wizard for the Handyman KPI System Windows installer.

This module provides a graphical user interface for setting up the Handyman KPI System,
including database configuration, admin account creation, and application settings.
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional, Callable

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))