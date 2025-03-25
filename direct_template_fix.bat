@echo off
echo ================================================
echo Handyman KPI System - Direct Template Fix
echo ================================================
echo.

set INSTALLED_APP=C:\Users\dtest\AppData\Local\Programs\Handyman KPI System

REM Step 1: Stopping any running instances
echo Step 1: Stopping any running instances...
taskkill /F /IM python.exe 2>nul

REM Step 2: Fix the base.html template by direct replacement
echo.
echo Step 2: Directly replacing base.html template...
set BASE_TEMPLATE=%INSTALLED_APP%\app\templates\base.html
echo Creating backup...
copy /Y "%BASE_TEMPLATE%" "%BASE_TEMPLATE%.bak_direct"

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

echo.
echo Template Fix Completed!
echo.
echo The base.html template has been completely replaced with a version that
echo does not reference the dashboard blueprint. All links now point to the main.index route.
echo.
echo Please try starting the application again.

pause
