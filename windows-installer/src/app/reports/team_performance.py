"""
Team Performance Report implementation.
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


class TeamPerformanceReport(ReportGenerator):
    """Team Performance Report Generator.
    
    Generates comparative performance reports across multiple employees.
    """
    
    def __init__(self):
        """Initialize the Team Performance Report generator."""
        super().__init__(
            title="Team Performance Report",
            description="Comparative analysis of employee performance metrics",
            report_type="team"
        )
    
    def collect_data(self, tier=None, start_date=None, end_date=None, employee_ids=None, **kwargs):
        """Collect all data needed for the team performance report.
        
        Args:
            tier (str, optional): Filter by employee tier
            start_date (str, optional): Start date for filtering evaluations (YYYY-MM-DD)
            end_date (str, optional): End date for filtering evaluations (YYYY-MM-DD)
            employee_ids (list, optional): List of employee IDs to include
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
        
        # Get employees based on filters
        employee_query = Employee.query
        
        if tier:
            employee_query = employee_query.filter(Employee.tier == tier)
            
        if employee_ids:
            employee_query = employee_query.filter(Employee.id.in_(employee_ids))
            
        employees = employee_query.all()
        
        if not employees:
            raise ValueError("No employees found matching the criteria")
        
        # Get evaluations for these employees
        evaluation_query = Evaluation.query.filter(
            Evaluation.date >= start_date,
            Evaluation.date <= end_date
        )
        
        if employee_ids:
            evaluation_query = evaluation_query.filter(Evaluation.employee_id.in_(employee_ids))
        elif tier:
            employee_ids = [e.id for e in employees]
            evaluation_query = evaluation_query.filter(Evaluation.employee_id.in_(employee_ids))
            
        evaluations = evaluation_query.order_by(Evaluation.date.desc()).all()
        
        # Get all skill categories
        skill_categories = SkillCategory.query.all()
        
        # Get all tool categories
        tool_categories = ToolCategory.query.all()
        
        # Prepare employee-wise skill data
        employee_skill_data = {}
        
        for employee in employees:
            employee_evals = [e for e in evaluations if e.employee_id == employee.id]
            
            # Aggregate skill ratings by category for this employee
            skill_ratings = defaultdict(list)
            
            for eval in employee_evals:
                for skill_eval in eval.skill_evaluations:
                    skill = skill_eval.skill
                    category = skill.category.name
                    skill_ratings[category].append(skill_eval.rating)
            
            # Calculate average for each category
            skill_averages = {}
            for category, ratings in skill_ratings.items():
                if ratings:
                    skill_averages[category] = sum(ratings) / len(ratings)
                else:
                    skill_averages[category] = 0
            
            # Store data for this employee
            employee_skill_data[employee.id] = {
                'employee': employee,
                'averages': skill_averages,
                'overall_average': sum(skill_averages.values()) / len(skill_averages) if skill_averages else 0
            }
        
        # Calculate team averages by skill category
        team_skill_averages = defaultdict(list)
        
        for emp_data in employee_skill_data.values():
            for category, avg in emp_data['averages'].items():
                team_skill_averages[category].append(avg)
        
        team_averages = {}
        for category, avgs in team_skill_averages.items():
            if avgs:
                team_averages[category] = sum(avgs) / len(avgs)
            else:
                team_averages[category] = 0
        
        # Prepare tool proficiency data
        tool_proficiency = defaultdict(lambda: defaultdict(int))
        tool_ownership = defaultdict(lambda: defaultdict(int))
        
        for evaluation in evaluations:
            for tool_eval in evaluation.tool_evaluations:
                tool = tool_eval.tool
                category = tool.category.name
                
                if tool_eval.can_operate:
                    tool_proficiency[category][tool.name] += 1
                    
                if tool_eval.owned:
                    tool_ownership[category][tool.name] += 1
        
        # Identify top performers by category
        top_performers = {}
        
        for category in team_skill_averages.keys():
            category_scores = [(emp_id, data['averages'].get(category, 0)) 
                              for emp_id, data in employee_skill_data.items()]
            category_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Get top 3 performers in this category
            top_category = []
            for emp_id, score in category_scores[:3]:
                if score > 0:  # Only include if they have a score
                    top_category.append({
                        'employee': employee_skill_data[emp_id]['employee'],
                        'score': score
                    })
            
            top_performers[category] = top_category
        
        # Calculate distribution of employees across tiers
        tier_distribution = defaultdict(int)
        for employee in employees:
            tier_distribution[employee.tier] += 1
        
        # Store all collected data
        self.data = {
            'employees': employees,
            'employee_skill_data': employee_skill_data,
            'team_averages': team_averages,
            'skill_categories': skill_categories,
            'tool_categories': tool_categories,
            'tool_proficiency': tool_proficiency,
            'tool_ownership': tool_ownership,
            'top_performers': top_performers,
            'tier_distribution': tier_distribution,
            'report_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'report_filters': {
                'tier': tier,
                'employee_ids': employee_ids
            }
        }
        
        return self.data
    
    def prepare_template_data(self):
        """Prepare data for the report template.
        
        Returns:
            dict: Dictionary containing template variables
        """
        # Convert data to template-friendly format
        team_averages = self.data['team_averages']
        skill_categories = self.data['skill_categories']
        top_performers = self.data['top_performers']
        tier_distribution = self.data['tier_distribution']
        employee_skill_data = self.data['employee_skill_data']
        
        # Format skill data for radar chart
        radar_data = {
            'labels': list(team_averages.keys()),
            'values': [team_averages.get(cat.name, 0) for cat in skill_categories]
        }
        
        # Prepare employee comparison data
        employee_comparison = []
        for emp_id, data in employee_skill_data.items():
            employee = data['employee']
            
            employee_comparison.append({
                'id': employee.id,
                'name': f"{employee.first_name} {employee.last_name}",
                'tier': employee.tier,
                'overall_average': data['overall_average'],
                'categories': data['averages']
            })
        
        # Sort employees by overall average rating (descending)
        employee_comparison.sort(key=lambda x: x['overall_average'], reverse=True)
        
        # Format tool proficiency data
        tool_data = []
        for category, tools in self.data['tool_proficiency'].items():
            for tool_name, count in tools.items():
                ownership_count = self.data['tool_ownership'][category].get(tool_name, 0)
                tool_data.append({
                    'category': category,
                    'tool': tool_name,
                    'proficiency_count': count,
                    'ownership_count': ownership_count,
                    'proficiency_percent': (count / len(self.data['employees'])) * 100,
                    'ownership_percent': (ownership_count / len(self.data['employees'])) * 100
                })
        
        # Sort tool data by proficiency percentage (descending)
        tool_data.sort(key=lambda x: x['proficiency_percent'], reverse=True)
        
        # Create template data dictionary
        template_data = {
            'employees': self.data['employees'],
            'team_averages': team_averages,
            'radar_data': radar_data,
            'top_performers': top_performers,
            'tier_distribution': tier_distribution,
            'employee_comparison': employee_comparison,
            'tool_data': tool_data[:20],  # Limit to top 20 tools
            'report_period': self.data['report_period'],
            'report_filters': self.data['report_filters']
        }
        
        return template_data
    
    def prepare_excel_data(self):
        """Prepare data for the Excel report.
        
        Returns:
            dict: Dictionary containing dataframes for each sheet
        """
        # Team summary sheet
        team_summary = {
            'Total Employees': [len(self.data['employees'])],
            'Report Period': [f"{self.data['report_period']['start_date'].strftime('%Y-%m-%d')} to {self.data['report_period']['end_date'].strftime('%Y-%m-%d')}"],
            'Tier Filter': [self.data['report_filters']['tier'] or 'All Tiers'],
        }
        
        # Add tier distribution
        for tier, count in self.data['tier_distribution'].items():
            team_summary[f"{tier} Count"] = [count]
            
        team_df = pd.DataFrame(team_summary)
        
        # Employee comparison sheet
        employee_data = []
        for emp_id, data in self.data['employee_skill_data'].items():
            employee = data['employee']
            emp_info = {
                'ID': employee.id,
                'Name': f"{employee.first_name} {employee.last_name}",
                'Tier': employee.tier,
                'Overall Average': round(data['overall_average'], 2)
            }
            
            # Add category averages
            for category, avg in data['averages'].items():
                emp_info[f"{category} Average"] = round(avg, 2)
                
            employee_data.append(emp_info)
            
        employee_df = pd.DataFrame(employee_data)
        
        # Sort by overall average (descending)
        employee_df = employee_df.sort_values('Overall Average', ascending=False)
        
        # Team average by category sheet
        team_avg_data = []
        for category, avg in self.data['team_averages'].items():
            team_avg_data.append({
                'Category': category,
                'Team Average': round(avg, 2),
                'Max Possible': 5,
                'Percentage': f"{round((avg / 5) * 100, 2)}%"
            })
        team_avg_df = pd.DataFrame(team_avg_data)
        
        # Tool proficiency sheet
        tool_data = []
        for category, tools in self.data['tool_proficiency'].items():
            for tool_name, count in tools.items():
                ownership_count = self.data['tool_ownership'][category].get(tool_name, 0)
                tool_data.append({
                    'Category': category,
                    'Tool': tool_name,
                    'Proficiency Count': count,
                    'Ownership Count': ownership_count,
                    'Proficiency %': f"{round((count / len(self.data['employees'])) * 100, 2)}%",
                    'Ownership %': f"{round((ownership_count / len(self.data['employees'])) * 100, 2)}%"
                })
        tool_df = pd.DataFrame(tool_data)
        
        # Sort by proficiency count (descending)
        tool_df = tool_df.sort_values('Proficiency Count', ascending=False)
        
        # Top performers sheet
        top_performers_data = []
        for category, performers in self.data['top_performers'].items():
            for idx, performer in enumerate(performers, 1):
                top_performers_data.append({
                    'Category': category,
                    'Rank': idx,
                    'Employee ID': performer['employee'].id,
                    'Employee Name': f"{performer['employee'].first_name} {performer['employee'].last_name}",
                    'Score': round(performer['score'], 2)
                })
        top_performers_df = pd.DataFrame(top_performers_data)
        
        # Return dictionary of dataframes
        return {
            'Team Summary': team_df,
            'Employee Comparison': employee_df,
            'Category Averages': team_avg_df,
            'Tool Proficiency': tool_df,
            'Top Performers': top_performers_df
        }
