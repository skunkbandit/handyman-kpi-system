"""
Email Utility Functions
---------------------
Utility functions for sending emails (placeholder implementation).
"""

import logging
from flask import current_app

logger = logging.getLogger(__name__)

def send_email(recipient, subject, body):
    """
    Send an email (placeholder function).
    
    In a production environment, this would connect to an email service.
    For now, it just logs the email content.
    
    Args:
        recipient (str): Email recipient address
        subject (str): Email subject line
        body (str): Email body content (HTML)
    """
    # Log the email for development
    logger.info(f"Email would be sent to: {recipient}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Body: {body}")
    
    # In a real application, you would use a service like:
    # - Flask-Mail
    # - SendGrid
    # - SMTP library
    # - AWS SES
    # to actually send the email
    
    # Example code for Flask-Mail (commented out):
    # from flask_mail import Message
    # from app import mail
    # msg = Message(subject, recipients=[recipient])
    # msg.html = body
    # mail.send(msg)
    
    # For now, this is a placeholder that just returns True
    return True

def send_password_reset_email(user, reset_url):
    """
    Send a password reset email with a reset link.
    
    Args:
        user (User): User model instance
        reset_url (str): URL for password reset
    """
    subject = "Password Reset Request"
    body = f"""
    <h1>Password Reset</h1>
    <p>Hello {user.username},</p>
    <p>You (or someone else) has requested a password reset for your account. 
    If you did not make this request, you can safely ignore this email.</p>
    
    <p>To reset your password, please click the link below:</p>
    <p><a href="{reset_url}">Reset Your Password</a></p>
    
    <p>This link will expire in 1 hour.</p>
    
    <p>Thank you,<br>
    The Handyman KPI System Team</p>
    """
    
    # For development, let's just return the success value
    # In production, we would actually send the email
    return send_email(user.username, subject, body)

def send_account_creation_email(user, temp_password):
    """
    Send an email to a new user with their temporary password.
    
    Args:
        user (User): User model instance
        temp_password (str): Temporary password for first login
    """
    subject = "Your New Account on Handyman KPI System"
    body = f"""
    <h1>Welcome to the Handyman KPI System</h1>
    <p>Hello {user.username},</p>
    
    <p>An account has been created for you in the Handyman KPI System.</p>
    
    <p>Your login details are:</p>
    <ul>
        <li><strong>Username:</strong> {user.username}</li>
        <li><strong>Temporary Password:</strong> {temp_password}</li>
    </ul>
    
    <p>Please login using the temporary password. You will be prompted to change 
    your password upon first login.</p>
    
    <p>Thank you,<br>
    The Handyman KPI System Team</p>
    """
    
    return send_email(user.username, subject, body)