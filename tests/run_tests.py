#!/usr/bin/env python
"""
Test runner script for the KPI system.
This script runs all tests and generates coverage reports.
"""
import os
import sys
import pytest
import coverage

def run_tests():
    """Run all tests with coverage reporting."""
    print("Starting test run with coverage...")
    
    # Start coverage measurement
    cov = coverage.Coverage(
        source=['kpi_system'],
        omit=[
            '*/tests/*',
            '*/migrations/*',
            '*/venv/*',
            '*/__pycache__/*'
        ]
    )
    cov.start()
    
    # Run tests with pytest
    test_args = [
        '--verbose',
        '--color=yes',
        '-xvs'
    ]
    
    # Add specific test modules if provided as arguments
    if len(sys.argv) > 1:
        test_args.extend(sys.argv[1:])
    else:
        # Run all tests by default
        test_args.append('tests/')
        
    result = pytest.main(test_args)
    
    # Stop coverage and generate report
    cov.stop()
    cov.save()
    
    print("\nGenerating coverage reports...")
    cov.report()
    
    # Generate HTML report
    html_dir = os.path.join('tests', 'coverage_html')
    cov.html_report(directory=html_dir)
    print(f"HTML coverage report generated in {html_dir}")
    
    # Generate XML report for CI integration
    xml_file = os.path.join('tests', 'coverage.xml')
    cov.xml_report(outfile=xml_file)
    print(f"XML coverage report generated at {xml_file}")
    
    return result

if __name__ == '__main__':
    sys.exit(run_tests())