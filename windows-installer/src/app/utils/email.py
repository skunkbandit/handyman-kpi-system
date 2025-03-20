"""
Email utility functions
----------------------
Functions for sending emails from the application.
"""

from flask import current_app

def send_password_reset_email(user, reset_url):
    """
    Send a password reset email to a user.
    
    This is a placeholder function that would typically send an actual email.
    For the development/testing environment, it simply logs the email details.
    
    Args:
        user: The user to send the email to
        reset_url: The URL for resetting the password
    """
    # In a production environment, this would send an actual email
    # For now, just log the details
    current_app.logger.info(f"Password reset email would be sent to {user.username}")
    current_app.logger.info(f"Reset URL: {reset_url}")
    
    # Placeholder for future email sending functionality
    # Example with Flask-Mail:
    # msg = Message(
    #     subject="Password Reset",
    #     recipients=[user.email],
    #     body=f"Click the following link to reset your password: {reset_url}",
    #     html=render_template('email/reset_password.html', user=user, reset_url=reset_url)
    # )
    # mail.send(msg)
    
    return True  # Indicate success