"""
Main entry point for the Handyman KPI System Installer.

This module provides the main entry point for the installer, which can be run as
a Python module: `python -m installer [command] [options]`.
"""
import os
import sys
import argparse
from .core.config import InstallerConfig

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Handyman KPI System Installer")
    
    # Common arguments
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Windows installer
    windows_parser = subparsers.add_parser("windows", help="Build Windows installer")
    windows_parser.add_argument(
        "--version",
        default="1.0.0",
        help="Version number for the installer"
    )
    windows_parser.add_argument(
        "--output-dir",
        help="Output directory for the installer"
    )
    
    # Docker installer
    docker_parser = subparsers.add_parser("docker", help="Build Docker image")
    docker_parser.add_argument(
        "--tag",
        default="latest",
        help="Tag for the Docker image"
    )
    
    # Source installer
    source_parser = subparsers.add_parser("source", help="Install from source")
    source_parser.add_argument(
        "--venv",
        help="Path to virtual environment"
    )
    
    # Setup wizard
    wizard_parser = subparsers.add_parser("wizard", help="Launch setup wizard")
    wizard_parser.add_argument(
        "--platform",
        choices=["windows", "linux", "macos"],
        default="windows",
        help="Platform to use for the wizard"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the installer."""
    args = parse_args()
    
    # Create configuration
    config = InstallerConfig(args.config) if args.config else InstallerConfig()
    
    # Execute command
    if args.command == "windows":
        from .build.windows import WindowsBuilder
        
        builder = WindowsBuilder(
            repo_url="https://github.com/skunkbandit/handyman-kpi-system",
            version=args.version,
            output_dir=args.output_dir
        )
        
        try:
            installer_path = builder.build()
            print(f"Windows installer created: {installer_path}")
            return 0
        except Exception as e:
            print(f"Error building Windows installer: {e}", file=sys.stderr)
            return 1
    
    elif args.command == "docker":
        # Docker builder placeholder
        print("Docker builder not implemented yet")
        return 1
    
    elif args.command == "source":
        # Source installer placeholder
        print("Source installer not implemented yet")
        return 1
    
    elif args.command == "wizard":
        if args.platform == "windows":
            from .platforms.windows.gui.setup_wizard import SetupWizard
            
            wizard = SetupWizard(config)
            wizard.run()
            return 0
        else:
            print(f"Wizard for {args.platform} not implemented yet")
            return 1
    
    else:
        print("No command specified. Use --help for usage information.")
        return 1

if __name__ == "__main__":
    sys.exit(main())