"""
Module that exposes all report generators.
"""
from .employee_performance import EmployeePerformanceReport
from .team_performance import TeamPerformanceReport
from .skills_analysis import SkillsAnalysisReport
from .tool_inventory import ToolInventoryReport

# A dictionary mapping report types to their generator classes
REPORT_GENERATORS = {
    'employee': EmployeePerformanceReport,
    'team': TeamPerformanceReport,
    'skills': SkillsAnalysisReport,
    'tools': ToolInventoryReport
}

def get_report_generator(report_type):
    """Get a report generator instance by type.
    
    Args:
        report_type (str): Type of report to generate
        
    Returns:
        ReportGenerator: Instance of the requested report generator
    
    Raises:
        ValueError: If the report type is not supported
    """
    generator_class = REPORT_GENERATORS.get(report_type)
    if not generator_class:
        raise ValueError(f"Unsupported report type: {report_type}")
    
    return generator_class()

def get_available_report_types():
    """Get a list of all available report types.
    
    Returns:
        list: List of report type dictionaries with 'id' and 'name' keys
    """
    return [
        {
            'id': 'employee',
            'name': 'Employee Performance Report',
            'description': 'Comprehensive evaluation of an individual employee\'s performance'
        },
        {
            'id': 'team',
            'name': 'Team Performance Report',
            'description': 'Comparative analysis of performance across multiple employees'
        },
        {
            'id': 'skills',
            'name': 'Skills Analysis Report',
            'description': 'Deep dive into skill distribution across the organization'
        },
        {
            'id': 'tools',
            'name': 'Tool Inventory Report',
            'description': 'Track tool proficiency and ownership across employees'
        }
    ]
