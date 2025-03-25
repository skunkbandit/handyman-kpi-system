"""
Unit tests for the Skill and SkillCategory models.
"""
import pytest
from kpi_system.backend.app.models.skill import Skill, SkillCategory

def test_skill_category_creation(db_session):
    """Test creating a new skill category."""
    category = SkillCategory(name="Test Category")
    
    db_session.add(category)
    db_session.commit()
    
    # Retrieve the category from the database
    saved_category = db_session.query(SkillCategory).filter_by(id=category.id).first()
    
    # Verify the category data was saved correctly
    assert saved_category is not None
    assert saved_category.name == "Test Category"
    assert len(saved_category.skills) == 0

def test_skill_creation(db_session):
    """Test creating a new skill."""
    # Create a category first
    category = SkillCategory(name="Plumbing")
    db_session.add(category)
    db_session.commit()
    
    # Create a skill in that category
    skill = Skill(
        name="Pipe Fitting",
        category_id=category.id,
        description="Installing and connecting pipes correctly"
    )
    
    db_session.add(skill)
    db_session.commit()
    
    # Retrieve the skill from the database
    saved_skill = db_session.query(Skill).filter_by(id=skill.id).first()
    
    # Verify the skill data was saved correctly
    assert saved_skill is not None
    assert saved_skill.name == "Pipe Fitting"
    assert saved_skill.description == "Installing and connecting pipes correctly"
    assert saved_skill.category_id == category.id
    assert saved_skill.category.name == "Plumbing"

def test_skill_relationship(db_session):
    """Test the relationship between skills and skill categories."""
    # Create a category
    category = SkillCategory(name="Carpentry")
    db_session.add(category)
    db_session.commit()
    
    # Create multiple skills in that category
    skills = [
        Skill(name="Framing", category=category),
        Skill(name="Cabinet Installation", category=category),
        Skill(name="Trim Work", category=category)
    ]
    
    db_session.add_all(skills)
    db_session.commit()
    
    # Retrieve the category with skills
    saved_category = db_session.query(SkillCategory).filter_by(id=category.id).first()
    
    # Verify the relationship works correctly
    assert len(saved_category.skills) == 3
    skill_names = [skill.name for skill in saved_category.skills]
    assert "Framing" in skill_names
    assert "Cabinet Installation" in skill_names
    assert "Trim Work" in skill_names

def test_unique_skill_name_per_category(db_session):
    """Test that skill names must be unique within a category."""
    # Create a category
    category = SkillCategory(name="Electrical")
    db_session.add(category)
    db_session.commit()
    
    # Create a skill in that category
    skill1 = Skill(name="Wiring", category=category)
    db_session.add(skill1)
    db_session.commit()
    
    # Try to create another skill with the same name in the same category
    skill2 = Skill(name="Wiring", category=category)
    db_session.add(skill2)
    
    # This should raise an integrity error due to the unique constraint
    with pytest.raises(Exception):
        db_session.commit()
    
    # Rollback the session to clean up
    db_session.rollback()
    
    # Verify that creating the same skill name in a different category works
    category2 = SkillCategory(name="Different Category")
    db_session.add(category2)
    db_session.commit()
    
    skill3 = Skill(name="Wiring", category=category2)
    db_session.add(skill3)
    db_session.commit()  # This should succeed
    
    # Verify both skills exist with the same name in different categories
    skill1_from_db = db_session.query(Skill).filter_by(id=skill1.id).first()
    skill3_from_db = db_session.query(Skill).filter_by(id=skill3.id).first()
    
    assert skill1_from_db.name == skill3_from_db.name
    assert skill1_from_db.category_id != skill3_from_db.category_id

def test_cascade_delete(db_session):
    """Test that deleting a category cascades to its skills."""
    # Create a category
    category = SkillCategory(name="Flooring")
    db_session.add(category)
    db_session.commit()
    
    # Create skills in that category
    skills = [
        Skill(name="Tile Installation", category=category),
        Skill(name="Hardwood Installation", category=category)
    ]
    
    db_session.add_all(skills)
    db_session.commit()
    
    # Get the skill IDs
    skill_ids = [skill.id for skill in skills]
    
    # Delete the category
    db_session.delete(category)
    db_session.commit()
    
    # Verify the skills were also deleted
    for skill_id in skill_ids:
        skill = db_session.query(Skill).filter_by(id=skill_id).first()
        assert skill is None
