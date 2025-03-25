@echo off
echo Building and testing the application with blueprint fixes...

REM Activate virtual environment if exists
IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Stop any running instances
echo Stopping any running instances...
taskkill /F /IM python.exe /T 2>nul

REM Run the application in development mode
cd kpi-system\backend
echo Starting Flask application...
python run.py

echo If the application starts correctly, this batch file has completed successfully.
pause
