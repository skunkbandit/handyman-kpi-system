# CSRF Token Fix Guide

## Issue Description

When attempting to add, edit, or delete employees in the Handyman KPI System, users encountered a "400 Bad Request: The CSRF token is missing" error. This happened because the forms were missing CSRF (Cross-Site Request Forgery) protection token fields.

## Technical Background

CSRF is a type of security vulnerability that allows attackers to trick users into performing unwanted actions on a website where they're authenticated. Flask applications use the Flask-WTF extension to protect against these attacks by requiring a unique token with each form submission.

In our application, this protection is configured in `backend/app/__init__.py`:

```python
from flask_wtf.csrf import CSRFProtect

# Create extension instances
csrf = CSRFProtect()

def create_app(test_config=None):
    # ...
    app.config.from_mapping(
        # ...
        WTF_CSRF_ENABLED=True,
        # ...
    )
    # ...
    csrf.init_app(app)
```

## The Fix

We've updated all employee-related forms to include the necessary CSRF token, by adding this line to each form:

```html
<!-- CSRF Token -->
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

### Files Modified:

1. `backend/app/templates/employees/create.html` - Form for adding new employees
2. `backend/app/templates/employees/edit.html` - Form for editing existing employees
3. `backend/app/templates/employees/index.html` - Delete confirmation modal form

## How to Apply the Fix

### Option 1: Pull the Latest Updates from GitHub

If you have a Git installation, simply pull the latest changes:

```bash
git pull origin main
```

### Option 2: Use the Fix Script

We've included a Python script that automatically adds the CSRF token to all required forms:

1. Navigate to the `scripts` directory in your project
2. Run the script:
   ```
   python fix_csrf_token.py
   ```

### Option 3: Manual Fix

If you prefer to make the changes manually:

1. Open each of the three templates mentioned above
2. For each form with `method="post"`, add the CSRF token input field after the opening `<form>` tag:
   ```html
   <form method="post" ...>
       <!-- CSRF Token -->
       <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
       <!-- Rest of the form -->
   </form>
   ```

## Verifying the Fix

After applying the fix, you should be able to:

1. Add new employees without encountering CSRF errors
2. Edit existing employees without CSRF errors
3. Delete employees without CSRF errors

## Preventing Similar Issues

When creating new forms in the future, remember to include the CSRF token for all forms that use POST, PUT, PATCH, or DELETE methods. Consider creating a form macro or including the token in a base template to ensure consistent application across the system.