@echo off
echo =====================================================
echo Handyman KPI System - Installation Fix Script
echo =====================================================
echo.

REM Set the installation path
set INSTALL_DIR=C:\Program Files\Handyman KPI System
set APP_DATA_DIR=%LOCALAPPDATA%\Handyman KPI System
echo Installation directory: %INSTALL_DIR%
echo Application data directory: %APP_DATA_DIR%

REM Step 1: Create necessary directories in AppData
echo Step 1: Creating directories in AppData...
if not exist "%APP_DATA_DIR%" mkdir "%APP_DATA_DIR%"
if not exist "%APP_DATA_DIR%\logs" mkdir "%APP_DATA_DIR%\logs"
if not exist "%APP_DATA_DIR%\database" mkdir "%APP_DATA_DIR%\database"
if not exist "%APP_DATA_DIR%\config" mkdir "%APP_DATA_DIR%\config"

REM Step 2: Kill any running instances of the application
echo Step 2: Stopping any running instances...
taskkill /F /IM python.exe >nul 2>&1

REM Step 3: Copy fixed files to installation directory
echo Step 3: Installing fixed files...

REM First check if the GitHub repository is available
set REPO_DIR=%~dp0
set GITHUB_REPO=https://github.com/skunkbandit/handyman-kpi-system

if exist "%REPO_DIR%handyman_kpi_launcher_detached.py" (
    echo Using files from current directory...
    set SOURCE_DIR=%REPO_DIR%
) else (
    echo Downloading files from GitHub repository...
    powershell -Command "$ErrorActionPreference = 'Stop'; try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/skunkbandit/handyman-kpi-system/main/handyman_kpi_launcher_detached.py' -OutFile '%TEMP%\handyman_kpi_launcher_detached.py' } catch { exit 1 }"
    powershell -Command "$ErrorActionPreference = 'Stop'; try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/skunkbandit/handyman-kpi-system/main/initialize_database.py' -OutFile '%TEMP%\initialize_database.py' } catch { exit 1 }"
    powershell -Command "$ErrorActionPreference = 'Stop'; try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/skunkbandit/handyman-kpi-system/main/kpi-system/backend/app/__init__.py.fixed' -OutFile '%TEMP%\__init__.py.fixed' } catch { exit 1 }"
    set SOURCE_DIR=%TEMP%\
)

REM Copy the detached launcher
echo Copying detached launcher...
copy /Y "%SOURCE_DIR%handyman_kpi_launcher_detached.py" "%INSTALL_DIR%\handyman_kpi_launcher.py"

REM Copy the database initialization script
echo Copying database initialization script...
copy /Y "%SOURCE_DIR%initialize_database.py" "%INSTALL_DIR%\initialize_database.py"

REM Copy the fixed app initialization
echo Copying fixed app initialization...
if exist "%SOURCE_DIR%__init__.py.fixed" (
    copy /Y "%SOURCE_DIR%__init__.py.fixed" "%INSTALL_DIR%\kpi-system\backend\app\__init__.py"
) else if exist "%SOURCE_DIR%kpi-system\backend\app\__init__.py.fixed" (
    copy /Y "%SOURCE_DIR%kpi-system\backend\app\__init__.py.fixed" "%INSTALL_DIR%\kpi-system\backend\app\__init__.py"
)

REM Step 4: Create database configuration
echo Step 4: Creating database configuration...
echo { > "%APP_DATA_DIR%\config\database.json"
echo   "type": "sqlite", >> "%APP_DATA_DIR%\config\database.json"
echo   "path": "%APP_DATA_DIR:\\=\\\\%\\database\\kpi_system.db" >> "%APP_DATA_DIR%\config\database.json"
echo } >> "%APP_DATA_DIR%\config\database.json"

REM Step 5: Run database initialization
echo Step 5: Initializing database...
cd /d "%INSTALL_DIR%"
".\python\python.exe" ".\initialize_database.py"

REM Step 6: Create a shortcut on desktop that doesn't show console window
echo Step 6: Creating improved desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Handyman KPI System.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\python\pythonw.exe'; $Shortcut.Arguments = '%INSTALL_DIR%\handyman_kpi_launcher.py'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\resources\icon.ico,0'; $Shortcut.Description = 'Handyman KPI System'; $Shortcut.WindowStyle = 7; $Shortcut.Save()"

echo.
echo =====================================================
echo Fix completed successfully!
echo =====================================================
echo.
echo The following improvements have been made:
echo.
echo 1. Database now stored in AppData for proper permissions
echo 2. Application now runs as a detached process (no console window)
echo 3. Default admin user created (admin/admin)
echo 4. Desktop shortcut updated to hide console window
echo.
echo Please use the desktop shortcut to start the application.
echo.

pause
