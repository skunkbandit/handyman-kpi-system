"""
User Model
---------
Model for storing system users with authentication and Flask-Login integration.
"""

from datetime import datetime
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model, UserMixin):
    """User model for system authentication and authorization with Flask-Login integration."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'manager', 'employee'
    last_login = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    force_password_change = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationship with Employee
    employee = db.relationship('Employee', backref=db.backref('user', lazy=True))

    def __init__(self, username, password, role, employee_id=None, active=True):
        self.username = username
        self.password = password  # This will call the setter method
        self.role = role
        self.employee_id = employee_id
        self.active = active

    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Set password to a hashed value."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check if the provided password matches the hashed password."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'

    def is_manager(self):
        """Check if user has manager role."""
        return self.role == 'manager' or self.role == 'admin'
        
    def is_employee(self):
        """Check if user has employee role."""
        return self.role == 'employee'
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    # Flask-Login methods
    def get_id(self):
        """Return the user ID as a unicode string."""
        return str(self.id)
    
    def is_active(self):
        """Return True if this is an active user."""
        return self.active
    
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True
    
    def is_anonymous(self):
        """Return False as anonymous users aren't supported."""
        return False
    
    # Password reset methods
    def generate_reset_token(self, expiration=3600):
        """Generate a reset token for password recovery."""
        self.reset_token = str(uuid.uuid4())
        self.reset_token_expiry = datetime.utcnow() + datetime.timedelta(seconds=expiration)
        db.session.commit()
        return self.reset_token
    
    @staticmethod
    def verify_reset_token(token):
        """Verify the reset token and return user if valid."""
        user = User.query.filter_by(reset_token=token).first()
        if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
            return None
        return user
    
    def clear_reset_token(self):
        """Clear the reset token after use."""
        self.reset_token = None
        self.reset_token_expiry = None
        db.session.commit()

    def __repr__(self):
        return f"<User {self.username}>"
