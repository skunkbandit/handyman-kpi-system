from flask import Blueprint

def init_app(app):
    """Register all blueprint routes with app"""
    from .auth import auth
    from .dashboard import dashboard
    from .employees import employees
    from .evaluations import evaluations
    from .reports import reports
    from .admin import admin
    
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(employees)
    app.register_blueprint(evaluations)
    app.register_blueprint(reports)
    app.register_blueprint(admin)