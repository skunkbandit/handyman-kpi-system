"""
Skills Analysis Report implementation.
"""
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.employee import Employee
from app.models.evaluation import Evaluation, SkillEvaluation
from app.models.skill import Skill, SkillCategory
from app import db
from .base import ReportGenerator


class SkillsAnalysisReport(ReportGenerator):
    """Skills Analysis Report Generator.
    
    Generates detailed analysis of skill distribution across the organization.
    """
    
    def __init__(self):
        """Initialize the Skills Analysis Report generator."""
        super().__init__(
            title="Skills Analysis Report",
            description="Detailed analysis of skill distribution across the organization",
            report_type="skills"
        )
    
    def collect_data(self, category_id=None, tier=None, start_date=None, end_date=None, **kwargs):
        """Collect all data needed for the skills analysis report.
        
        Args:
            category_id (int, optional): Filter by skill category ID
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
        
        # Get skill categories
        if category_id:
            categories = [SkillCategory.query.get(category_id)]
            if not categories[0]:
                raise ValueError(f"Skill category with ID {category_id} not found")
        else:
            categories = SkillCategory.query.all()
            
        # Get skills within selected categories
        category_ids = [category.id for category in categories]
        skills = Skill.query.filter(Skill.category_id.in_(category_ids)).all()
        
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
        
        # Collect skill ratings across all evaluations
        skill_ratings = defaultdict(list)
        employee_skill_ratings = defaultdict(lambda: defaultdict(list))
        
        for evaluation in evaluations:
            for skill_eval in evaluation.skill_evaluations:
                skill = skill_eval.skill
                
                # Skip if not in our target categories
                if skill.category_id not in category_ids:
                    continue
                    
                # Add to overall skill ratings
                skill_ratings[skill.id].append({
                    'skill_name': skill.name,
                    'category_name': skill.category.name,
                    'rating': skill_eval.rating,
                    'employee_id': evaluation.employee_id,
                    'date': evaluation.date
                })
                
                # Add to employee-specific ratings
                employee_skill_ratings[evaluation.employee_id][skill.id].append({
                    'rating': skill_eval.rating,
                    'date': evaluation.date
                })
        
        # Calculate skill averages across all employees
        skill_averages = {}
        for skill_id, ratings in skill_ratings.items():
            all_ratings = [r['rating'] for r in ratings]
            if all_ratings:
                skill_averages[skill_id] = {
                    'skill_name': ratings[0]['skill_name'],
                    'category_name': ratings[0]['category_name'],
                    'average_rating': sum(all_ratings) / len(all_ratings),
                    'count': len(all_ratings),
                    'employee_count': len(set(r['employee_id'] for r in ratings))
                }
        
        # Calculate average ratings by category
        category_averages = defaultdict(list)
        for skill_id, data in skill_averages.items():
            category_name = data['category_name']
            category_averages[category_name].append(data['average_rating'])
        
        category_avg = {}
        for category_name, averages in category_averages.items():
            if averages:
                category_avg[category_name] = sum(averages) / len(averages)
            else:
                category_avg[category_name] = 0
        
        # Identify skill gaps (skills with lowest average ratings)
        skill_gaps = []
        for skill_id, data in skill_averages.items():
            skill_gaps.append({
                'skill_id': skill_id,
                'skill_name': data['skill_name'],
                'category_name': data['category_name'],
                'average_rating': data['average_rating'],
                'gap': 5 - data['average_rating']  # Max rating (5) minus current average
            })
        
        # Sort skill gaps by gap size (descending)
        skill_gaps.sort(key=lambda x: x['gap'], reverse=True)
        
        # Track skill development over time
        # Group by month for time series analysis
        monthly_skill_data = defaultdict(lambda: defaultdict(list))
        
        for skill_id, ratings in skill_ratings.items():
            for rating in ratings:
                month_key = rating['date'].strftime('%Y-%m')
                monthly_skill_data[month_key][skill_id].append(rating['rating'])
        
        # Calculate monthly averages
        skill_trends = defaultdict(list)
        
        for month_key in sorted(monthly_skill_data.keys()):
            for skill_id, ratings in monthly_skill_data[month_key].items():
                if skill_id in skill_averages:  # Only track skills we calculated averages for
                    skill_trends[skill_id].append({
                        'month': month_key,
                        'average': sum(ratings) / len(ratings) if ratings else 0
                    })
        
        # Calculate skill distribution by tier (if all tiers were included)
        tier_skill_averages = defaultdict(lambda: defaultdict(list))
        
        for employee in employees:
            for skill_id in skill_averages.keys():
                emp_ratings = employee_skill_ratings.get(employee.id, {}).get(skill_id, [])
                if emp_ratings:
                    ratings = [r['rating'] for r in emp_ratings]
                    tier_skill_averages[employee.tier][skill_id].append(sum(ratings) / len(ratings))
        
        tier_skill_avg = {}
        for tier_name, skill_data in tier_skill_averages.items():
            tier_skill_avg[tier_name] = {}
            for skill_id, averages in skill_data.items():
                if averages:
                    tier_skill_avg[tier_name][skill_id] = sum(averages) / len(averages)
                else:
                    tier_skill_avg[tier_name][skill_id] = 0
        
        # Store all collected data
        self.data = {
            'categories': categories,
            'skills': skills,
            'employees': employees,
            'skill_ratings': skill_ratings,
            'skill_averages': skill_averages,
            'category_averages': category_avg,
            'skill_gaps': skill_gaps,
            'skill_trends': skill_trends,
            'tier_skill_averages': tier_skill_avg,
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
        category_averages = self.data['category_averages']
        
        # Format category data for bar chart
        category_chart_data = {
            'labels': [cat.name for cat in categories],
            'values': [category_averages.get(cat.name, 0) for cat in categories]
        }
        
        # Prepare skill gap data
        skill_gaps = self.data['skill_gaps'][:10]  # Top 10 skill gaps
        
        skill_gap_chart_data = {
            'labels': [gap['skill_name'] for gap in skill_gaps],
            'values': [gap['gap'] for gap in skill_gaps]
        }
        
        # Prepare trend data for selected skills (top 5 most common)
        top_skills = sorted(
            self.data['skill_averages'].items(), 
            key=lambda x: x[1]['count'], 
            reverse=True
        )[:5]
        
        trend_data = {}
        for skill_id, data in top_skills:
            if skill_id in self.data['skill_trends']:
                skill_name = data['skill_name']
                trend_data[skill_name] = {
                    'months': [t['month'] for t in self.data['skill_trends'][skill_id]],
                    'values': [t['average'] for t in self.data['skill_trends'][skill_id]]
                }
        
        # Prepare tier comparison data
        tier_comparison = {}
        tier_skill_averages = self.data['tier_skill_averages']
        
        if tier_skill_averages:
            # Get skills that have data for all tiers
            all_skill_ids = set()
            for tier, skill_data in tier_skill_averages.items():
                all_skill_ids.update(skill_data.keys())
            
            for skill_id in all_skill_ids:
                if skill_id in self.data['skill_averages']:
                    skill_name = self.data['skill_averages'][skill_id]['skill_name']
                    tier_comparison[skill_name] = {
                        tier: skill_data.get(skill_id, 0) 
                        for tier, skill_data in tier_skill_averages.items()
                    }
        
        # Create template data dictionary
        template_data = {
            'categories': categories,
            'category_averages': category_averages,
            'category_chart_data': category_chart_data,
            'skill_averages': self.data['skill_averages'],
            'skill_gaps': skill_gaps,
            'skill_gap_chart_data': skill_gap_chart_data,
            'trend_data': trend_data,
            'tier_comparison': tier_comparison,
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
            'Average Rating': [],
            'Number of Skills': [],
            'Max Possible': [],
            'Percentage': []
        }
        
        for category in self.data['categories']:
            category_skills = [s for s in self.data['skills'] if s.category_id == category.id]
            avg_rating = self.data['category_averages'].get(category.name, 0)
            
            summary_data['Category'].append(category.name)
            summary_data['Average Rating'].append(round(avg_rating, 2))
            summary_data['Number of Skills'].append(len(category_skills))
            summary_data['Max Possible'].append(5)
            summary_data['Percentage'].append(f"{round((avg_rating / 5) * 100, 2)}%")
            
        summary_df = pd.DataFrame(summary_data)
        
        # Skills details sheet
        skills_data = {
            'Skill ID': [],
            'Skill Name': [],
            'Category': [],
            'Average Rating': [],
            'Evaluations Count': [],
            'Employee Count': [],
            'Gap Score': []
        }
        
        for skill_id, data in self.data['skill_averages'].items():
            skills_data['Skill ID'].append(skill_id)
            skills_data['Skill Name'].append(data['skill_name'])
            skills_data['Category'].append(data['category_name'])
            skills_data['Average Rating'].append(round(data['average_rating'], 2))
            skills_data['Evaluations Count'].append(data['count'])
            skills_data['Employee Count'].append(data['employee_count'])
            skills_data['Gap Score'].append(round(5 - data['average_rating'], 2))
            
        skills_df = pd.DataFrame(skills_data)
        
        # Sort by gap score (descending)
        skills_df = skills_df.sort_values('Gap Score', ascending=False)
        
        # Tier comparison sheet (if available)
        tier_comparison_df = None
        if self.data['tier_skill_averages']:
            tier_data = {
                'Skill ID': [],
                'Skill Name': [],
                'Category': []
            }
            
            # Add columns for each tier
            tiers = sorted(self.data['tier_skill_averages'].keys())
            for tier in tiers:
                tier_data[tier] = []
            
            # Add data rows
            for skill_id in self.data['skill_averages'].keys():
                skill_name = self.data['skill_averages'][skill_id]['skill_name']
                category_name = self.data['skill_averages'][skill_id]['category_name']
                
                tier_data['Skill ID'].append(skill_id)
                tier_data['Skill Name'].append(skill_name)
                tier_data['Category'].append(category_name)
                
                for tier in tiers:
                    tier_skill_avg = self.data['tier_skill_averages'].get(tier, {})
                    avg_rating = tier_skill_avg.get(skill_id, 0)
                    tier_data[tier].append(round(avg_rating, 2))
            
            tier_comparison_df = pd.DataFrame(tier_data)
        
        # Trend analysis sheet
        trend_data = {
            'Month': [],
            'Skill ID': [],
            'Skill Name': [],
            'Category': [],
            'Average Rating': []
        }
        
        for skill_id, trends in self.data['skill_trends'].items():
            if skill_id in self.data['skill_averages']:
                skill_name = self.data['skill_averages'][skill_id]['skill_name']
                category_name = self.data['skill_averages'][skill_id]['category_name']
                
                for trend in trends:
                    trend_data['Month'].append(trend['month'])
                    trend_data['Skill ID'].append(skill_id)
                    trend_data['Skill Name'].append(skill_name)
                    trend_data['Category'].append(category_name)
                    trend_data['Average Rating'].append(round(trend['average'], 2))
        
        trend_df = pd.DataFrame(trend_data)
        
        # Create the return dictionary
        result = {
            'Category Summary': summary_df,
            'Skill Details': skills_df,
            'Trend Analysis': trend_df
        }
        
        # Add tier comparison if available
        if tier_comparison_df is not None:
            result['Tier Comparison'] = tier_comparison_df
            
        return result
