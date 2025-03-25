"""
Employee routes for the KPI system
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.employee import Employee
from app.models.skill import Skill, SkillCategory
from app.models.tool import Tool, ToolCategory
from app.models.evaluation import Evaluation, SkillEvaluation, ToolEvaluation, SpecialSkill
from app import db
from datetime import datetime
from sqlalchemy import func, desc, and_

# Create blueprint
bp = Blueprint('employees', __name__, url_prefix='/employees')

@bp.route('/')
def index():
    """
    List all employees with filtering options
    """
    # Get filter parameters
    search = request.args.get('search', '')
    tier = request.args.get('tier', '')
    status = request.args.get('status', '')
    
    # Base query
    query = Employee.query
    
    # Apply filters
    if search:
        query = query.filter(Employee.name.ilike(f'%{search}%') | 
                           Employee.phone.ilike(f'%{search}%'))
    
    if tier:
        query = query.filter(Employee.tier == tier)
    
    if status == 'active':
        query = query.filter(Employee.active == True)
    elif status == 'inactive':
        query = query.filter(Employee.active == False)
    
    # Get results ordered by name
    employees = query.order_by(Employee.name).all()
    
    return render_template('employees/index.html', employees=employees)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    """
    Create a new employee - GET displays form, POST processes submission
    """
    if request.method == 'POST':
        # Process the submitted form
        name = request.form.get('name')
        phone = request.form.get('phone', '')
        tier = request.form.get('tier')
        hire_date_str = request.form.get('hire_date', '')
        active = 'active' in request.form
        
        error = None
        if not name:
            error = 'Name is required.'
        elif not tier:
            error = 'Tier is required.'
        
        if error is None:
            # Parse hire date if provided
            hire_date = None
            if hire_date_str:
                try:
                    hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
                except ValueError:
                    error = 'Invalid date format. Please use YYYY-MM-DD.'
            
            if error is None:
                # Create new employee record
                employee = Employee(
                    name=name,
                    phone=phone if phone else None,
                    tier=tier,
                    hire_date=hire_date,
                    active=active
                )
                db.session.add(employee)
                db.session.commit()
                
                flash(f'Employee "{name}" successfully created!', 'success')
                return redirect(url_for('employees.view', employee_id=employee.employee_id))
        
        flash(error, 'danger')
    
    # If GET request or validation error, display the form
    return render_template('employees/create.html')

@bp.route('/<int:employee_id>/view')
def view(employee_id):
    """
    View details of an employee including evaluations, skills, and tools
    """
    employee = Employee.query.get_or_404(employee_id)
    
    # Get all evaluations for this employee
    evaluations = Evaluation.query.filter_by(employee_id=employee_id)\
                                .order_by(Evaluation.evaluation_date.desc())\
                                .all()
    
    # Get the most recent evaluation
    last_evaluation = evaluations[0] if evaluations else None
    
    # Get skill categories
    skill_categories = SkillCategory.query.order_by(SkillCategory.display_order).all()
    
    # Calculate average rating for each skill category
    category_ratings = {}
    
    for category in skill_categories:
        # Query average rating for this category
        rating_query = db.session.query(
            func.avg(SkillEvaluation.rating).label('avg_rating')
        ).join(
            Evaluation, SkillEvaluation.evaluation_id == Evaluation.evaluation_id
        ).join(
            Skill, SkillEvaluation.skill_id == Skill.skill_id
        ).filter(
            Evaluation.employee_id == employee_id,
            Skill.category_id == category.category_id
        )
        
        avg_rating = rating_query.scalar()
        category_ratings[category.category_id] = avg_rating if avg_rating else 0
    
    # Get tool categories and tools
    tool_categories = ToolCategory.query.order_by(ToolCategory.display_order).all()
    
    # Group tools by category
    tools_by_category = {}
    for category in tool_categories:
        tools_by_category[category.category_id] = Tool.query.filter_by(category_id=category.category_id).all()
    
    # Get tool proficiency data
    # 1. Tools the employee can operate
    can_operate_tools = set()
    tool_evals = db.session.query(
        ToolEvaluation.tool_id
    ).join(
        Evaluation, ToolEvaluation.evaluation_id == Evaluation.evaluation_id
    ).filter(
        Evaluation.employee_id == employee_id,
        ToolEvaluation.can_operate == True
    ).all()
    
    for tool_eval in tool_evals:
        can_operate_tools.add(tool_eval.tool_id)
    
    # 2. Tools the employee owns
    owns_tools = set()
    tool_evals = db.session.query(
        ToolEvaluation.tool_id
    ).join(
        Evaluation, ToolEvaluation.evaluation_id == Evaluation.evaluation_id
    ).filter(
        Evaluation.employee_id == employee_id,
        ToolEvaluation.owns_tool == True
    ).all()
    
    for tool_eval in tool_evals:
        owns_tools.add(tool_eval.tool_id)
    
    # Calculate tool counts by category
    category_tool_counts = {}
    for category in tool_categories:
        # Count tools in this category that the employee can operate
        count = db.session.query(func.count(Tool.tool_id)).filter(
            Tool.category_id == category.category_id,
            Tool.tool_id.in_(can_operate_tools)
        ).scalar()
        
        category_tool_counts[category.category_id] = count
    
    # Calculate overall tool proficiency percentage
    total_tools = db.session.query(func.count(Tool.tool_id)).scalar()
    tool_proficiency = (len(can_operate_tools) / total_tools * 100) if total_tools > 0 else 0
    
    # Get special skills
    special_skills = db.session.query(
        SpecialSkill
    ).join(
        Evaluation, SpecialSkill.evaluation_id == Evaluation.evaluation_id
    ).filter(
        Evaluation.employee_id == employee_id
    ).all()
    
    return render_template(
        'employees/view.html',
        employee=employee,
        evaluations=evaluations,
        last_evaluation=last_evaluation,
        skill_categories=skill_categories,
        category_ratings=category_ratings,
        tool_categories=tool_categories,
        tools_by_category=tools_by_category,
        can_operate_tools=can_operate_tools,
        owns_tools=owns_tools,
        category_tool_counts=category_tool_counts,
        tool_proficiency=tool_proficiency,
        special_skills=special_skills
    )

@bp.route('/<int:employee_id>/edit', methods=('GET', 'POST'))
def edit(employee_id):
    """
    Edit an existing employee
    """
    employee = Employee.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        # Process the submitted form
        name = request.form.get('name')
        phone = request.form.get('phone', '')
        tier = request.form.get('tier')
        hire_date_str = request.form.get('hire_date', '')
        active = 'active' in request.form
        
        error = None
        if not name:
            error = 'Name is required.'
        elif not tier:
            error = 'Tier is required.'
        
        if error is None:
            # Parse hire date if provided
            hire_date = None
            if hire_date_str:
                try:
                    hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
                except ValueError:
                    error = 'Invalid date format. Please use YYYY-MM-DD.'
            
            if error is None:
                # Update employee record
                employee.name = name
                employee.phone = phone if phone else None
                employee.tier = tier
                employee.hire_date = hire_date
                employee.active = active
                employee.updated_at = datetime.now()
                
                db.session.commit()
                
                flash(f'Employee "{name}" successfully updated!', 'success')
                return redirect(url_for('employees.view', employee_id=employee.employee_id))
        
        flash(error, 'danger')
    
    # Calculate statistics for display
    # Get all evaluations for this employee
    evaluations = Evaluation.query.filter_by(employee_id=employee_id).all()
    
    # Calculate average skill rating
    avg_skill_rating = 0
    if evaluations:
        skill_ratings = db.session.query(
            func.avg(SkillEvaluation.rating).label('avg_rating')
        ).join(
            Evaluation, SkillEvaluation.evaluation_id == Evaluation.evaluation_id
        ).filter(
            Evaluation.employee_id == employee_id
        ).scalar()
        
        avg_skill_rating = skill_ratings if skill_ratings else 0
    
    # Calculate tool proficiency
    total_tools = db.session.query(func.count(Tool.tool_id)).scalar()
    if total_tools > 0:
        can_operate_count = db.session.query(
            func.count(ToolEvaluation.tool_id.distinct())
        ).join(
            Evaluation, ToolEvaluation.evaluation_id == Evaluation.evaluation_id
        ).filter(
            Evaluation.employee_id == employee_id,
            ToolEvaluation.can_operate == True
        ).scalar()
        
        tools_proficiency = (can_operate_count / total_tools * 100)
    else:
        tools_proficiency = 0
    
    return render_template(
        'employees/edit.html',
        employee=employee,
        evaluations=evaluations,
        avg_skill_rating=avg_skill_rating,
        tools_proficiency=tools_proficiency
    )

@bp.route('/<int:employee_id>/delete', methods=('POST',))
def delete(employee_id):
    """
    Delete an employee
    """
    employee = Employee.query.get_or_404(employee_id)
    
    try:
        # Store employee name for flash message
        name = employee.name
        
        # Delete the employee (and cascade delete related records)
        db.session.delete(employee)
        db.session.commit()
        
        flash(f'Employee "{name}" successfully deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'danger')
    
    return redirect(url_for('employees.index'))

# API endpoints for AJAX operations
@bp.route('/api/list')
def api_list():
    """
    Return JSON list of employees
    """
    # Get filter parameters
    tier = request.args.get('tier', '')
    status = request.args.get('status', '')
    
    # Base query
    query = Employee.query
    
    # Apply filters
    if tier:
        query = query.filter(Employee.tier == tier)
    
    if status == 'active':
        query = query.filter(Employee.active == True)
    elif status == 'inactive':
        query = query.filter(Employee.active == False)
    
    # Get results ordered by name
    employees = query.order_by(Employee.name).all()
    
    return jsonify([employee.to_dict() for employee in employees])

@bp.route('/api/<int:employee_id>')
def api_get(employee_id):
    """
    Return JSON data for a specific employee
    """
    employee = Employee.query.get_or_404(employee_id)
    return jsonify(employee.to_dict())

@bp.route('/api/tiers')
def api_tiers():
    """
    Return list of valid employee tiers
    """
    tiers = [
        "Apprentice",
        "Handyman",
        "Craftsman",
        "Master Craftsman",
        "Lead Craftsman"
    ]
    return jsonify(tiers)
