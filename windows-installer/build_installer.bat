@echo off
setlocal enabledelayedexpansion

echo ================================================
echo Building Handyman KPI System Windows Installer
echo ================================================
echo.

REM Set paths
set "SCRIPT_DIR=%~dp0"
set "TEMP_DIR=%SCRIPT_DIR%temp"
set "OUTPUT_DIR=%SCRIPT_DIR%output"
set "PYTHON_DIR=%SCRIPT_DIR%python"
set "RESOURCE_DIR=%SCRIPT_DIR%resources"

REM Create necessary directories
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
if not exist "%RESOURCE_DIR%" mkdir "%RESOURCE_DIR%"

REM Download embedded Python (adjust version as needed)
echo Downloading embedded Python...
curl -L https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip -o "%TEMP_DIR%\python.zip"

REM Extract Python
echo Extracting Python...
powershell -command "Expand-Archive -Force '%TEMP_DIR%\python.zip' -DestinationPath '%PYTHON_DIR%'"

REM Download get-pip.py
echo Downloading pip...
curl -L https://bootstrap.pypa.io/get-pip.py -o "%TEMP_DIR%\get-pip.py"

REM Modify python310._pth to enable site-packages
echo Enabling site-packages...
powershell -command "(Get-Content '%PYTHON_DIR%\python310._pth') -replace '#import site', 'import site' | Set-Content '%PYTHON_DIR%\python310._pth'"

REM Install pip
echo Installing pip...
"%PYTHON_DIR%\python.exe" "%TEMP_DIR%\get-pip.py" --no-warn-script-location

REM Install requirements
echo Installing requirements...
"%PYTHON_DIR%\Scripts\pip.exe" install Flask==2.2.3 Werkzeug==2.2.3 Jinja2==3.1.2 waitress==2.1.2

REM Clone repository if not already present
if not exist "%TEMP_DIR%\handyman-kpi-system" (
    echo Cloning repository...
    git clone https://github.com/skunkbandit/handyman-kpi-system.git "%TEMP_DIR%\handyman-kpi-system"
) else (
    echo Updating repository...
    cd /d "%TEMP_DIR%\handyman-kpi-system"
    git pull
)

REM Copy necessary files from repo
echo Copying necessary files from repository...
xcopy /E /I /Y "%TEMP_DIR%\handyman-kpi-system\database" "%SCRIPT_DIR%\src\database"
xcopy /E /I /Y "%TEMP_DIR%\handyman-kpi-system\backend\app" "%SCRIPT_DIR%\src\app"
REM We'll use the pre-created logo.png file in the resources directory

REM Using pre-created icon.ico file in the resources directory
echo Using pre-created icon from resources directory...

REM Run Inno Setup to build the installer
echo Building installer with Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%SCRIPT_DIR%\installer.iss"

echo.
echo ================================================
echo Build completed!
echo Installer can be found in: %OUTPUT_DIR%
echo ================================================

REM Clean up
echo Cleaning up...
rmdir /S /Q "%TEMP_DIR%"

pause
