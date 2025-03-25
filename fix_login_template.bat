@echo off
echo ================================================
echo Handyman KPI System - Login Template Fix
echo ================================================
echo.

set INSTALLED_APP=C:\Users\dtest\AppData\Local\Programs\Handyman KPI System

REM Step 1: Stopping any running instances
echo Step 1: Stopping any running instances...
taskkill /F /IM python.exe 2>nul

REM Step 2: Fix the login.html template by direct replacement
echo.
echo Step 2: Directly replacing login.html template...
set LOGIN_TEMPLATE=%INSTALLED_APP%\app\templates\auth\login.html
echo Creating backup...
if exist "%LOGIN_TEMPLATE%" (
    copy /Y "%LOGIN_TEMPLATE%" "%LOGIN_TEMPLATE%.bak_direct"
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
echo                     ^<a href="{{ url_for('auth.forgot_password') }}" class="text-decoration-none"^>Forgot password?^</a^> >> "%LOGIN_TEMPLATE%"
echo                 ^</div^> >> "%LOGIN_TEMPLATE%"
echo             ^</div^> >> "%LOGIN_TEMPLATE%"
echo         ^</div^> >> "%LOGIN_TEMPLATE%"
echo     ^</div^> >> "%LOGIN_TEMPLATE%"
echo ^</div^> >> "%LOGIN_TEMPLATE%"
echo {% endblock %} >> "%LOGIN_TEMPLATE%"

echo.
echo Login Template Fix Completed!
echo.
echo The login.html template has been completely replaced with a version that
echo extends the base template but doesn't have any internal references to dashboard.
echo.
echo Please try starting the application again.

pause
