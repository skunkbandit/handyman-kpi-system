"""
Unit tests for the Evaluation models.
"""
import pytest
from datetime import datetime, timedelta
from kpi_system.backend.app.models.evaluation import Evaluation, EvalSkill, EvalTool, SpecialSkill
from kpi_system.backend.app.models.employee import Employee
from kpi_system.backend.app.models.skill import Skill, SkillCategory
from kpi_system.backend.app.models.tool import Tool, ToolCategory
from kpi_system.backend.app.models.user import User

def test_evaluation_creation(db_session):
    """Test creating a new evaluation."""
    # Create a test employee
    employee = Employee(
        first_name="Eval",
        last_name="Test",
        tier="Handyman",
        hire_date=datetime.now().date(),
        active=True
    )
    db_session.add(employee)
    
    # Create a test evaluator
    evaluator = User(
        username="evaluator",
        email="evaluator@example.com",
        role="manager"
    )
    evaluator.set_password("evalpass")
    db_session.add(evaluator)
    db_session.commit()
    
    # Create an evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        date=datetime.now().date(),
        notes="Initial evaluation"
    )
    
    db_session.add(evaluation)
    db_session.commit()
    
    # Retrieve the evaluation from the database
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Verify the evaluation data was saved correctly
    assert saved_evaluation is not None
    assert saved_evaluation.employee_id == employee.id
    assert saved_evaluation.evaluator_id == evaluator.id
    assert saved_evaluation.notes == "Initial evaluation"
    assert saved_evaluation.date == datetime.now().date()
    assert len(saved_evaluation.skill_ratings) == 0
    assert len(saved_evaluation.tool_ratings) == 0
    assert len(saved_evaluation.special_skills) == 0

def test_skill_rating_creation(db_session):
    """Test adding skill ratings to an evaluation."""
    # Create a test employee
    employee = Employee(
        first_name="Skill",
        last_name="Test",
        tier="Craftsman",
        hire_date=datetime.now().date(),
        active=True
    )
    db_session.add(employee)
    
    # Create a test evaluator
    evaluator = User(
        username="skill_evaluator",
        email="skill_evaluator@example.com",
        role="manager"
    )
    evaluator.set_password("skillpass")
    db_session.add(evaluator)
    
    # Create a skill category and skills
    category = SkillCategory(name="Test Skills")
    db_session.add(category)
    db_session.commit()
    
    skill1 = Skill(name="Test Skill 1", category=category)
    skill2 = Skill(name="Test Skill 2", category=category)
    db_session.add_all([skill1, skill2])
    db_session.commit()
    
    # Create an evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        date=datetime.now().date(),
        notes="Skill rating test"
    )
    db_session.add(evaluation)
    db_session.commit()
    
    # Add skill ratings
    skill_rating1 = EvalSkill(
        evaluation_id=evaluation.id,
        skill_id=skill1.id,
        rating=4,
        notes="Good skill"
    )
    
    skill_rating2 = EvalSkill(
        evaluation_id=evaluation.id,
        skill_id=skill2.id,
        rating=2,
        notes="Needs improvement"
    )
    
    db_session.add_all([skill_rating1, skill_rating2])
    db_session.commit()
    
    # Retrieve the evaluation with skill ratings
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Verify the skill ratings were saved correctly
    assert len(saved_evaluation.skill_ratings) == 2
    
    # Ratings are sorted by their ID, so the order might not match the creation order
    # Let's check by skill ID instead
    ratings_by_skill_id = {rating.skill_id: rating for rating in saved_evaluation.skill_ratings}
    
    assert ratings_by_skill_id[skill1.id].rating == 4
    assert ratings_by_skill_id[skill1.id].notes == "Good skill"
    assert ratings_by_skill_id[skill2.id].rating == 2
    assert ratings_by_skill_id[skill2.id].notes == "Needs improvement"

