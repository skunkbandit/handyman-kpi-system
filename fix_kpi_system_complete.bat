@echo off
echo ===================================================
echo Handyman KPI System - Complete Fix Script
echo ===================================================
echo This script will fix:
echo 1. Database schema issues (missing columns)
echo 2. Launcher window issues (terminal stays open)
echo 3. Datetime import issues (password reset error)
echo 4. Admin user issues (login credentials)
echo ---------------------------------------------------
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo NOTICE: This script will work best with administrator privileges.
    echo Some functions will still work without admin rights.
    echo Some fixes will need to be manually applied.
    echo.
    pause
)

echo Checking Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH.
    echo Please make sure Python is installed and added to PATH.
    echo.
    pause
    exit /b 1
)

:: Find install directory
set "SCRIPT_DIR=%~dp0"
echo Script directory: %SCRIPT_DIR%

:: Set installation directory paths
set "PROG_FILES_DIR=C:\Program Files\Handyman KPI System"
set "USER_DIR=%SCRIPT_DIR%"

:: Check which installation directory exists
if exist "%PROG_FILES_DIR%" (
    set "INSTALL_DIR=%PROG_FILES_DIR%"
) else (
    set "INSTALL_DIR=%USER_DIR%"
)
echo Installation directory: %INSTALL_DIR%

:: Create AppData directories if they don't exist
echo Creating AppData directories...
set "APPDATA_DIR=%LOCALAPPDATA%\Handyman KPI System"
if not exist "%APPDATA_DIR%" mkdir "%APPDATA_DIR%"
if not exist "%APPDATA_DIR%\config" mkdir "%APPDATA_DIR%\config"
if not exist "%APPDATA_DIR%\database" mkdir "%APPDATA_DIR%\database"
if not exist "%APPDATA_DIR%\logs" mkdir "%APPDATA_DIR%\logs"

:: Step 1: Fix database schema
echo.
echo ===================================================
echo Step 1: Fixing database schema...
echo ===================================================
python "%SCRIPT_DIR%fix_database_schema.py"
if %errorlevel% neq 0 (
    echo ERROR: Database schema fix failed.
    echo Please check the logs at "%APPDATA_DIR%\logs\database_schema_fix.log".
    echo.
    pause
    exit /b 1
)
echo Database schema fix completed successfully.
echo.

:: Step 2: Fix admin user
echo.
echo ===================================================
echo Step 2: Fixing admin user...
echo ===================================================
python "%SCRIPT_DIR%fix_admin_user.py"
if %errorlevel% neq 0 (
    echo ERROR: Admin user fix failed.
    echo Please check the logs at "%APPDATA_DIR%\logs\admin_user_fix.log".
    echo.
    pause
    exit /b 1
)
echo Admin user fix completed successfully.
echo.

:: Step 3: Fix datetime import
echo.
echo ===================================================
echo Step 3: Fixing datetime imports...
echo ===================================================
python "%SCRIPT_DIR%fix_datetime_imports.py"
if %errorlevel% neq 0 (
    echo ERROR: Datetime imports fix failed.
    echo Please check the logs at "%APPDATA_DIR%\logs\datetime_fix.log".
    echo.
    pause
    exit /b 1
)
echo A fixed version of the user.py file has been created.
echo.

:: Step 4: Fix launcher window
echo.
echo ===================================================
echo Step 4: Fixing launcher window...
echo ===================================================
python "%SCRIPT_DIR%fix_launcher_window.py"
if %errorlevel% neq 0 (
    echo ERROR: Launcher window fix failed.
    echo Please check the logs at "%APPDATA_DIR%\logs\launcher_fix.log".
    echo.
    pause
    exit /b 1
)

:: Check if we have admin rights for copying files
net session >nul 2>&1
if %errorlevel% equ 0 (
    :: We have admin rights, copy the files
    echo.
    echo ===================================================
    echo Applying fixes to Program Files (Admin mode)...
    echo ===================================================
    
    :: Copy the fixed user.py
    if exist "%SCRIPT_DIR%fixed_user.py" (
        copy /Y "%SCRIPT_DIR%fixed_user.py" "%INSTALL_DIR%\kpi-system\backend\app\models\user.py"
        echo Fixed user.py applied successfully.
    )
    
    :: Copy the detached launcher
    if exist "%SCRIPT_DIR%handyman_kpi_launcher_detached.py" (
        copy /Y "%SCRIPT_DIR%handyman_kpi_launcher_detached.py" "%INSTALL_DIR%\handyman_kpi_launcher_detached.py"
        echo Detached launcher applied successfully.
    )
) else (
    :: No admin rights, show manual instructions
    echo.
    echo ===================================================
    echo MANUAL STEPS REQUIRED - ADMIN PRIVILEGES NEEDED
    echo ===================================================
    echo.
    echo To complete the installation, please open a Command Prompt as Administrator
    echo and run the following commands:
    echo.
    if exist "%SCRIPT_DIR%fixed_user.py" (
        echo copy "%SCRIPT_DIR%fixed_user.py" "%INSTALL_DIR%\kpi-system\backend\app\models\user.py"
    )
    if exist "%SCRIPT_DIR%handyman_kpi_launcher_detached.py" (
        echo copy "%SCRIPT_DIR%handyman_kpi_launcher_detached.py" "%INSTALL_DIR%\handyman_kpi_launcher_detached.py"
    )
    echo.
    echo ===================================================
    echo.
    pause
)

:: Final message
echo.
echo ===================================================
echo Handyman KPI System Fix - Complete
echo ===================================================
echo.
echo All fixes have been applied or prepared successfully.
echo.
echo Desktop shortcuts have been created:
echo - "Handyman KPI System" - Launches the application without a console window
echo - "Handyman KPI System (Browser)" - Opens the application in your web browser
echo.
echo Default login credentials:
echo Username: admin
echo Password: admin
echo.
echo Please use these credentials to log in and then
echo change your password for security.
echo.
echo Thank you for using Handyman KPI System!
echo.
pause
