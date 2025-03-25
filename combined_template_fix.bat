@echo off
echo ================================================
echo Handyman KPI System - Combined Template Fix
echo ================================================
echo.

set INSTALLED_APP=C:\Users\dtest\AppData\Local\Programs\Handyman KPI System

REM Step 1: Stopping any running instances
echo Step 1: Stopping any running instances...
taskkill /F /IM python.exe 2>nul

REM Step 2: Mock reports module
echo.
echo Step 2: Creating mock reports module...

set REPORTS_DIR=%INSTALLED_APP%\app\reports
echo Creating backup of reports directory...
if not exist "%REPORTS_DIR%.bak" (
    xcopy /E /I /Y "%REPORTS_DIR%" "%REPORTS_DIR%.bak"
)

REM Clear existing reports directory
if exist "%REPORTS_DIR%" (
    rd /S /Q "%REPORTS_DIR%"
)
mkdir "%REPORTS_DIR%"

REM Create mock __init__.py
echo """Mock reports module""" > "%REPORTS_DIR%\__init__.py"
echo. >> "%REPORTS_DIR%\__init__.py"

REM Create mock base.py
echo """Mock report generator base class""" > "%REPORTS_DIR%\base.py"
echo. >> "%REPORTS_DIR%\base.py"
echo class ReportGenerator: >> "%REPORTS_DIR%\base.py"
echo     """Mockup of report generator that doesn't import WeasyPrint""" >> "%REPORTS_DIR%\base.py"
echo     def __init__(self, *args, **kwargs): >> "%REPORTS_DIR%\base.py"
echo         self.name = "Mock Report" >> "%REPORTS_DIR%\base.py"
echo         self.supported_formats = ["html", "pdf"] >> "%REPORTS_DIR%\base.py"
echo. >> "%REPORTS_DIR%\base.py"
echo     def generate(self, *args, **kwargs): >> "%REPORTS_DIR%\base.py"
echo         return "This is a mock report. Real reports are unavailable in emergency mode." >> "%REPORTS_DIR%\base.py"
echo. >> "%REPORTS_DIR%\base.py"

REM Create mock generators.py
echo """Mock report generators""" > "%REPORTS_DIR%\generators.py"
echo. >> "%REPORTS_DIR%\generators.py"
echo from .base import ReportGenerator >> "%REPORTS_DIR%\generators.py"
echo. >> "%REPORTS_DIR%\generators.py"
echo def get_report_generator(report_type): >> "%REPORTS_DIR%\generators.py"
echo     """Return a mock report generator""" >> "%REPORTS_DIR%\generators.py"
echo     return ReportGenerator() >> "%REPORTS_DIR%\generators.py"
echo. >> "%REPORTS_DIR%\generators.py"
echo def get_available_report_types(): >> "%REPORTS_DIR%\generators.py"
echo     """Return mock available report types""" >> "%REPORTS_DIR%\generators.py"
echo     return [ >> "%REPORTS_DIR%\generators.py"
echo         {"id": "mock", "name": "Mock Report", "description": "Real reports are disabled in emergency mode"} >> "%REPORTS_DIR%\generators.py"
echo     ] >> "%REPORTS_DIR%\generators.py"
echo. >> "%REPORTS_DIR%\generators.py"

REM Create mock employee_performance.py
echo """Mock employee performance report""" > "%REPORTS_DIR%\employee_performance.py"
echo. >> "%REPORTS_DIR%\employee_performance.py"
echo from .base import ReportGenerator >> "%REPORTS_DIR%\employee_performance.py"
echo. >> "%REPORTS_DIR%\employee_performance.py"
echo class EmployeePerformanceReport(ReportGenerator): >> "%REPORTS_DIR%\employee_performance.py"
echo     """Mock employee performance report""" >> "%REPORTS_DIR%\employee_performance.py"
echo     def __init__(self, *args, **kwargs): >> "%REPORTS_DIR%\employee_performance.py"
echo         super().__init__() >> "%REPORTS_DIR%\employee_performance.py"
echo         self.name = "Employee Performance" >> "%REPORTS_DIR%\employee_performance.py"
echo. >> "%REPORTS_DIR%\employee_performance.py"
echo     def generate(self, *args, **kwargs): >> "%REPORTS_DIR%\employee_performance.py"
echo         return "This is a mock employee performance report. Real reports are unavailable in emergency mode." >> "%REPORTS_DIR%\employee_performance.py"
echo. >> "%REPORTS_DIR%\employee_performance.py"

