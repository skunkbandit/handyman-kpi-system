"""
Main routes for the KPI system
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """
    Index page - redirects to dashboard for authenticated users
    or to login page for anonymous users
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    else:
        return redirect(url_for('auth.login'))

@bp.route('/about')
@login_required
def about():
    """
    About page with system information
    """
    return render_template('about.html')
