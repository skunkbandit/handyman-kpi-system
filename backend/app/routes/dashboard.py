"""
Dashboard routes for the KPI system
"""
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models.employee import Employee
from app.models.skill import Skill, SkillCategory
from app.models.tool import Tool, ToolCategory
from app.models.evaluation import Evaluation, SkillEvaluation, ToolEvaluation
from sqlalchemy import func, desc, and_
from app import db
from datetime import datetime, timedelta
import calendar

# Create blueprint
bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    """
    Display the main dashboard with KPI statistics and charts
    """
    # Get filter parameters
    employee_id = request.args.get('employee_id', type=int)
    category_id = request.args.get('category_id', type=int)
    tier = request.args.get('tier')
    date_range = request.args.get('date_range', 'all')
    
    # For non-manager users, restrict view to their own data if they are linked to an employee
    if not current_user.is_manager() and current_user.employee_id:
        employee_id = current_user.employee_id
    
    # Base query for all evaluations
    base_query = Evaluation.query
    
    # Apply filters
    if employee_id:
        base_query = base_query.filter(Evaluation.employee_id == employee_id)
    
    if tier:
        base_query = base_query.join(Employee).filter(Employee.tier == tier)
    
    # Date range filter
    today = datetime.now().date()
    if date_range == 'year':
        start_date = today - timedelta(days=365)
        base_query = base_query.filter(Evaluation.evaluation_date >= start_date)
    elif date_range == 'quarter':
        start_date = today - timedelta(days=90)
        base_query = base_query.filter(Evaluation.evaluation_date >= start_date)
    elif date_range == 'month':
        start_date = today - timedelta(days=30)
        base_query = base_query.filter(Evaluation.evaluation_date >= start_date)
    
    # Get all employees for the filter dropdown
    # Managers can see all, employees only see themselves
    if current_user.is_manager():
        employees = Employee.query.filter_by(active=True).all()
    else:
        if current_user.employee_id:
            employees = [Employee.query.get(current_user.employee_id)]
        else:
            employees = []
    
    # Get all skill categories
    skill_categories = SkillCategory.query.order_by(SkillCategory.display_order).all()
    
    # Calculate statistics
    stats = {
        'total_employees': Employee.query.filter_by(active=True).count(),
        'total_evaluations': base_query.count(),
        'avg_skill_rating': 0,
        'tools_percentage': 0
    }
    
    # Calculate average skill rating
    skill_rating_query = db.session.query(
        func.avg(SkillEvaluation.rating).label('avg_rating')
    ).join(
        Evaluation, SkillEvaluation.evaluation_id == Evaluation.evaluation_id
    )
    
    # Apply the same filters to skill evaluations
    if employee_id:
        skill_rating_query = skill_rating_query.filter(Evaluation.employee_id == employee_id)
    if tier:
        skill_rating_query = skill_rating_query.join(Employee).filter(Employee.tier == tier)
    if date_range != 'all':
        skill_rating_query = skill_rating_query.filter(Evaluation.evaluation_date >= start_date)
    if category_id:
        skill_rating_query = skill_rating_query.join(
            Skill, SkillEvaluation.skill_id == Skill.skill_id
        ).filter(Skill.category_id == category_id)
    
    avg_rating_result = skill_rating_query.first()
    stats['avg_skill_rating'] = avg_rating_result.avg_rating if avg_rating_result.avg_rating else 0
    
    # Calculate tool proficiency percentage
    tool_query = db.session.query(
        func.count(ToolEvaluation.tool_evaluation_id).label('total_tools'),
        func.sum(func.cast(ToolEvaluation.can_operate, db.Integer)).label('can_operate_count')
    ).join(
        Evaluation, ToolEvaluation.evaluation_id == Evaluation.evaluation_id
    )
    
    # Apply the same filters to tool evaluations
    if employee_id:
        tool_query = tool_query.filter(Evaluation.employee_id == employee_id)
    if tier:
        tool_query = tool_query.join(Employee).filter(Employee.tier == tier)
    if date_range != 'all':
        tool_query = tool_query.filter(Evaluation.evaluation_date >= start_date)
    
    tool_result = tool_query.first()
    if tool_result.total_tools > 0:
        stats['tools_percentage'] = (tool_result.can_operate_count / tool_result.total_tools) * 100
    
    # Get top skills (highest average ratings)
    top_skills_query = db.session.query(
        Skill,
        func.avg(SkillEvaluation.rating).label('avg_rating')
    ).join(
        SkillEvaluation, Skill.skill_id == SkillEvaluation.skill_id
    ).join(
        Evaluation, SkillEvaluation.evaluation_id == Evaluation.evaluation_id
    ).group_by(
        Skill.skill_id
    ).order_by(
        desc('avg_rating')
    )
    
    # Apply filters to top skills query
    if employee_id:
        top_skills_query = top_skills_query.filter(Evaluation.employee_id == employee_id)
    if tier:
        top_skills_query = top_skills_query.join(Employee).filter(Employee.tier == tier)
    if date_range != 'all':
        top_skills_query = top_skills_query.filter(Evaluation.evaluation_date >= start_date)
    if category_id:
        top_skills_query = top_skills_query.filter(Skill.category_id == category_id)
    
    # Get top 5 skills
    top_skills_results = top_skills_query.limit(5).all()
    top_skills = []
    for skill, avg_rating in top_skills_results:
        skill_dict = skill.to_dict()
        skill_dict['avg_rating'] = avg_rating
        skill_dict['category'] = SkillCategory.query.get(skill.category_id)
        top_skills.append(skill_dict)
    
    # Get improvement areas (lowest average ratings)
    improvement_skills_query = db.session.query(
        Skill,
        func.avg(SkillEvaluation.rating).label('avg_rating')
    ).join(
        SkillEvaluation, Skill.skill_id == SkillEvaluation.skill_id
    ).join(
        Evaluation, SkillEvaluation.evaluation_id == Evaluation.evaluation_id
    ).group_by(
        Skill.skill_id
    ).order_by(
        'avg_rating'
    )
    
    # Apply filters to improvement skills query
    if employee_id:
        improvement_skills_query = improvement_skills_query.filter(Evaluation.employee_id == employee_id)
    if tier:
        improvement_skills_query = improvement_skills_query.join(Employee).filter(Employee.tier == tier)
    if date_range != 'all':
        improvement_skills_query = improvement_skills_query.filter(Evaluation.evaluation_date >= start_date)
    if category_id:
        improvement_skills_query = improvement_skills_query.filter(Skill.category_id == category_id)
    
    # Get bottom 5 skills
    improvement_skills_results = improvement_skills_query.limit(5).all()
    improvement_skills = []
    for skill, avg_rating in improvement_skills_results:
        skill_dict = skill.to_dict()
        skill_dict['avg_rating'] = avg_rating
        skill_dict['category'] = SkillCategory.query.get(skill.category_id)
        improvement_skills.append(skill_dict)
    
    # Get recent evaluations
    recent_evaluations = base_query.order_by(Evaluation.evaluation_date.desc()).limit(5).all()
    
    # Calculate average ratings by category for radar chart
    category_avg_ratings = {}
    for category in skill_categories:
        category_query = db.session.query(
            func.avg(SkillEvaluation.rating).label('avg_rating')
        ).join(
            Evaluation, SkillEvaluation.evaluation_id == Evaluation.evaluation_id
        ).join(
            Skill, SkillEvaluation.skill_id == Skill.skill_id
        ).filter(
            Skill.category_id == category.category_id
        )
        
        # Apply filters
        if employee_id:
            category_query = category_query.filter(Evaluation.employee_id == employee_id)
        if tier:
            category_query = category_query.join(Employee).filter(Employee.tier == tier)
        if date_range != 'all':
            category_query = category_query.filter(Evaluation.evaluation_date >= start_date)
        
        avg_rating = category_query.scalar()
        category_avg_ratings[category.category_id] = avg_rating if avg_rating else 0
    
    # Calculate progress over time for line chart
    # Determine date range for chart
    if date_range == 'all':
        # Use the last 12 months
        end_date = today
        start_date = end_date.replace(year=end_date.year - 1, day=1)
    elif date_range == 'year':
        end_date = today
        start_date = end_date.replace(year=end_date.year - 1)
    elif date_range == 'quarter':
        end_date = today
        start_date = end_date - timedelta(days=90)
    else:  # month
        end_date = today
        start_date = end_date - timedelta(days=30)
    
    # Generate list of months for x-axis
    progress_dates = []
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        progress_dates.append(current_date)
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Calculate average ratings by category and month
    category_progress = {}
    for category in skill_categories:
        for date in progress_dates:
            # Calculate next month
            if date.month == 12:
                next_month = date.replace(year=date.year + 1, month=1)
            else:
                next_month = date.replace(month=date.month + 1)
            
            # Query average rating for this category in this month
            month_query = db.session.query(
                func.avg(SkillEvaluation.rating).label('avg_rating')
            ).join(
                Evaluation, SkillEvaluation.evaluation_id == Evaluation.evaluation_id
            ).join(
                Skill, SkillEvaluation.skill_id == Skill.skill_id
            ).filter(
                Skill.category_id == category.category_id,
                Evaluation.evaluation_date >= date,
                Evaluation.evaluation_date < next_month
            )
            
            # Apply employee and tier filters
            if employee_id:
                month_query = month_query.filter(Evaluation.employee_id == employee_id)
            if tier:
                month_query = month_query.join(Employee).filter(Employee.tier == tier)
            
            avg_rating = month_query.scalar()
            category_progress[(category.category_id, date.strftime("%Y-%m"))] = avg_rating if avg_rating else 0
    
    return render_template(
        'dashboard/index.html',
        stats=stats,
        employees=employees,
        skill_categories=skill_categories,
        top_skills=top_skills,
        improvement_skills=improvement_skills,
        recent_evaluations=recent_evaluations,
        category_avg_ratings=category_avg_ratings,
        progress_dates=progress_dates,
        category_progress=category_progress,
        filters={
            'employee_id': employee_id,
            'category_id': category_id,
            'tier': tier,
            'date_range': date_range
        }
    )
