"""
Unit tests for the Evaluation model.
"""
import pytest
from datetime import datetime
from kpi_system.backend.app.models.evaluation import Evaluation, EvalSkill, EvalTool
from kpi_system.backend.app.models.employee import Employee
from kpi_system.backend.app.models.skill import Skill, SkillCategory
from kpi_system.backend.app.models.tool import Tool, ToolCategory
from kpi_system.backend.app.models.user import User

def test_evaluation_creation(db_session):
    """Test creating a new evaluation."""
    # Get an employee and evaluator
    employee = db_session.query(Employee).first()
    evaluator = db_session.query(User).filter_by(role='manager').first()
    
    # Create a new evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        evaluation_date=datetime.now().date(),
        notes="Test evaluation notes"
    )
    
    db_session.add(evaluation)
    db_session.commit()
    
    # Retrieve the evaluation from the database
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Verify the evaluation data was saved correctly
    assert saved_evaluation is not None
    assert saved_evaluation.employee_id == employee.id
    assert saved_evaluation.evaluator_id == evaluator.id
    assert saved_evaluation.notes == "Test evaluation notes"
    assert saved_evaluation.evaluation_date == datetime.now().date()

def test_evaluation_with_skills(db_session):
    """Test creating an evaluation with skill ratings."""
    # Get an employee and evaluator
    employee = db_session.query(Employee).first()
    evaluator = db_session.query(User).filter_by(role='manager').first()
    
    # Create a new evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        evaluation_date=datetime.now().date(),
        notes="Evaluation with skills"
    )
    
    db_session.add(evaluation)
    db_session.commit()
    
    # Get some skills to rate
    skills = db_session.query(Skill).limit(3).all()
    
    # Add skill ratings
    for i, skill in enumerate(skills):
        eval_skill = EvalSkill(
            evaluation_id=evaluation.id,
            skill_id=skill.id,
            rating=i+3  # Ratings from 3 to 5
        )
        db_session.add(eval_skill)
    
    db_session.commit()
    
    # Retrieve the evaluation with skills
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Verify the skills were saved correctly
    assert len(saved_evaluation.eval_skills) == 3
    
    # Check that ratings were saved correctly
    ratings = [es.rating for es in saved_evaluation.eval_skills]
    assert sorted(ratings) == [3, 4, 5]

def test_evaluation_with_tools(db_session):
    """Test creating an evaluation with tool proficiencies."""
    # Get an employee and evaluator
    employee = db_session.query(Employee).first()
    evaluator = db_session.query(User).filter_by(role='manager').first()
    
    # Create a new evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        evaluation_date=datetime.now().date(),
        notes="Evaluation with tools"
    )
    
    db_session.add(evaluation)
    db_session.commit()
    
    # Get some tools to evaluate
    tools = db_session.query(Tool).limit(2).all()
    
    # Add tool evaluations
    eval_tool1 = EvalTool(
        evaluation_id=evaluation.id,
        tool_id=tools[0].id,
        can_operate=True,
        owns_tool=True
    )
    
    eval_tool2 = EvalTool(
        evaluation_id=evaluation.id,
        tool_id=tools[1].id,
        can_operate=True,
        owns_tool=False
    )
    
    db_session.add(eval_tool1)
    db_session.add(eval_tool2)
    db_session.commit()
    
    # Retrieve the evaluation with tools
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Verify the tools were saved correctly
    assert len(saved_evaluation.eval_tools) == 2
    
    # Check that tool proficiencies were saved correctly
    tool_proficiencies = [(et.can_operate, et.owns_tool) for et in saved_evaluation.eval_tools]
    assert (True, True) in tool_proficiencies
    assert (True, False) in tool_proficiencies

def test_evaluation_special_skills(db_session):
    """Test adding special skills to an evaluation."""
    # Get an employee and evaluator
    employee = db_session.query(Employee).first()
    evaluator = db_session.query(User).filter_by(role='manager').first()
    
    # Create a new evaluation with special skills
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        evaluation_date=datetime.now().date(),
        notes="Evaluation with special skills",
        special_skills="Custom cabinetry, Historical restoration"
    )
    
    db_session.add(evaluation)
    db_session.commit()
    
    # Retrieve the evaluation
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Verify the special skills were saved
    assert saved_evaluation.special_skills == "Custom cabinetry, Historical restoration"

def test_evaluation_average_rating(db_session):
    """Test calculating the average rating for an evaluation."""
    # Get an employee and evaluator
    employee = db_session.query(Employee).first()
    evaluator = db_session.query(User).filter_by(role='manager').first()
    
    # Create a new evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        evaluation_date=datetime.now().date()
    )
    
    db_session.add(evaluation)
    db_session.commit()
    
    # Get some skills to rate
    skills = db_session.query(Skill).limit(4).all()
    
    # Add skill ratings: 2, 3, 4, 5
    for i, skill in enumerate(skills):
        eval_skill = EvalSkill(
            evaluation_id=evaluation.id,
            skill_id=skill.id,
            rating=i+2  # Ratings from 2 to 5
        )
        db_session.add(eval_skill)
    
    db_session.commit()
    
    # Retrieve the evaluation
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Verify the average rating calculation
    # Average of 2, 3, 4, 5 = 3.5
    assert saved_evaluation.average_rating == 3.5

def test_evaluation_by_category(db_session):
    """Test getting evaluation ratings by skill category."""
    # Get an employee and evaluator
    employee = db_session.query(Employee).first()
    evaluator = db_session.query(User).filter_by(role='manager').first()
    
    # Create a new evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        evaluation_date=datetime.now().date()
    )
    
    db_session.add(evaluation)
    db_session.commit()
    
    # Get skill categories
    categories = db_session.query(SkillCategory).all()
    
    # Add skill ratings for each category
    for category in categories:
        skills = db_session.query(Skill).filter_by(category_id=category.id).all()
        
        # Rate each skill in the category
        for i, skill in enumerate(skills):
            eval_skill = EvalSkill(
                evaluation_id=evaluation.id,
                skill_id=skill.id,
                rating=4  # All skills rated 4
            )
            db_session.add(eval_skill)
    
    db_session.commit()
    
    # Retrieve the evaluation
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Check category averages
    category_ratings = saved_evaluation.ratings_by_category(db_session)
    
    # Verify all categories have an average rating of 4
    for category_name, rating in category_ratings.items():
        assert rating == 4.0