REM Step 3: Fix the base.html template by direct replacement
echo.
echo Step 3: Directly replacing base.html template...
set BASE_TEMPLATE=%INSTALLED_APP%\app\templates\base.html
echo Creating backup...
copy /Y "%BASE_TEMPLATE%" "%BASE_TEMPLATE%.bak_combined"

echo Creating new base.html template...
echo ^<!DOCTYPE html^> > "%BASE_TEMPLATE%"
echo ^<html lang="en"^> >> "%BASE_TEMPLATE%"
echo ^<head^> >> "%BASE_TEMPLATE%"
echo     ^<meta charset="UTF-8"^> >> "%BASE_TEMPLATE%"
echo     ^<meta name="viewport" content="width=device-width, initial-scale=1.0"^> >> "%BASE_TEMPLATE%"
echo     ^<title^>{% block title %}Handyman KPI System{% endblock %}^</title^> >> "%BASE_TEMPLATE%"
echo     ^<!-- Bootstrap CSS --^> >> "%BASE_TEMPLATE%"
echo     ^<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet"^> >> "%BASE_TEMPLATE%"
echo     ^<!-- Custom CSS --^> >> "%BASE_TEMPLATE%"
echo     ^<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}"^> >> "%BASE_TEMPLATE%"
echo     ^<!-- Font Awesome --^> >> "%BASE_TEMPLATE%"
echo     ^<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"^> >> "%BASE_TEMPLATE%"
echo     {% block styles %}{% endblock %} >> "%BASE_TEMPLATE%"
echo ^</head^> >> "%BASE_TEMPLATE%"
echo ^<body^> >> "%BASE_TEMPLATE%"
echo     ^<header^> >> "%BASE_TEMPLATE%"
echo         ^<nav class="navbar navbar-expand-lg navbar-dark bg-primary"^> >> "%BASE_TEMPLATE%"
echo             ^<div class="container"^> >> "%BASE_TEMPLATE%"
echo                 ^<a class="navbar-brand" href="{{ url_for('main.index') }}"^> >> "%BASE_TEMPLATE%"
echo                     ^<i class="fas fa-tools me-2"^>^</i^> Handyman KPI System >> "%BASE_TEMPLATE%"
echo                 ^</a^> >> "%BASE_TEMPLATE%"
echo                 ^<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation"^> >> "%BASE_TEMPLATE%"
echo                     ^<span class="navbar-toggler-icon"^>^</span^> >> "%BASE_TEMPLATE%"
echo                 ^</button^> >> "%BASE_TEMPLATE%"
echo                 ^<div class="collapse navbar-collapse" id="navbarNav"^> >> "%BASE_TEMPLATE%"
echo                     ^<ul class="navbar-nav me-auto"^> >> "%BASE_TEMPLATE%"
echo                         ^<li class="nav-item"^> >> "%BASE_TEMPLATE%"
echo                             ^<a class="nav-link" href="{{ url_for('main.index') }}"^>Home^</a^> >> "%BASE_TEMPLATE%"
echo                         ^</li^> >> "%BASE_TEMPLATE%"
echo                         {% if current_user.is_authenticated %} >> "%BASE_TEMPLATE%"
echo                         ^<li class="nav-item"^> >> "%BASE_TEMPLATE%"
echo                             ^<a class="nav-link" href="{{ url_for('main.index') }}"^>Dashboard^</a^> >> "%BASE_TEMPLATE%"
echo                         ^</li^> >> "%BASE_TEMPLATE%"
echo                         {% endif %} >> "%BASE_TEMPLATE%"
echo                     ^</ul^> >> "%BASE_TEMPLATE%"
echo                     ^<ul class="navbar-nav ms-auto"^> >> "%BASE_TEMPLATE%"
echo                         {% if current_user.is_authenticated %} >> "%BASE_TEMPLATE%"
echo                         ^<li class="nav-item dropdown"^> >> "%BASE_TEMPLATE%"
echo                             ^<a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false"^> >> "%BASE_TEMPLATE%"
echo                                 ^<i class="fas fa-user me-1"^>^</i^>{{ current_user.username }} >> "%BASE_TEMPLATE%"
echo                             ^</a^> >> "%BASE_TEMPLATE%"
echo                             ^<ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown"^> >> "%BASE_TEMPLATE%"
echo                                 ^<li^>^<a class="dropdown-item" href="{{ url_for('auth.profile') }}"^>Profile^</a^>^</li^> >> "%BASE_TEMPLATE%"
echo                                 ^<li^>^<hr class="dropdown-divider"^>^</li^> >> "%BASE_TEMPLATE%"
echo                                 ^<li^>^<a class="dropdown-item" href="{{ url_for('auth.logout') }}"^>Logout^</a^>^</li^> >> "%BASE_TEMPLATE%"
echo                             ^</ul^> >> "%BASE_TEMPLATE%"
echo                         ^</li^> >> "%BASE_TEMPLATE%"
echo                         {% else %} >> "%BASE_TEMPLATE%"
echo                         ^<li class="nav-item"^> >> "%BASE_TEMPLATE%"
echo                             ^<a class="nav-link" href="{{ url_for('auth.login') }}"^>Login^</a^> >> "%BASE_TEMPLATE%"
echo                         ^</li^> >> "%BASE_TEMPLATE%"
echo                         {% endif %} >> "%BASE_TEMPLATE%"
echo                     ^</ul^> >> "%BASE_TEMPLATE%"
echo                 ^</div^> >> "%BASE_TEMPLATE%"
echo             ^</div^> >> "%BASE_TEMPLATE%"
echo         ^</nav^> >> "%BASE_TEMPLATE%"
echo     ^</header^> >> "%BASE_TEMPLATE%"
echo. >> "%BASE_TEMPLATE%"
echo     ^<main class="container mt-4"^> >> "%BASE_TEMPLATE%"
echo         {% with messages = get_flashed_messages(with_categories=true) %} >> "%BASE_TEMPLATE%"
echo             {% if messages %} >> "%BASE_TEMPLATE%"
echo                 {% for category, message in messages %} >> "%BASE_TEMPLATE%"
echo                     ^<div class="alert alert-{{ category }} alert-dismissible fade show" role="alert"^> >> "%BASE_TEMPLATE%"
echo                         {{ message }} >> "%BASE_TEMPLATE%"
echo                         ^<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"^>^</button^> >> "%BASE_TEMPLATE%"
echo                     ^</div^> >> "%BASE_TEMPLATE%"
echo                 {% endfor %} >> "%BASE_TEMPLATE%"
echo             {% endif %} >> "%BASE_TEMPLATE%"
echo         {% endwith %} >> "%BASE_TEMPLATE%"
echo. >> "%BASE_TEMPLATE%"
echo         {% block content %}{% endblock %} >> "%BASE_TEMPLATE%"
echo     ^</main^> >> "%BASE_TEMPLATE%"
echo. >> "%BASE_TEMPLATE%"
echo     ^<footer class="container mt-5 mb-3"^> >> "%BASE_TEMPLATE%"
echo         ^<hr^> >> "%BASE_TEMPLATE%"
echo         ^<p class="text-center text-muted"^> >> "%BASE_TEMPLATE%"
echo             ^&copy; {{ now().year }} Handyman KPI System | Version {{ app_version }} >> "%BASE_TEMPLATE%"
echo         ^</p^> >> "%BASE_TEMPLATE%"
echo     ^</footer^> >> "%BASE_TEMPLATE%"
echo. >> "%BASE_TEMPLATE%"
echo     ^<!-- Bootstrap Bundle with Popper --^> >> "%BASE_TEMPLATE%"
echo     ^<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"^>^</script^> >> "%BASE_TEMPLATE%"
echo     ^<!-- Custom JavaScript --^> >> "%BASE_TEMPLATE%"
echo     ^<script src="{{ url_for('static', filename='js/script.js') }}"^>^</script^> >> "%BASE_TEMPLATE%"
echo     {% block scripts %}{% endblock %} >> "%BASE_TEMPLATE%"
echo ^</body^> >> "%BASE_TEMPLATE%"
echo ^</html^> >> "%BASE_TEMPLATE%"

