"""
Evaluation routes for the KPI system
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.employee import Employee
from app.models.skill import Skill, SkillCategory
from app.models.tool import Tool, ToolCategory
from app.models.evaluation import Evaluation, SkillEvaluation, ToolEvaluation, SpecialSkill
from app import db
from datetime import datetime

# Create blueprint
bp = Blueprint('evaluations', __name__, url_prefix='/evaluations')

@bp.route('/')
def index():
    """
    List all evaluations
    """
    evaluations = Evaluation.query.order_by(Evaluation.evaluation_date.desc()).all()
    return render_template('evaluations/index.html', evaluations=evaluations)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    """
    Create a new evaluation - GET displays form, POST processes submission
    """
    # Get all employees for the dropdown
    employees = Employee.query.filter_by(active=True).all()
    
    if request.method == 'POST':
        # Process the submitted form
        employee_id = request.form.get('employee_id')
        evaluator_id = request.form.get('evaluator_id')
        evaluation_date = request.form.get('evaluation_date')
        notes = request.form.get('notes')

        error = None
        if not employee_id:
            error = 'Employee is required.'
        elif not evaluation_date:
            error = 'Evaluation date is required.'

        if error is None:
            # Create new evaluation record
            evaluation = Evaluation(
                employee_id=employee_id,
                evaluator_id=evaluator_id,
                evaluation_date=datetime.strptime(evaluation_date, '%Y-%m-%d').date(),
                notes=notes
            )
            db.session.add(evaluation)
            db.session.commit()

            # Get the new evaluation ID to use for skill and tool evaluations
            evaluation_id = evaluation.evaluation_id
            
            # Process skill evaluations
            skill_categories = SkillCategory.query.all()
            for category in skill_categories:
                for skill in category.skills:
                    skill_rating = request.form.get(f'skill_{skill.skill_id}')
                    if skill_rating and skill_rating.isdigit():
                        skill_eval = SkillEvaluation(
                            evaluation_id=evaluation_id,
                            skill_id=skill.skill_id,
                            rating=int(skill_rating)
                        )
                        db.session.add(skill_eval)
            
            # Process tool evaluations
            tool_categories = ToolCategory.query.all()
            for category in tool_categories:
                for tool in category.tools:
                    can_operate = request.form.get(f'tool_operate_{tool.tool_id}') == 'on'
                    owns_tool = request.form.get(f'tool_own_{tool.tool_id}') == 'on'
                    if can_operate or owns_tool:
                        tool_eval = ToolEvaluation(
                            evaluation_id=evaluation_id,
                            tool_id=tool.tool_id,
                            can_operate=can_operate,
                            owns_tool=owns_tool
                        )
                        db.session.add(tool_eval)
            
            # Process special skills
            special_skills = request.form.get('special_skills')
            if special_skills:
                for skill_name in special_skills.split(','):
                    if skill_name.strip():
                        special_skill = SpecialSkill(
                            evaluation_id=evaluation_id,
                            skill_name=skill_name.strip()
                        )
                        db.session.add(special_skill)
            
            db.session.commit()
            flash('Evaluation successfully created!', 'success')
            return redirect(url_for('evaluations.view', evaluation_id=evaluation_id))
        else:
            flash(error, 'danger')
    
    # Get all categories, skills, and tools for the form
    skill_categories = SkillCategory.query.order_by(SkillCategory.display_order).all()
    tool_categories = ToolCategory.query.order_by(ToolCategory.display_order).all()
    
    return render_template(
        'evaluations/create.html',
        employees=employees,
        skill_categories=skill_categories,
        tool_categories=tool_categories
    )

@bp.route('/<int:evaluation_id>/view')
def view(evaluation_id):
    """
    View details of an evaluation
    """
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    return render_template('evaluations/view.html', evaluation=evaluation)

@bp.route('/<int:evaluation_id>/edit', methods=('GET', 'POST'))
def edit(evaluation_id):
    """
    Edit an existing evaluation
    """
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    employees = Employee.query.filter_by(active=True).all()
    
    if request.method == 'POST':
        # Similar to create but update existing records
        evaluation.employee_id = request.form.get('employee_id')
        evaluation.evaluator_id = request.form.get('evaluator_id')
        evaluation.evaluation_date = datetime.strptime(request.form.get('evaluation_date'), '%Y-%m-%d').date()
        evaluation.notes = request.form.get('notes')

        # Clear existing skill and tool evaluations to replace with new ones
        SkillEvaluation.query.filter_by(evaluation_id=evaluation_id).delete()
        ToolEvaluation.query.filter_by(evaluation_id=evaluation_id).delete()
        SpecialSkill.query.filter_by(evaluation_id=evaluation_id).delete()
        
        # Process skill evaluations
        skill_categories = SkillCategory.query.all()
        for category in skill_categories:
            for skill in category.skills:
                skill_rating = request.form.get(f'skill_{skill.skill_id}')
                if skill_rating and skill_rating.isdigit():
                    skill_eval = SkillEvaluation(
                        evaluation_id=evaluation_id,
                        skill_id=skill.skill_id,
                        rating=int(skill_rating)
                    )
                    db.session.add(skill_eval)
        
        # Process tool evaluations
        tool_categories = ToolCategory.query.all()
        for category in tool_categories:
            for tool in category.tools:
                can_operate = request.form.get(f'tool_operate_{tool.tool_id}') == 'on'
                owns_tool = request.form.get(f'tool_own_{tool.tool_id}') == 'on'
                if can_operate or owns_tool:
                    tool_eval = ToolEvaluation(
                        evaluation_id=evaluation_id,
                        tool_id=tool.tool_id,
                        can_operate=can_operate,
                        owns_tool=owns_tool
                    )
                    db.session.add(tool_eval)
        
        # Process special skills
        special_skills = request.form.get('special_skills')
        if special_skills:
            for skill_name in special_skills.split(','):
                if skill_name.strip():
                    special_skill = SpecialSkill(
                        evaluation_id=evaluation_id,
                        skill_name=skill_name.strip()
                    )
                    db.session.add(special_skill)
        
        db.session.commit()
        flash('Evaluation successfully updated!', 'success')
        return redirect(url_for('evaluations.view', evaluation_id=evaluation_id))
    
    # Get all categories, skills, and tools for the form
    skill_categories = SkillCategory.query.order_by(SkillCategory.display_order).all()
    tool_categories = ToolCategory.query.order_by(ToolCategory.display_order).all()
    
    # Get existing skill evaluations
    skill_evaluations = {
        se.skill_id: se.rating 
        for se in SkillEvaluation.query.filter_by(evaluation_id=evaluation_id).all()
    }
    
    # Get existing tool evaluations
    tool_evaluations = {
        te.tool_id: {'can_operate': te.can_operate, 'owns_tool': te.owns_tool} 
        for te in ToolEvaluation.query.filter_by(evaluation_id=evaluation_id).all()
    }
    
    # Get existing special skills
    special_skills = [
        ss.skill_name 
        for ss in SpecialSkill.query.filter_by(evaluation_id=evaluation_id).all()
    ]
    
    return render_template(
        'evaluations/edit.html',
        evaluation=evaluation,
        employees=employees,
        skill_categories=skill_categories,
        tool_categories=tool_categories,
        skill_evaluations=skill_evaluations,
        tool_evaluations=tool_evaluations,
        special_skills=','.join(special_skills)
    )

@bp.route('/<int:evaluation_id>/delete', methods=('POST',))
def delete(evaluation_id):
    """
    Delete an evaluation
    """
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    db.session.delete(evaluation)
    db.session.commit()
    flash('Evaluation successfully deleted!', 'success')
    return redirect(url_for('evaluations.index'))

# API endpoints for AJAX operations
@bp.route('/api/list')
def api_list():
    """
    Return JSON list of evaluations
    """
    evaluations = Evaluation.query.order_by(Evaluation.evaluation_date.desc()).all()
    return jsonify([evaluation.to_dict() for evaluation in evaluations])

@bp.route('/api/<int:evaluation_id>')
def api_get(evaluation_id):
    """
    Return JSON data for a specific evaluation
    """
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    return jsonify(evaluation.to_dict())
