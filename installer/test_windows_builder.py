"""
Test script for the Windows builder.

This script tests the WindowsBuilder class to ensure it works correctly.
"""
import os
import sys
from build.windows import WindowsBuilder

def test_windows_builder():
    """Test the WindowsBuilder class."""
    # Initialize builder with test parameters
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
    builder = WindowsBuilder(
        repo_url="https://github.com/skunkbandit/handyman-kpi-system",
        version="1.0.0-test",
        output_dir=output_dir
    )
    
    # Test directory creation
    builder.create_directories()
    assert os.path.exists(builder.python_dir)
    assert os.path.exists(builder.app_dir)
    assert os.path.exists(builder.installer_dir)
    assert os.path.exists(builder.output_dir)
    
    # Test finding Inno Setup
    inno_path = builder._find_inno_setup()
    if inno_path:
        print(f"Inno Setup found at: {inno_path}")
    else:
        print("Inno Setup not found")
    
    print("Basic tests passed!")
    
    # Uncomment to test the full build process (takes time)
    # try:
    #     installer_path = builder.build()
    #     print(f"Installer created at: {installer_path}")
    # except Exception as e:
    #     print(f"Error: {e}")
    #     sys.exit(1)

if __name__ == "__main__":
    test_windows_builder()
