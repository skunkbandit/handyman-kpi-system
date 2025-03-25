from flask import render_template, redirect, url_for, flash, request
from app import app

@app.route('/')
def index():
    return render_template('index.html', title='Handyman KPI System')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple placeholder authentication
        if username == 'admin' and password == 'admin':
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', title='Login')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

# Create a custom error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
