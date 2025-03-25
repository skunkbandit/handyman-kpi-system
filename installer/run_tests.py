"""Test runner for the KPI System Installer.

This script discovers and runs all tests for the installer components.
"""

import os
import sys
import unittest
import argparse
from pathlib import Path

# Add the installer directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import shared utilities
from installer.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def discover_and_run_tests(test_pattern="test_*.py", start_dir=None, verbosity=2):
    """
    Discover and run all tests matching the pattern.
    
    Args:
        test_pattern (str): Pattern to match test files
        start_dir (str, optional): Directory to start discovery
        verbosity (int): Verbosity level for test output
        
    Returns:
        unittest.TestResult: Result of the test run
    """
    # Determine the start directory
    if start_dir is None:
        start_dir = os.path.dirname(os.path.abspath(__file__))
        
    # Discover tests
    loader = unittest.TestLoader()
    test_suite = loader.discover(start_dir, pattern=test_pattern)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(test_suite)


def run_specific_tests(test_names, verbosity=2):
    """
    Run specific test modules, classes or methods.
    
    Args:
        test_names (list): List of test names to run
        verbosity (int): Verbosity level for test output
        
    Returns:
        unittest.TestResult: Result of the test run
    """
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    for test_name in test_names:
        try:
            # Try to load the test by name
            tests = loader.loadTestsFromName(test_name)
            test_suite.addTest(tests)
        except (ImportError, AttributeError) as e:
            logger.error(f"Could not load test {test_name}: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(test_suite)


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for the KPI System Installer")
    parser.add_argument("--pattern", "-p", default="test_*.py", 
                        help="Pattern to match test files (default: test_*.py)")
    parser.add_argument("--directory", "-d", default=None,
                        help="Directory to start test discovery (default: script directory)")
    parser.add_argument("--verbosity", "-v", type=int, default=2,
                        help="Verbosity level (default: 2)")
    parser.add_argument("--specific", "-s", nargs="+", default=[],
                        help="Run specific test modules, classes or methods")
    parser.add_argument("--gui", "-g", action="store_true",
                        help="Run only GUI-related tests")
    parser.add_argument("--inno", "-i", action="store_true",
                        help="Run only Inno Setup integration tests")
    parser.add_argument("--core", "-c", action="store_true",
                        help="Run only core functionality tests")
    
    args = parser.parse_args()
    
    # Set up specific test patterns based on arguments
    if args.gui:
        args.pattern = "test_*gui*.py"
    elif args.inno:
        args.pattern = "test_*inno*.py"
    elif args.core:
        args.pattern = "test_*(?!gui|inno)*.py"
    
    # Run tests
    if args.specific:
        result = run_specific_tests(args.specific, args.verbosity)
    else:
        result = discover_and_run_tests(args.pattern, args.directory, args.verbosity)
    
    # Print summary and exit with appropriate status code
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        print("\nTest run failed. See above for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()