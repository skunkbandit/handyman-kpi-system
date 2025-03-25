"""
Evaluation Models
"""
from datetime import datetime
from app import db

class Evaluation(db.Model):
    """
    Evaluation model representing an evaluation instance for an employee
    """
    __tablename__ = 'evaluations'

    evaluation_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    evaluator_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    evaluation_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = db.relationship('Employee', foreign_keys=[employee_id], back_populates='evaluations')
    evaluator = db.relationship('Employee', foreign_keys=[evaluator_id])
    skill_evaluations = db.relationship('SkillEvaluation', back_populates='evaluation', cascade='all, delete-orphan')
    tool_evaluations = db.relationship('ToolEvaluation', back_populates='evaluation', cascade='all, delete-orphan')
    special_skills = db.relationship('SpecialSkill', back_populates='evaluation', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Evaluation {self.evaluation_id} for {self.employee_id} on {self.evaluation_date}>"

    def to_dict(self):
        """
        Convert evaluation object to dictionary for API responses
        """
        return {
            'evaluation_id': self.evaluation_id,
            'employee_id': self.employee_id,
            'evaluator_id': self.evaluator_id,
            'evaluation_date': self.evaluation_date.strftime('%Y-%m-%d'),
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class SkillEvaluation(db.Model):
    """
    Skill evaluation model representing the rating for a specific skill
    """
    __tablename__ = 'skill_evaluations'

    skill_evaluation_id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.evaluation_id'))
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.skill_id'))
    rating = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evaluation = db.relationship('Evaluation', back_populates='skill_evaluations')
    skill = db.relationship('Skill', back_populates='evaluations')

    def __repr__(self):
        return f"<SkillEvaluation {self.skill_id} ({self.rating}/5)>"

    def to_dict(self):
        """
        Convert skill evaluation object to dictionary for API responses
        """
        return {
            'skill_evaluation_id': self.skill_evaluation_id,
            'evaluation_id': self.evaluation_id,
            'skill_id': self.skill_id,
            'rating': self.rating,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class ToolEvaluation(db.Model):
    """
    Tool evaluation model representing the proficiency and ownership of a specific tool
    """
    __tablename__ = 'tool_evaluations'

    tool_evaluation_id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.evaluation_id'))
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.tool_id'))
    can_operate = db.Column(db.Boolean, default=False)
    owns_tool = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evaluation = db.relationship('Evaluation', back_populates='tool_evaluations')
    tool = db.relationship('Tool', back_populates='evaluations')

    def __repr__(self):
        return f"<ToolEvaluation {self.tool_id} (operate:{self.can_operate}, own:{self.owns_tool})>"

    def to_dict(self):
        """
        Convert tool evaluation object to dictionary for API responses
        """
        return {
            'tool_evaluation_id': self.tool_evaluation_id,
            'evaluation_id': self.evaluation_id,
            'tool_id': self.tool_id,
            'can_operate': self.can_operate,
            'owns_tool': self.owns_tool,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class SpecialSkill(db.Model):
    """
    Special skill model representing additional skills not in the predefined list
    """
    __tablename__ = 'special_skills'

    special_skill_id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.evaluation_id'))
    skill_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evaluation = db.relationship('Evaluation', back_populates='special_skills')

    def __repr__(self):
        return f"<SpecialSkill {self.skill_name}>"

    def to_dict(self):
        """
        Convert special skill object to dictionary for API responses
        """
        return {
            'special_skill_id': self.special_skill_id,
            'evaluation_id': self.evaluation_id,
            'skill_name': self.skill_name,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
