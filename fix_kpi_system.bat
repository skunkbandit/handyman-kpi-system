@echo off
echo ===================================================
echo Handyman KPI System - Complete Fix Script
echo ===================================================
echo This script will:
echo 1. Fix database schema issues
echo 2. Fix launcher window issues
echo 3. Create improved desktop shortcuts
echo ---------------------------------------------------
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo NOTICE: This script will work best with administrator privileges.
    echo Some functions will still work without admin rights.
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

:: Step 2: Fix launcher window
echo.
echo ===================================================
echo Step 2: Fixing launcher window...
echo ===================================================
python "%SCRIPT_DIR%fix_launcher_window.py"
if %errorlevel% neq 0 (
    echo ERROR: Launcher window fix failed.
    echo Please check the logs at "%APPDATA_DIR%\logs\launcher_fix.log".
    echo.
    pause
    exit /b 1
)

:: Copy launcher to Program Files if needed and if we have admin rights
if "%INSTALL_DIR%"=="%PROG_FILES_DIR%" (
    echo.
    echo Copying detached launcher to installation directory...
    
    :: Check if we are running as admin
    net session >nul 2>&1
    if %errorlevel% equ 0 (
        :: We have admin rights, copy the file
        copy /Y "%SCRIPT_DIR%handyman_kpi_launcher_detached.py" "%INSTALL_DIR%\handyman_kpi_launcher_detached.py"
        echo Launcher deployed successfully.
    ) else (
        :: No admin rights, show manual instructions
        echo.
        echo ===================================================
        echo MANUAL STEP REQUIRED - ADMIN PRIVILEGES NEEDED
        echo ===================================================
        echo.
        echo To complete the installation, please open a Command Prompt as Administrator
        echo and run the following command:
        echo.
        echo copy "%SCRIPT_DIR%handyman_kpi_launcher_detached.py" "%INSTALL_DIR%\handyman_kpi_launcher_detached.py"
        echo.
        echo ===================================================
        echo.
        pause
    )
)

:: Final message
echo.
echo ===================================================
echo Handyman KPI System Fix - Complete
echo ===================================================
echo.
echo All fixes have been applied successfully.
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
