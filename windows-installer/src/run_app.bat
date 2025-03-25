@echo off
cd /d "%~dp0"
echo Starting Handyman KPI System...

"python\python.exe" launcher.py

if %errorlevel% neq 0 (
    echo Error starting application!
    echo Please make sure Python is installed correctly.
    pause
)
