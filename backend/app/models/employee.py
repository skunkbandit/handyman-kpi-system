"""
Employee Model
"""
from datetime import datetime
from app import db

class Employee(db.Model):
    """
    Employee model representing the handyman business employees
    """
    __tablename__ = 'employees'

    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    tier = db.Column(db.String(20), nullable=False)
    hire_date = db.Column(db.Date)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evaluations = db.relationship('Evaluation', back_populates='employee')

    def __repr__(self):
        return f"<Employee {self.name} ({self.tier})>"

    def to_dict(self):
        """
        Convert employee object to dictionary for API responses
        """
        return {
            'employee_id': self.employee_id,
            'name': self.name,
            'phone': self.phone,
            'tier': self.tier,
            'hire_date': self.hire_date.strftime('%Y-%m-%d') if self.hire_date else None,
            'active': self.active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }