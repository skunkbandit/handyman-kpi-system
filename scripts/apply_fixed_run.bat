@echo off
echo =========================================================
echo Handyman KPI System - App Import Fix
echo =========================================================
echo.
echo This script will fix the "Could not locate the create_app function" error
echo by applying an enhanced run.py file to the installation.
echo.
echo Press Ctrl+C to cancel or any key to continue...
pause > nul

echo.
echo Running fix script...
echo.

:: Run the Python script with elevated permissions
powershell -Command "Start-Process python -ArgumentList 'apply_fixed_run.py' -Verb RunAs -Wait"

echo.
echo Fix script completed. Check the output above for results.
echo.
echo If successful, try launching the Handyman KPI System now.
echo.
echo Press any key to exit...
pause > nul