REM Step 4: Fix the login.html template by direct replacement
echo.
echo Step 4: Fixing login.html template...
set LOGIN_TEMPLATE=%INSTALLED_APP%\app\templates\auth\login.html
echo Creating backup...
if exist "%LOGIN_TEMPLATE%" (
    copy /Y "%LOGIN_TEMPLATE%" "%LOGIN_TEMPLATE%.bak_combined"
)

echo Creating new login.html template...
mkdir "%INSTALLED_APP%\app\templates\auth" 2>nul

echo {% extends "base.html" %} > "%LOGIN_TEMPLATE%"
echo. >> "%LOGIN_TEMPLATE%"
echo {% block title %}Login - Handyman KPI System{% endblock %} >> "%LOGIN_TEMPLATE%"
echo. >> "%LOGIN_TEMPLATE%"
echo {% block content %} >> "%LOGIN_TEMPLATE%"
echo ^<div class="row"^> >> "%LOGIN_TEMPLATE%"
echo     ^<div class="col-md-6 offset-md-3"^> >> "%LOGIN_TEMPLATE%"
echo         ^<div class="card shadow-sm"^> >> "%LOGIN_TEMPLATE%"
echo             ^<div class="card-body p-4"^> >> "%LOGIN_TEMPLATE%"
echo                 ^<h2 class="text-center mb-4"^>Login^</h2^> >> "%LOGIN_TEMPLATE%"
echo. >> "%LOGIN_TEMPLATE%"
echo                 {% with messages = get_flashed_messages(with_categories=true) %} >> "%LOGIN_TEMPLATE%"
echo                     {% if messages %} >> "%LOGIN_TEMPLATE%"
echo                         {% for category, message in messages %} >> "%LOGIN_TEMPLATE%"
echo                             ^<div class="alert alert-{{ category }} alert-dismissible fade show" role="alert"^> >> "%LOGIN_TEMPLATE%"
echo                                 {{ message }} >> "%LOGIN_TEMPLATE%"
echo                                 ^<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"^>^</button^> >> "%LOGIN_TEMPLATE%"
echo                             ^</div^> >> "%LOGIN_TEMPLATE%"
echo                         {% endfor %} >> "%LOGIN_TEMPLATE%"
echo                     {% endif %} >> "%LOGIN_TEMPLATE%"
echo                 {% endwith %} >> "%LOGIN_TEMPLATE%"
echo. >> "%LOGIN_TEMPLATE%"
echo                 ^<form method="post" action="{{ url_for('auth.login') }}"^> >> "%LOGIN_TEMPLATE%"
echo                     ^<div class="mb-3"^> >> "%LOGIN_TEMPLATE%"
echo                         ^<label for="username" class="form-label"^>Username^</label^> >> "%LOGIN_TEMPLATE%"
echo                         ^<input type="text" class="form-control" id="username" name="username" required^> >> "%LOGIN_TEMPLATE%"
echo                     ^</div^> >> "%LOGIN_TEMPLATE%"
echo                     ^<div class="mb-3"^> >> "%LOGIN_TEMPLATE%"
echo                         ^<label for="password" class="form-label"^>Password^</label^> >> "%LOGIN_TEMPLATE%"
echo                         ^<input type="password" class="form-control" id="password" name="password" required^> >> "%LOGIN_TEMPLATE%"
echo                     ^</div^> >> "%LOGIN_TEMPLATE%"
echo                     ^<div class="mb-3 form-check"^> >> "%LOGIN_TEMPLATE%"
echo                         ^<input type="checkbox" class="form-check-input" id="remember" name="remember"^> >> "%LOGIN_TEMPLATE%"
echo                         ^<label class="form-check-label" for="remember"^>Remember me^</label^> >> "%LOGIN_TEMPLATE%"
echo                     ^</div^> >> "%LOGIN_TEMPLATE%"
echo                     ^<div class="d-grid"^> >> "%LOGIN_TEMPLATE%"
echo                         ^<button type="submit" class="btn btn-primary"^>Login^</button^> >> "%LOGIN_TEMPLATE%"
echo                     ^</div^> >> "%LOGIN_TEMPLATE%"
echo                 ^</form^> >> "%LOGIN_TEMPLATE%"
echo                 ^<div class="text-center mt-3"^> >> "%LOGIN_TEMPLATE%"
echo                     ^<a href="{{ url_for('main.index') }}" class="text-decoration-none"^>Forgot password?^</a^> >> "%LOGIN_TEMPLATE%"
echo                 ^</div^> >> "%LOGIN_TEMPLATE%"
echo             ^</div^> >> "%LOGIN_TEMPLATE%"
echo         ^</div^> >> "%LOGIN_TEMPLATE%"
echo     ^</div^> >> "%LOGIN_TEMPLATE%"
echo ^</div^> >> "%LOGIN_TEMPLATE%"
echo {% endblock %} >> "%LOGIN_TEMPLATE%"

