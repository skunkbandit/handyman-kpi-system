"""
Skill Models
"""
from datetime import datetime
from app import db

class SkillCategory(db.Model):
    """
    Skill category model representing main skill areas (plumbing, carpentry, etc.)
    """
    __tablename__ = 'skill_categories'

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = db.relationship('Skill', back_populates='category')

    def __repr__(self):
        return f"<SkillCategory {self.name}>"

    def to_dict(self):
        """
        Convert skill category object to dictionary for API responses
        """
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'display_order': self.display_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Skill(db.Model):
    """
    Skill model representing specific skills within categories
    """
    __tablename__ = 'skills'

    skill_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('skill_categories.category_id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = db.relationship('SkillCategory', back_populates='skills')
    evaluations = db.relationship('SkillEvaluation', back_populates='skill')

    def __repr__(self):
        return f"<Skill {self.name}>"

    def to_dict(self):
        """
        Convert skill object to dictionary for API responses
        """
        return {
            'skill_id': self.skill_id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'display_order': self.display_order,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }