"""
Tool Inventory Report implementation.
"""
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.employee import Employee
from app.models.evaluation import Evaluation, ToolEvaluation
from app.models.tool import Tool, ToolCategory
from app import db
from .base import ReportGenerator


class ToolInventoryReport(ReportGenerator):
    """Tool Inventory Report Generator.
    
    Generates reports on tool proficiency and ownership across the organization.
    """
    
    def __init__(self):
        """Initialize the Tool Inventory Report generator."""
        super().__init__(
            title="Tool Inventory Report",
            description="Analysis of tool proficiency and ownership across the organization",
            report_type="tools"
        )
    
    def collect_data(self, category_id=None, tier=None, start_date=None, end_date=None, **kwargs):
        """Collect all data needed for the tool inventory report.
        
        Args:
            category_id (int, optional): Filter by tool category ID
            tier (str, optional): Filter by employee tier
            start_date (str, optional): Start date for filtering evaluations (YYYY-MM-DD)
            end_date (str, optional): End date for filtering evaluations (YYYY-MM-DD)
            **kwargs: Additional filters
            
        Returns:
            dict: Dictionary containing the collected data
        """
        # Parse dates or use defaults (last 12 months)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = datetime.now()
            
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = end_date - timedelta(days=365)  # Last 12 months
        
        # Get tool categories
        if category_id:
            categories = [ToolCategory.query.get(category_id)]
            if not categories[0]:
                raise ValueError(f"Tool category with ID {category_id} not found")
        else:
            categories = ToolCategory.query.all()
            
        # Get tools within selected categories
        category_ids = [category.id for category in categories]
        tools = Tool.query.filter(Tool.category_id.in_(category_ids)).all()
        
        # Get employees based on filters
        employee_query = Employee.query
        if tier:
            employee_query = employee_query.filter(Employee.tier == tier)
        employees = employee_query.all()
        
        # Get evaluations for filtered employees
        evaluation_query = Evaluation.query.filter(
            Evaluation.date >= start_date,
            Evaluation.date <= end_date
        )
        
        if tier:
            employee_ids = [e.id for e in employees]
            evaluation_query = evaluation_query.filter(Evaluation.employee_id.in_(employee_ids))
            
        evaluations = evaluation_query.all()
        
        # Collect tool data across all evaluations
        tool_data = defaultdict(list)
        employee_tool_data = defaultdict(lambda: defaultdict(dict))
        
        for evaluation in evaluations:
            for tool_eval in evaluation.tool_evaluations:
                tool = tool_eval.tool
                
                # Skip if not in our target categories
                if tool.category_id not in category_ids:
                    continue
                    
                # Add to overall tool data
                tool_data[tool.id].append({
                    'tool_name': tool.name,
                    'category_name': tool.category.name,
                    'can_operate': tool_eval.can_operate,
                    'owned': tool_eval.owned,
                    'truck_stock': tool_eval.truck_stock,
                    'employee_id': evaluation.employee_id,
                    'date': evaluation.date
                })
                
                # Add to employee-specific data (most recent evaluation)
                employee_id = evaluation.employee_id
                if tool.id not in employee_tool_data[employee_id] or evaluation.date > employee_tool_data[employee_id][tool.id].get('date', datetime.min):
                    employee_tool_data[employee_id][tool.id] = {
                        'tool_name': tool.name,
                        'category_name': tool.category.name,
                        'can_operate': tool_eval.can_operate,
                        'owned': tool_eval.owned,
                        'truck_stock': tool_eval.truck_stock,
                        'date': evaluation.date
                    }
        
        # Calculate tool statistics
        tool_stats = {}
        for tool_id, entries in tool_data.items():
            # Get the total number of unique employees evaluated with this tool
            unique_employees = set(entry['employee_id'] for entry in entries)
            employee_count = len(unique_employees)
            
            if employee_count > 0:
                # Count employees who can operate this tool
                can_operate_entries = [e for e in entries if e['can_operate']]
                can_operate_employees = set(e['employee_id'] for e in can_operate_entries)
                can_operate_count = len(can_operate_employees)
                
                # Count employees who own this tool
                owned_entries = [e for e in entries if e['owned']]
                owned_employees = set(e['employee_id'] for e in owned_entries)
                owned_count = len(owned_employees)
                
                # Count employees who have this tool as truck stock
                truck_stock_entries = [e for e in entries if e['truck_stock']]
                truck_stock_employees = set(e['employee_id'] for e in truck_stock_entries)
                truck_stock_count = len(truck_stock_employees)
                
                tool_stats[tool_id] = {
                    'tool_name': entries[0]['tool_name'],
                    'category_name': entries[0]['category_name'],
                    'can_operate_count': can_operate_count,
                    'owned_count': owned_count,
                    'truck_stock_count': truck_stock_count,
                    'can_operate_percent': (can_operate_count / employee_count) * 100,
                    'owned_percent': (owned_count / employee_count) * 100,
                    'truck_stock_percent': (truck_stock_count / employee_count) * 100,
                    'employee_count': employee_count
                }
        
        # Calculate category statistics
        category_stats = defaultdict(lambda: {
            'tool_count': 0,
            'can_operate_count': 0,
            'owned_count': 0,
            'truck_stock_count': 0,
            'total_evaluations': 0
        })
        
        for tool_id, stats in tool_stats.items():
            category_name = stats['category_name']
            category_stats[category_name]['tool_count'] += 1
            category_stats[category_name]['can_operate_count'] += stats['can_operate_count']
            category_stats[category_name]['owned_count'] += stats['owned_count']
            category_stats[category_name]['truck_stock_count'] += stats['truck_stock_count']
            category_stats[category_name]['total_evaluations'] += stats['employee_count']
        
        # Calculate averages for each category
        for category_name, stats in category_stats.items():
            if stats['total_evaluations'] > 0:
                stats['can_operate_avg'] = (stats['can_operate_count'] / stats['total_evaluations']) * 100
                stats['owned_avg'] = (stats['owned_count'] / stats['total_evaluations']) * 100
                stats['truck_stock_avg'] = (stats['truck_stock_count'] / stats['total_evaluations']) * 100
            else:
                stats['can_operate_avg'] = 0
                stats['owned_avg'] = 0
                stats['truck_stock_avg'] = 0
        
        # Identify missing tools (tools with low ownership rates)
        missing_tools = []
        for tool_id, stats in tool_stats.items():
            # Consider a tool "missing" if less than 50% of employees own it
            # but more than 50% can operate it (suggests it's useful but underowned)
            if stats['owned_percent'] < 50 and stats['can_operate_percent'] > 50:
                missing_tools.append({
                    'tool_id': tool_id,
                    'tool_name': stats['tool_name'],
                    'category_name': stats['category_name'],
                    'owned_percent': stats['owned_percent'],
                    'can_operate_percent': stats['can_operate_percent'],
                    'gap': stats['can_operate_percent'] - stats['owned_percent']
                })
        
        # Sort missing tools by the gap between operation ability and ownership (descending)
        missing_tools.sort(key=lambda x: x['gap'], reverse=True)
        
        # Calculate tool training needs
        training_needs = []
        for tool_id, stats in tool_stats.items():
            # Consider a tool a "training need" if less than 50% of employees can operate it
            if stats['can_operate_percent'] < 50:
                training_needs.append({
                    'tool_id': tool_id,
                    'tool_name': stats['tool_name'],
                    'category_name': stats['category_name'],
                    'can_operate_percent': stats['can_operate_percent'],
                    'gap': 100 - stats['can_operate_percent']  # Gap to 100% proficiency
                })
        
        # Sort training needs by the proficiency gap (descending)
        training_needs.sort(key=lambda x: x['gap'], reverse=True)
        
        # Store all collected data
        self.data = {
            'categories': categories,
            'tools': tools,
            'employees': employees,
            'tool_data': tool_data,
            'employee_tool_data': employee_tool_data,
            'tool_stats': tool_stats,
            'category_stats': category_stats,
            'missing_tools': missing_tools,
            'training_needs': training_needs,
            'report_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'report_filters': {
                'category_id': category_id,
                'tier': tier
            }
        }
        
        return self.data
    
    def prepare_template_data(self):
        """Prepare data for the report template.
        
        Returns:
            dict: Dictionary containing template variables
        """
        # Prepare category data for charts
        categories = self.data['categories']
        category_stats = self.data['category_stats']
        
        # Format category data for chart
        category_chart_data = {
            'labels': [cat.name for cat in categories],
            'can_operate_values': [category_stats.get(cat.name, {}).get('can_operate_avg', 0) for cat in categories],
            'owned_values': [category_stats.get(cat.name, {}).get('owned_avg', 0) for cat in categories],
            'truck_stock_values': [category_stats.get(cat.name, {}).get('truck_stock_avg', 0) for cat in categories]
        }
        
        # Prepare missing tools data
        missing_tools = self.data['missing_tools'][:10]  # Top 10 missing tools
        
        missing_tools_chart_data = {
            'labels': [tool['tool_name'] for tool in missing_tools],
            'owned_values': [tool['owned_percent'] for tool in missing_tools],
            'can_operate_values': [tool['can_operate_percent'] for tool in missing_tools]
        }
        
        # Prepare training needs data
        training_needs = self.data['training_needs'][:10]  # Top 10 training needs
        
        training_needs_chart_data = {
            'labels': [tool['tool_name'] for tool in training_needs],
            'can_operate_values': [tool['can_operate_percent'] for tool in training_needs],
            'gap_values': [tool['gap'] for tool in training_needs]
        }
        
        # Create template data dictionary
        template_data = {
            'categories': categories,
            'category_stats': category_stats,
            'category_chart_data': category_chart_data,
            'tool_stats': self.data['tool_stats'],
            'missing_tools': missing_tools,
            'missing_tools_chart_data': missing_tools_chart_data,
            'training_needs': training_needs,
            'training_needs_chart_data': training_needs_chart_data,
            'report_period': self.data['report_period'],
            'report_filters': self.data['report_filters']
        }
        
        return template_data
    
    def prepare_excel_data(self):
        """Prepare data for the Excel report.
        
        Returns:
            dict: Dictionary containing dataframes for each sheet
        """
        # Summary sheet
        summary_data = {
            'Category': [],
            'Tool Count': [],
            'Can Operate %': [],
            'Owned %': [],
            'Truck Stock %': []
        }
        
        for category in self.data['categories']:
            stats = self.data['category_stats'].get(category.name, {})
            
            summary_data['Category'].append(category.name)
            summary_data['Tool Count'].append(stats.get('tool_count', 0))
            summary_data['Can Operate %'].append(f"{round(stats.get('can_operate_avg', 0), 2)}%")
            summary_data['Owned %'].append(f"{round(stats.get('owned_avg', 0), 2)}%")
            summary_data['Truck Stock %'].append(f"{round(stats.get('truck_stock_avg', 0), 2)}%")
            
        summary_df = pd.DataFrame(summary_data)
        
        # Tool details sheet
        tools_data = {
            'Tool ID': [],
            'Tool Name': [],
            'Category': [],
            'Can Operate Count': [],
            'Can Operate %': [],
            'Owned Count': [],
            'Owned %': [],
            'Truck Stock Count': [],
            'Truck Stock %': [],
            'Employee Count': []
        }
        
        for tool_id, stats in self.data['tool_stats'].items():
            tools_data['Tool ID'].append(tool_id)
            tools_data['Tool Name'].append(stats['tool_name'])
            tools_data['Category'].append(stats['category_name'])
            tools_data['Can Operate Count'].append(stats['can_operate_count'])
            tools_data['Can Operate %'].append(f"{round(stats['can_operate_percent'], 2)}%")
            tools_data['Owned Count'].append(stats['owned_count'])
            tools_data['Owned %'].append(f"{round(stats['owned_percent'], 2)}%")
            tools_data['Truck Stock Count'].append(stats['truck_stock_count'])
            tools_data['Truck Stock %'].append(f"{round(stats['truck_stock_percent'], 2)}%")
            tools_data['Employee Count'].append(stats['employee_count'])
            
        tools_df = pd.DataFrame(tools_data)
        
        # Sort by can operate percentage (descending)
        tools_df = tools_df.sort_values('Can Operate Count', ascending=False)
        
        # Missing tools sheet
        missing_data = {
            'Tool ID': [],
            'Tool Name': [],
            'Category': [],
            'Owned %': [],
            'Can Operate %': [],
            'Gap': []
        }
        
        for tool in self.data['missing_tools']:
            missing_data['Tool ID'].append(tool['tool_id'])
            missing_data['Tool Name'].append(tool['tool_name'])
            missing_data['Category'].append(tool['category_name'])
            missing_data['Owned %'].append(f"{round(tool['owned_percent'], 2)}%")
            missing_data['Can Operate %'].append(f"{round(tool['can_operate_percent'], 2)}%")
            missing_data['Gap'].append(f"{round(tool['gap'], 2)}%")
            
        missing_df = pd.DataFrame(missing_data)
        
        # Training needs sheet
        training_data = {
            'Tool ID': [],
            'Tool Name': [],
            'Category': [],
            'Can Operate %': [],
            'Gap to 100%': []
        }
        
        for tool in self.data['training_needs']:
            training_data['Tool ID'].append(tool['tool_id'])
            training_data['Tool Name'].append(tool['tool_name'])
            training_data['Category'].append(tool['category_name'])
            training_data['Can Operate %'].append(f"{round(tool['can_operate_percent'], 2)}%")
            training_data['Gap to 100%'].append(f"{round(tool['gap'], 2)}%")
            
        training_df = pd.DataFrame(training_data)
        
        # Employee tool inventory sheet
        inventory_data = []
        
        for employee_id, tools in self.data['employee_tool_data'].items():
            employee = next((e for e in self.data['employees'] if e.id == employee_id), None)
            if employee:
                for tool_id, tool_info in tools.items():
                    inventory_data.append({
                        'Employee ID': employee_id,
                        'Employee Name': f"{employee.first_name} {employee.last_name}",
                        'Tier': employee.tier,
                        'Tool Name': tool_info['tool_name'],
                        'Category': tool_info['category_name'],
                        'Can Operate': 'Yes' if tool_info['can_operate'] else 'No',
                        'Owned': 'Yes' if tool_info['owned'] else 'No',
                        'Truck Stock': 'Yes' if tool_info['truck_stock'] else 'No',
                        'Last Evaluated': tool_info['date'].strftime('%Y-%m-%d')
                    })
        
        inventory_df = pd.DataFrame(inventory_data)
        
        # Return dictionary of dataframes
        return {
            'Category Summary': summary_df,
            'Tool Details': tools_df,
            'Missing Tools': missing_df,
            'Training Needs': training_df,
            'Employee Inventory': inventory_df
        }
