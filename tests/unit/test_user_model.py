"""
Unit tests for the User model.
"""
import pytest
from kpi_system.backend.app.models.user import User

def test_user_creation(db_session):
    """Test creating a new user."""
    user = User(
        username="testuser",
        email="test@example.com",
        role="employee"
    )
    user.set_password("securepassword")
    
    db_session.add(user)
    db_session.commit()
    
    # Retrieve the user from the database
    saved_user = db_session.query(User).filter_by(username="testuser").first()
    
    # Verify the user data was saved correctly
    assert saved_user is not None
    assert saved_user.username == "testuser"
    assert saved_user.email == "test@example.com"
    assert saved_user.role == "employee"
    assert saved_user.password != "securepassword"  # Password should be hashed

def test_password_hashing(db_session):
    """Test password hashing and verification."""
    user = User(
        username="passwordtest",
        email="password@example.com",
        role="employee"
    )
    
    # Set the password
    user.set_password("mypassword")
    
    # Verify the password was hashed
    assert user.password != "mypassword"
    
    # Check the password verification method
    assert user.check_password("mypassword") is True
    assert user.check_password("wrongpassword") is False

def test_user_role_validation(db_session):
    """Test that user role must be a valid role."""
    # Create a user with an invalid role
    user = User(
        username="invalidrole",
        email="invalid@example.com",
        role="superuser"  # Not a valid role
    )
    
    user.set_password("password")
    
    # Add the user to the session
    db_session.add(user)
    
    # Committing should raise an exception because of the role validation
    with pytest.raises(ValueError):
        db_session.commit()
        
    # Rollback the session to clean up
    db_session.rollback()

def test_user_unique_username(db_session):
    """Test that username must be unique."""
    # Create the first user
    user1 = User(
        username="uniqueuser",
        email="unique1@example.com",
        role="admin"
    )
    user1.set_password("password")
    db_session.add(user1)
    db_session.commit()
    
    # Create a second user with the same username
    user2 = User(
        username="uniqueuser",  # Same username
        email="unique2@example.com",
        role="employee"
    )
    user2.set_password("password")
    db_session.add(user2)
    
    # Committing should raise an exception due to unique constraint
    with pytest.raises(Exception):
        db_session.commit()
        
    # Rollback the session to clean up
    db_session.rollback()

def test_user_unique_email(db_session):
    """Test that email must be unique."""
    # Create the first user
    user1 = User(
        username="emailuser1",
        email="same@example.com",
        role="admin"
    )
    user1.set_password("password")
    db_session.add(user1)
    db_session.commit()
    
    # Create a second user with the same email
    user2 = User(
        username="emailuser2",
        email="same@example.com",  # Same email
        role="employee"
    )
    user2.set_password("password")
    db_session.add(user2)
    
    # Committing should raise an exception due to unique constraint
    with pytest.raises(Exception):
        db_session.commit()
        
    # Rollback the session to clean up
    db_session.rollback()

def test_password_reset_token(db_session):
    """Test password reset token generation and verification."""
    user = User(
        username="resetuser",
        email="reset@example.com",
        role="manager"
    )
    user.set_password("originalpassword")
    
    db_session.add(user)
    db_session.commit()
    
    # Generate a password reset token
    token = user.get_reset_password_token()
    
    # Verify the token is valid and returns the correct user
    verified_user = User.verify_reset_password_token(token)
    assert verified_user is not None
    assert verified_user.id == user.id
    
    # Verify an invalid token returns None
    invalid_user = User.verify_reset_password_token("invalid-token")
    assert invalid_user is None
