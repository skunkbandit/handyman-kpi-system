#!/usr/bin/env python
"""
Test runner for installer integration tests.

This script runs the integration tests for the installer components.
"""

import os
import sys
import pytest

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


def run_database_integration_tests():
    """Run database integration tests."""
    print("Running database integration tests...")
    result = pytest.main([
        os.path.join(os.path.dirname(__file__), 'test_database_integration.py'),
        os.path.join(os.path.dirname(__file__), 'test_database_integration_part2.py'),
        '-v'
    ])
    return result == 0


def run_setup_wizard_tests():
    """Run setup wizard integration tests."""
    print("Running setup wizard integration tests...")
    result = pytest.main([
        os.path.join(os.path.dirname(__file__), 'test_setup_wizard.py'),
        '-v'
    ])
    return result == 0


def run_end_to_end_tests():
    """Run end-to-end installation tests."""
    print("Running end-to-end installation tests...")
    result = pytest.main([
        os.path.join(os.path.dirname(__file__), 'test_end_to_end.py'),
        os.path.join(os.path.dirname(__file__), 'test_end_to_end_part2.py'),
        '-v'
    ])
    return result == 0


def run_all_tests():
    """Run all installer integration tests."""
    print("Running all installer integration tests...")
    result = pytest.main([
        os.path.join(os.path.dirname(__file__)),
        '-v'
    ])
    return result == 0


if __name__ == '__main__':
    # Parse command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == 'database':
            success = run_database_integration_tests()
        elif test_type == 'wizard':
            success = run_setup_wizard_tests()
        elif test_type == 'end-to-end':
            success = run_end_to_end_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available test types: database, wizard, end-to-end")
            success = False
    else:
        # Run all tests by default
        success = run_all_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)