"""
Employee Performance Report implementation.
"""
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.employee import Employee
from app.models.evaluation import Evaluation, SkillEvaluation, ToolEvaluation
from app.models.skill import Skill, SkillCategory
from app.models.tool import Tool, ToolCategory
from app import db
from .base import ReportGenerator


class EmployeePerformanceReport(ReportGenerator):
    """Employee Performance Report Generator.
    
    Generates comprehensive performance reports for individual employees.
    """
    
    def __init__(self):
        """Initialize the Employee Performance Report generator."""
        super().__init__(
            title="Employee Performance Report",
            description="Comprehensive evaluation of employee performance metrics",
            report_type="employee"
        )
    
    def collect_data(self, employee_id, start_date=None, end_date=None, **kwargs):
        """Collect all data needed for the employee performance report.
        
        Args:
            employee_id (int): ID of the employee
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
        
        # Get employee details
        employee = Employee.query.get(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        # Get evaluations for this employee
        evaluations = Evaluation.query.filter(
            Evaluation.employee_id == employee_id,
            Evaluation.date >= start_date,
            Evaluation.date <= end_date
        ).order_by(Evaluation.date.desc()).all()
        
        # Get all skill categories
        skill_categories = SkillCategory.query.all()
        
        # Get all tool categories
        tool_categories = ToolCategory.query.all()
        
        # Prepare skill data from evaluations
        skill_data = defaultdict(list)
        for evaluation in evaluations:
            for skill_eval in evaluation.skill_evaluations:
                skill = skill_eval.skill
                category = skill.category.name
                skill_data[category].append({
                    'skill_name': skill.name,
                    'rating': skill_eval.rating,
                    'date': evaluation.date
                })
        
        # Calculate average skill ratings by category
        skill_averages = {}
        for category, skills in skill_data.items():
            ratings = [s['rating'] for s in skills]
            if ratings:
                skill_averages[category] = sum(ratings) / len(ratings)
            else:
                skill_averages[category] = 0
        
        # Prepare tool data from evaluations
        tool_data = defaultdict(list)
        for evaluation in evaluations:
            for tool_eval in evaluation.tool_evaluations:
                tool = tool_eval.tool
                category = tool.category.name
                tool_data[category].append({
                    'tool_name': tool.name,
                    'can_operate': tool_eval.can_operate,
                    'owned': tool_eval.owned,
                    'date': evaluation.date
                })
        
        # Count tools that can be operated and owned by category
        tool_stats = {}
        for category, tools in tool_data.items():
            can_operate_count = sum(1 for t in tools if t['can_operate'])
            owned_count = sum(1 for t in tools if t['owned'])
            total_tools = len(set(t['tool_name'] for t in tools))
            if total_tools > 0:
                tool_stats[category] = {
                    'can_operate_percent': (can_operate_count / total_tools) * 100,
                    'owned_percent': (owned_count / total_tools) * 100,
                    'total_tools': total_tools
                }
            else:
                tool_stats[category] = {
                    'can_operate_percent': 0,
                    'owned_percent': 0,
                    'total_tools': 0
                }
        
        # Get historical data for trend analysis
        historical_data = []
        
        # Group evaluations by month
        eval_by_month = defaultdict(list)
        for evaluation in evaluations:
            month_key = evaluation.date.strftime('%Y-%m')
            eval_by_month[month_key].append(evaluation)
        
        # Calculate average skill rating for each month
        for month_key, month_evals in sorted(eval_by_month.items()):
            month_skills = []
            for eval in month_evals:
                month_skills.extend([se.rating for se in eval.skill_evaluations])
            
            if month_skills:
                avg_rating = sum(month_skills) / len(month_skills)
                historical_data.append({
                    'date': month_key,
                    'average_rating': avg_rating
                })
        
        # Identify improvement areas (lowest rated skills)
        improvement_areas = []
        all_skill_ratings = []
        
        for eval in evaluations:
            for skill_eval in eval.skill_evaluations:
                all_skill_ratings.append({
                    'skill_name': skill_eval.skill.name,
                    'category': skill_eval.skill.category.name,
                    'rating': skill_eval.rating
                })
        
        # Group by skill name and calculate averages
        skill_ratings_grouped = defaultdict(list)
        for sr in all_skill_ratings:
            skill_ratings_grouped[(sr['skill_name'], sr['category'])].append(sr['rating'])
        
        avg_skill_ratings = []
        for (skill_name, category), ratings in skill_ratings_grouped.items():
            avg_rating = sum(ratings) / len(ratings)
            avg_skill_ratings.append({
                'skill_name': skill_name,
                'category': category,
                'average_rating': avg_rating
            })
        
        # Sort by rating (ascending) and get the 5 lowest
        avg_skill_ratings.sort(key=lambda x: x['average_rating'])
        improvement_areas = avg_skill_ratings[:5]
        
        # Store all collected data
        self.data = {
            'employee': employee,
            'evaluations': evaluations,
            'skill_categories': skill_categories,
            'tool_categories': tool_categories,
            'skill_data': skill_data,
            'skill_averages': skill_averages,
            'tool_data': tool_data,
            'tool_stats': tool_stats,
            'historical_data': historical_data,
            'improvement_areas': improvement_areas,
            'report_period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return self.data
    
    def prepare_template_data(self):
        """Prepare data for the report template.
        
        Returns:
            dict: Dictionary containing template variables
        """
        # Convert data to template-friendly format
        employee = self.data['employee']
        skill_averages = self.data['skill_averages']
        skill_categories = self.data['skill_categories']
        tool_stats = self.data['tool_stats']
        improvement_areas = self.data['improvement_areas']
        historical_data = self.data['historical_data']
        
        # Format skill data for radar chart
        radar_data = {
            'labels': list(skill_averages.keys()),
            'values': [skill_averages.get(cat.name, 0) for cat in skill_categories]
        }
        
        # Format historical data for line chart
        line_data = {
            'labels': [hd['date'] for hd in historical_data],
            'values': [hd['average_rating'] for hd in historical_data]
        }
        
        # Create template data dictionary
        template_data = {
            'employee': employee,
            'skill_averages': skill_averages,
            'tool_stats': tool_stats,
            'improvement_areas': improvement_areas,
            'radar_data': radar_data,
            'line_data': line_data,
            'recent_evaluations': self.data['evaluations'][:5],
            'report_period': self.data['report_period']
        }
        
        return template_data
    
    def prepare_excel_data(self):
        """Prepare data for the Excel report.
        
        Returns:
            dict: Dictionary containing dataframes for each sheet
        """
        # Employee information sheet
        employee = self.data['employee']
        evaluations = self.data['evaluations']
        
        # Create employee info dataframe
        employee_info = {
            'Employee ID': [employee.id],
            'Name': [f"{employee.first_name} {employee.last_name}"],
            'Current Tier': [employee.tier],
            'Hire Date': [employee.hire_date],
            'Phone Number': [employee.phone],
            'Email': [employee.email],
            'Total Evaluations': [len(evaluations)],
            'Last Evaluation Date': [evaluations[0].date if evaluations else 'N/A']
        }
        employee_df = pd.DataFrame(employee_info)
        
        # Create skills dataframe
        skills_data = []
        for category, skills in self.data['skill_data'].items():
            for skill in skills:
                skills_data.append({
                    'Category': category,
                    'Skill': skill['skill_name'],
                    'Rating': skill['rating'],
                    'Evaluation Date': skill['date']
                })
        skills_df = pd.DataFrame(skills_data)
        
        # Create tools dataframe
        tools_data = []
        for category, tools in self.data['tool_data'].items():
            for tool in tools:
                tools_data.append({
                    'Category': category,
                    'Tool': tool['tool_name'],
                    'Can Operate': 'Yes' if tool['can_operate'] else 'No',
                    'Owned': 'Yes' if tool['owned'] else 'No',
                    'Evaluation Date': tool['date']
                })
        tools_df = pd.DataFrame(tools_data)
        
        # Create summary dataframe
        skill_averages = [(k, v) for k, v in self.data['skill_averages'].items()]
        summary_data = []
        for category, avg in skill_averages:
            summary_data.append({
                'Category': category,
                'Average Rating': round(avg, 2),
                'Max Possible': 5,
                'Percentage': f"{round((avg / 5) * 100, 2)}%"
            })
        summary_df = pd.DataFrame(summary_data)
        
        # Create improvement areas dataframe
        improvement_df = pd.DataFrame(self.data['improvement_areas'])
        
        # Return dictionary of dataframes
        return {
            'Employee Info': employee_df,
            'Skills Summary': summary_df,
            'Detailed Skills': skills_df,
            'Tools': tools_df,
            'Improvement Areas': improvement_df
        }
