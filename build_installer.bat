@echo off
echo Building Handyman KPI System installer...

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

:: Install required packages
pip install pillow

:: Run the build script
python scripts\build_installer.py

:: Check if the build was successful
if %errorlevel% neq 0 (
    echo Error building installer!
    pause
    exit /b %errorlevel%
)

echo Installer built successfully!
pause
