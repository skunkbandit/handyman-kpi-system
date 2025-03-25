@echo off
echo Setting up test environment for KPI System Installation...

set BASE_DIR=%~dp0
set REPO_DIR=%BASE_DIR%test-repo

echo Creating test directory at %REPO_DIR%
if not exist "%REPO_DIR%" mkdir "%REPO_DIR%"

echo Cloning repository...
cd /d "%REPO_DIR%"
git clone https://github.com/skunkbandit/handyman-kpi-system.git

echo Creating Python virtual environment...
cd handyman-kpi-system
python -m venv venv
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Setting up database...
python scripts\init_database.py

echo Test environment setup complete!
echo You can now run the application with: python backend\run.py