REM Step 5: Fix routes/__init__.py to avoid importing reports
echo.
echo Step 5: Fixing routes/__init__.py...
set ROUTES_INIT=%INSTALLED_APP%\app\routes\__init__.py
echo Creating backup...
copy /Y "%ROUTES_INIT%" "%ROUTES_INIT%.bak_combined"

echo """Routes package for the KPI system""" > "%ROUTES_INIT%"
echo. >> "%ROUTES_INIT%"
echo # Individual route imports will be done directly in app/__init__.py >> "%ROUTES_INIT%"
echo # This prevents circular imports and allows selective importing >> "%ROUTES_INIT%"
echo. >> "%ROUTES_INIT%"
echo __all__ = [] >> "%ROUTES_INIT%"

REM Step 6: Fix the auth blueprint in auth.py
echo.
echo Step 6: Fixing auth blueprint in auth.py...
set AUTH_FILE=%INSTALLED_APP%\app\routes\auth.py
echo Creating backup...
copy /Y "%AUTH_FILE%" "%AUTH_FILE%.bak_combined"
echo Replacing auth_bp with bp...
powershell -Command "(Get-Content '%AUTH_FILE%') -replace 'auth_bp', 'bp' | Set-Content '%AUTH_FILE%'"

echo.
echo Combined Fix Completed!
echo.
echo This comprehensive fix combines multiple approaches:
echo 1. Created mock report modules that don't import WeasyPrint
echo 2. Replaced the base.html template to remove dashboard references
echo 3. Replaced the login.html template with a clean version
echo 4. Fixed the routes/__init__.py to prevent problematic imports
echo 5. Fixed the auth blueprint naming in auth.py
echo.
echo Please try starting the application again. If you still encounter issues,
echo please check the error messages for additional clues.

pause
