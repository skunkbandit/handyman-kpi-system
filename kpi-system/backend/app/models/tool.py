"""
Tool Models
"""
from datetime import datetime
from app import db

class ToolCategory(db.Model):
    """
    Tool category model representing main tool categories
    """
    __tablename__ = 'tool_categories'

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tools = db.relationship('Tool', back_populates='category')

    def __repr__(self):
        return f"<ToolCategory {self.name}>"

    def to_dict(self):
        """
        Convert tool category object to dictionary for API responses
        """
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'display_order': self.display_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Tool(db.Model):
    """
    Tool model representing specific tools
    """
    __tablename__ = 'tools'

    tool_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('tool_categories.category_id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = db.relationship('ToolCategory', back_populates='tools')
    evaluations = db.relationship('ToolEvaluation', back_populates='tool')

    def __repr__(self):
        return f"<Tool {self.name}>"

    def to_dict(self):
        """
        Convert tool object to dictionary for API responses
        """
        return {
            'tool_id': self.tool_id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'display_order': self.display_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
