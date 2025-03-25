#!/usr/bin/env python3
"""
Test runner for the Handyman KPI System Installer unit tests.

This script discovers and runs all unit tests for the installer components.
"""

import os
import sys
import unittest
import coverage

# Add the main project directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))


def run_tests(with_coverage=False):
    """
    Run all unit tests for the installer components.
    
    Args:
        with_coverage (bool): Whether to measure code coverage
    
    Returns:
        int: Number of test failures
    """
    # Get the directory containing the test modules
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    if with_coverage:
        # Start coverage measurement
        cov = coverage.Coverage(
            source=['installer.shared.database'],
            omit=['*/__pycache__/*', '*/tests/*']
        )
        cov.start()
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if with_coverage:
        # Stop coverage measurement and report
        cov.stop()
        print("\nCoverage report:")
        cov.report()
        
        # Generate HTML report
        html_dir = os.path.join(test_dir, 'coverage_html')
        os.makedirs(html_dir, exist_ok=True)
        cov.html_report(directory=html_dir)
        print(f"HTML coverage report generated in: {html_dir}")
    
    # Return the number of failures
    return len(result.failures) + len(result.errors)


if __name__ == '__main__':
    # Parse command-line arguments
    measure_coverage = '--cov' in sys.argv
    
    # Run the tests
    print("Running installer unit tests...")
    failures = run_tests(with_coverage=measure_coverage)
    
    # Exit with appropriate code
    sys.exit(failures)
