#!/usr/bin/env python
"""
Test runner script for the KPI system.
This script runs all tests or specific test categories with coverage reporting.
"""
import os
import sys
import argparse
import subprocess
import coverage
import time

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run KPI System tests with coverage')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--ui', action='store_true', help='Run UI tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--xml', action='store_true', help='Generate XML coverage report for CI')
    parser.add_argument('--skip-coverage', action='store_true', help='Skip coverage analysis')
    parser.add_argument('files', nargs='*', help='Specific test files to run')
    
    args = parser.parse_args()
    
    # If no specific test type is selected, run all tests
    if not (args.unit or args.integration or args.ui or args.files):
        args.all = True
        
    return args

def run_tests(args):
    """Run tests according to specified arguments."""
    print("=" * 80)
    print(f"KPI System Test Runner - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Determine which tests to run
    test_paths = []
    
    if args.files:
        # Run specific test files
        test_paths.extend(args.files)
    else:
        if args.all or args.unit:
            test_paths.append('tests/unit/')
        
        if args.all or args.integration:
            test_paths.append('tests/integration/')
        
        if args.all or args.ui:
            test_paths.append('tests/ui/')
    
    # Skip coverage for UI tests (Selenium doesn't work well with coverage)
    skip_coverage = args.skip_coverage or (args.ui and not (args.unit or args.integration))
    
    # Basic pytest arguments
    pytest_args = [
        '-v',  # Verbose
        '--color=yes',  # Colored output
    ]
    
    # Skip UI tests if running with coverage
    if not args.ui and not args.all:
        pytest_args.append('--ignore=tests/ui/')
    
    # Add test paths
    pytest_args.extend(test_paths)
    
    if skip_coverage:
        print("Running tests without coverage...")
        cmd = [sys.executable, '-m', 'pytest'] + pytest_args
        result = subprocess.run(cmd)
        return result.returncode
    else:
        print("Running tests with coverage...")
        
        # Initialize coverage
        cov = coverage.Coverage(
            source=['kpi_system'],
            omit=[
                '*/tests/*',
                '*/migrations/*',
                '*/venv/*',
                '*/__pycache__/*',
                '*/site-packages/*'
            ]
        )
        
        # Start coverage
        cov.start()
        
        # Run pytest
        cmd = [sys.executable, '-m', 'pytest'] + pytest_args
        result = subprocess.run(cmd)
        
        # Stop coverage
        cov.stop()
        cov.save()
        
        print("\nCoverage Summary:")
        cov.report()
        
        # Generate HTML report if requested
        if args.html:
            html_dir = os.path.join('tests', 'coverage_html')
            print(f"\nGenerating HTML coverage report in {html_dir}...")
            cov.html_report(directory=html_dir)
        
        # Generate XML report if requested
        if args.xml:
            xml_file = os.path.join('tests', 'coverage.xml')
            print(f"\nGenerating XML coverage report at {xml_file}...")
            cov.xml_report(outfile=xml_file)
        
        return result.returncode

if __name__ == '__main__':
    args = parse_args()
    sys.exit(run_tests(args))
