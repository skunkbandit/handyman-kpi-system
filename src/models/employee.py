"""
Employee Model
-------------
Represents employees in the handyman business.
"""

from datetime import datetime
from app import db

class Employee(db.Model):
    """Employee model for storing employee details."""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20))
    tier_level = db.Column(db.Integer, nullable=False)  # 1-5 corresponding to the 5 tiers
    hire_date = db.Column(db.Date)
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evaluations = db.relationship('Evaluation', backref='employee', lazy=True)
    special_skills = db.relationship('SpecialSkill', backref='employee', lazy=True)
    user = db.relationship('User', backref='employee', uselist=False, lazy=True)

    def __init__(self, first_name, last_name, tier_level, phone_number=None, 
                 hire_date=None, active=True, notes=None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.tier_level = tier_level
        self.hire_date = hire_date
        self.active = active
        self.notes = notes

    @property
    def full_name(self):
        """Return the employee's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def tier_name(self):
        """Return the name of the employee's current tier."""
        tiers = {
            1: "Apprentice",
            2: "Handyman",
            3: "Craftsman",
            4: "Master Craftsman",
            5: "Lead Craftsman"
        }
        return tiers.get(self.tier_level, "Unknown")

    def get_latest_evaluation(self):
        """Return the employee's most recent evaluation."""
        return Evaluation.query.filter_by(employee_id=self.id).order_by(Evaluation.evaluation_date.desc()).first()

    def get_skill_average(self, category_id=None):
        """Calculate the employee's average skill rating, optionally filtered by category."""
        latest_eval = self.get_latest_evaluation()
        if not latest_eval:
            return 0

        query = EvalSkill.query.filter_by(evaluation_id=latest_eval.id)
        
        if category_id:
            # Join with skills table to filter by category
            query = query.join(Skill, EvalSkill.skill_id == Skill.id).filter(Skill.category_id == category_id)
        
        skills = query.all()
        if not skills:
            return 0
            
        return sum(s.rating for s in skills) / len(skills)

    def __repr__(self):
        return f"<Employee {self.full_name}>"