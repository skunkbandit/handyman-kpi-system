"""
Unit tests for the Tool and ToolCategory models.
"""
import pytest
from kpi_system.backend.app.models.tool import Tool, ToolCategory

def test_tool_category_creation(db_session):
    """Test creating a new tool category."""
    category = ToolCategory(name="Hand Tools")
    
    db_session.add(category)
    db_session.commit()
    
    # Retrieve the category from the database
    saved_category = db_session.query(ToolCategory).filter_by(id=category.id).first()
    
    # Verify the category data was saved correctly
    assert saved_category is not None
    assert saved_category.name == "Hand Tools"
    assert len(saved_category.tools) == 0

def test_tool_creation(db_session):
    """Test creating a new tool."""
    # Create a category first
    category = ToolCategory(name="Power Tools")
    db_session.add(category)
    db_session.commit()
    
    # Create a tool in that category
    tool = Tool(
        name="Circular Saw",
        category_id=category.id,
        description="For cutting wood and other materials"
    )
    
    db_session.add(tool)
    db_session.commit()
    
    # Retrieve the tool from the database
    saved_tool = db_session.query(Tool).filter_by(id=tool.id).first()
    
    # Verify the tool data was saved correctly
    assert saved_tool is not None
    assert saved_tool.name == "Circular Saw"
    assert saved_tool.description == "For cutting wood and other materials"
    assert saved_tool.category_id == category.id
    assert saved_tool.category.name == "Power Tools"

def test_tool_relationship(db_session):
    """Test the relationship between tools and tool categories."""
    # Create a category
    category = ToolCategory(name="Measuring Tools")
    db_session.add(category)
    db_session.commit()
    
    # Create multiple tools in that category
    tools = [
        Tool(name="Tape Measure", category=category),
        Tool(name="Laser Level", category=category),
        Tool(name="Speed Square", category=category)
    ]
    
    db_session.add_all(tools)
    db_session.commit()
    
    # Retrieve the category with tools
    saved_category = db_session.query(ToolCategory).filter_by(id=category.id).first()
    
    # Verify the relationship works correctly
    assert len(saved_category.tools) == 3
    tool_names = [tool.name for tool in saved_category.tools]
    assert "Tape Measure" in tool_names
    assert "Laser Level" in tool_names
    assert "Speed Square" in tool_names

def test_unique_tool_name_per_category(db_session):
    """Test that tool names must be unique within a category."""
    # Create a category
    category = ToolCategory(name="Cutting Tools")
    db_session.add(category)
    db_session.commit()
    
    # Create a tool in that category
    tool1 = Tool(name="Utility Knife", category=category)
    db_session.add(tool1)
    db_session.commit()
    
    # Try to create another tool with the same name in the same category
    tool2 = Tool(name="Utility Knife", category=category)
    db_session.add(tool2)
    
    # This should raise an integrity error due to the unique constraint
    with pytest.raises(Exception):
        db_session.commit()
    
    # Rollback the session to clean up
    db_session.rollback()
    
    # Verify that creating the same tool name in a different category works
    category2 = ToolCategory(name="Different Category")
    db_session.add(category2)
    db_session.commit()
    
    tool3 = Tool(name="Utility Knife", category=category2)
    db_session.add(tool3)
    db_session.commit()  # This should succeed
    
    # Verify both tools exist with the same name in different categories
    tool1_from_db = db_session.query(Tool).filter_by(id=tool1.id).first()
    tool3_from_db = db_session.query(Tool).filter_by(id=tool3.id).first()
    
    assert tool1_from_db.name == tool3_from_db.name
    assert tool1_from_db.category_id != tool3_from_db.category_id

def test_cascade_delete(db_session):
    """Test that deleting a category cascades to its tools."""
    # Create a category
    category = ToolCategory(name="Painting Tools")
    db_session.add(category)
    db_session.commit()
    
    # Create tools in that category
    tools = [
        Tool(name="Paint Roller", category=category),
        Tool(name="Paint Brush", category=category)
    ]
    
    db_session.add_all(tools)
    db_session.commit()
    
    # Get the tool IDs
    tool_ids = [tool.id for tool in tools]
    
    # Delete the category
    db_session.delete(category)
    db_session.commit()
    
    # Verify the tools were also deleted
    for tool_id in tool_ids:
        tool = db_session.query(Tool).filter_by(id=tool_id).first()
        assert tool is None
