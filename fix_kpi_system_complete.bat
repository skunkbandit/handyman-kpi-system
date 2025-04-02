@echo off
echo ======================================================
echo Handyman KPI System - Comprehensive Fix Script
echo ======================================================
echo This script will:
echo 1. Fix database schema issues
echo 2. Create a properly detached launcher
echo 3. Update any necessary files
echo ======================================================

REM Check if running with admin privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %errorlevel% neq 0 (
    echo Administrator privileges required
    echo Please run this script as Administrator
    pause
    exit /b 1
)

echo.
echo Step 1: Fixing database schema...
python fix_database_all.py
if %errorlevel% neq 0 (
    echo Failed to fix database schema
    pause
    exit /b 1
)
echo Database schema fix completed successfully

echo.
echo Step 2: Creating desktop shortcut...
set INSTALL_DIR="%ProgramFiles%\Handyman KPI System"
if not exist %INSTALL_DIR% (
    echo Installation directory not found: %INSTALL_DIR%
    echo Please ensure the system is installed correctly
    pause
    exit /b 1
)

echo Copying files to installation directory...
copy /Y "handyman_kpi_launcher_detached.pyw" %INSTALL_DIR%\
copy /Y "fix_database_all.py" %INSTALL_DIR%\

echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('C:\Users\Public\Desktop\Handyman KPI System.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\handyman_kpi_launcher_detached.pyw'; $Shortcut.IconLocation = '%INSTALL_DIR%\kpi-system\static\images\favicon.ico,0'; $Shortcut.Save()"

echo.
echo ======================================================
echo Fix completed successfully!
echo ======================================================
echo The system should now start without showing a terminal window
echo and the database structure has been fixed.
echo.
echo Default admin user:
echo Username: admin
echo Password: admin
echo.
echo Please change this password after logging in.
echo ======================================================
pause