def test_tool_rating_creation(db_session):
    """Test adding tool ratings to an evaluation."""
    # Create a test employee
    employee = Employee(
        first_name="Tool",
        last_name="Test",
        tier="Master Craftsman",
        hire_date=datetime.now().date(),
        active=True
    )
    db_session.add(employee)
    
    # Create a test evaluator
    evaluator = User(
        username="tool_evaluator",
        email="tool_evaluator@example.com",
        role="manager"
    )
    evaluator.set_password("toolpass")
    db_session.add(evaluator)
    
    # Create a tool category and tools
    category = ToolCategory(name="Test Tools")
    db_session.add(category)
    db_session.commit()
    
    tool1 = Tool(name="Test Tool 1", category=category)
    tool2 = Tool(name="Test Tool 2", category=category)
    db_session.add_all([tool1, tool2])
    db_session.commit()
    
    # Create an evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        date=datetime.now().date(),
        notes="Tool rating test"
    )
    db_session.add(evaluation)
    db_session.commit()
    
    # Add tool ratings
    tool_rating1 = EvalTool(
        evaluation_id=evaluation.id,
        tool_id=tool1.id,
        can_operate=True,
        has_tool=True,
        notes="Owns and knows how to use"
    )
    
    tool_rating2 = EvalTool(
        evaluation_id=evaluation.id,
        tool_id=tool2.id,
        can_operate=True,
        has_tool=False,
        notes="Can use but doesn't own"
    )
    
    db_session.add_all([tool_rating1, tool_rating2])
    db_session.commit()
    
    # Retrieve the evaluation with tool ratings
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Verify the tool ratings were saved correctly
    assert len(saved_evaluation.tool_ratings) == 2
    
    # Ratings are sorted by their ID, so the order might not match the creation order
    # Let's check by tool ID instead
    ratings_by_tool_id = {rating.tool_id: rating for rating in saved_evaluation.tool_ratings}
    
    assert ratings_by_tool_id[tool1.id].can_operate is True
    assert ratings_by_tool_id[tool1.id].has_tool is True
    assert ratings_by_tool_id[tool1.id].notes == "Owns and knows how to use"
    assert ratings_by_tool_id[tool2.id].can_operate is True
    assert ratings_by_tool_id[tool2.id].has_tool is False
    assert ratings_by_tool_id[tool2.id].notes == "Can use but doesn't own"

def test_special_skill_creation(db_session):
    """Test adding special skills to an evaluation."""
    # Create a test employee
    employee = Employee(
        first_name="Special",
        last_name="Test",
        tier="Lead Craftsman",
        hire_date=datetime.now().date(),
        active=True
    )
    db_session.add(employee)
    
    # Create a test evaluator
    evaluator = User(
        username="special_evaluator",
        email="special_evaluator@example.com",
        role="manager"
    )
    evaluator.set_password("specialpass")
    db_session.add(evaluator)
    db_session.commit()
    
    # Create an evaluation
    evaluation = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        date=datetime.now().date(),
        notes="Special skill test"
    )
    db_session.add(evaluation)
    db_session.commit()
    
    # Add special skills
    special_skill1 = SpecialSkill(
        evaluation_id=evaluation.id,
        name="Custom Woodworking",
        description="Able to create custom woodworking designs from scratch"
    )
    
    special_skill2 = SpecialSkill(
        evaluation_id=evaluation.id,
        name="Historic Restoration",
        description="Specializes in historic building restoration techniques"
    )
    
    db_session.add_all([special_skill1, special_skill2])
    db_session.commit()
    
    # Retrieve the evaluation with special skills
    saved_evaluation = db_session.query(Evaluation).filter_by(id=evaluation.id).first()
    
    # Verify the special skills were saved correctly
    assert len(saved_evaluation.special_skills) == 2
    
    # Special skills are sorted by their ID, so we'll check by name
    skill_names = [skill.name for skill in saved_evaluation.special_skills]
    assert "Custom Woodworking" in skill_names
    assert "Historic Restoration" in skill_names
    
    # Find each skill by name and check details
    for skill in saved_evaluation.special_skills:
        if skill.name == "Custom Woodworking":
            assert skill.description == "Able to create custom woodworking designs from scratch"
        elif skill.name == "Historic Restoration":
            assert skill.description == "Specializes in historic building restoration techniques"

def test_evaluation_history(db_session):
    """Test retrieving evaluation history for an employee."""
    # Create a test employee
    employee = Employee(
        first_name="History",
        last_name="Test",
        tier="Apprentice",
        hire_date=(datetime.now() - timedelta(days=365)).date(),
        active=True
    )
    db_session.add(employee)
    
    # Create a test evaluator
    evaluator = User(
        username="history_evaluator",
        email="history_evaluator@example.com",
        role="manager"
    )
    evaluator.set_password("historypass")
    db_session.add(evaluator)
    db_session.commit()
    
    # Create evaluations at different dates
    evaluation1 = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        date=(datetime.now() - timedelta(days=180)).date(),
        notes="First evaluation"
    )
    
    evaluation2 = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        date=(datetime.now() - timedelta(days=90)).date(),
        notes="Second evaluation"
    )
    
    evaluation3 = Evaluation(
        employee_id=employee.id,
        evaluator_id=evaluator.id,
        date=datetime.now().date(),
        notes="Current evaluation"
    )
    
    db_session.add_all([evaluation1, evaluation2, evaluation3])
    db_session.commit()
    
    # Retrieve all evaluations for the employee
    employee_evaluations = db_session.query(Evaluation).filter_by(employee_id=employee.id).order_by(Evaluation.date).all()
    
    # Verify the evaluations were retrieved correctly
    assert len(employee_evaluations) == 3
    assert employee_evaluations[0].notes == "First evaluation"
    assert employee_evaluations[1].notes == "Second evaluation"
    assert employee_evaluations[2].notes == "Current evaluation"
    
    # Check timestamps are in order
    assert employee_evaluations[0].date < employee_evaluations[1].date
    assert employee_evaluations[1].date < employee_evaluations[2].date
