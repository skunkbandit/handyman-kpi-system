@echo off
echo ================================================
echo Handyman KPI System - Template Fix
echo ================================================
echo.

set INSTALLED_APP=C:\Users\dtest\AppData\Local\Programs\Handyman KPI System

REM Step 1: Stopping any running instances
echo Step 1: Stopping any running instances...
taskkill /F /IM python.exe 2>nul

REM Step 2: Fix the base.html template
echo.
echo Step 2: Fixing base.html template...
set BASE_TEMPLATE=%INSTALLED_APP%\app\templates\base.html
echo Creating backup...
copy /Y "%BASE_TEMPLATE%" "%BASE_TEMPLATE%.old"

REM Replace the dashboard.index reference with main.index
powershell -Command "(Get-Content '%BASE_TEMPLATE%') -replace 'url_for''dashboard.index''', 'url_for''main.index''' | Set-Content '%BASE_TEMPLATE%'"

REM Step 3: Fix the login.html template if needed
echo.
echo Step 3: Checking login.html template...
set LOGIN_TEMPLATE=%INSTALLED_APP%\app\templates\auth\login.html
if exist "%LOGIN_TEMPLATE%" (
    echo Creating backup...
    copy /Y "%LOGIN_TEMPLATE%" "%LOGIN_TEMPLATE%.old"
    
    echo Fixing any dashboard references...
    powershell -Command "(Get-Content '%LOGIN_TEMPLATE%') -replace 'url_for''dashboard.index''', 'url_for''main.index''' | Set-Content '%LOGIN_TEMPLATE%'"
)

echo.
echo Template Fix Completed!
echo.
echo References to the dashboard blueprint have been replaced with main.index.
echo The application should now be able to render templates without errors.
echo.
echo Please try starting the application again.

pause
