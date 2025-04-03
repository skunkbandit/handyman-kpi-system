@echo off
echo =======================================================
echo Building Handyman KPI System Installer
echo =======================================================
echo.

:: Check for Inno Setup
where iscc >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Inno Setup Compiler (iscc.exe) not found in PATH.
    echo Please install Inno Setup from https://jrsoftware.org/isinfo.php
    echo and make sure it's added to your PATH.
    echo.
    pause
    exit /b 1
)

:: Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH.
    echo Please make sure Python is installed and added to PATH.
    echo.
    pause
    exit /b 1
)

:: Create required directories
if not exist "wheels" mkdir wheels
if not exist "installers" mkdir installers
if not exist "installer\output" mkdir installer\output

:: Check for required files
if not exist "handyman_kpi_launcher_detached.py" (
    echo ERROR: handyman_kpi_launcher_detached.py not found.
    echo This file is required for the installer.
    echo.
    pause
    exit /b 1
)

if not exist "initialize_database.py" (
    echo ERROR: initialize_database.py not found.
    echo This file is required for the installer.
    echo.
    pause
    exit /b 1
)

:: Download wheel files if needed
echo Checking for required wheel files...
set "WHEEL_COUNT=0"
for %%F in (wheels\*.whl) do set /a WHEEL_COUNT+=1

if %WHEEL_COUNT% equ 0 (
    echo No wheel files found. Downloading required dependencies...
    python scripts\download_wheels.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to download wheel files.
        echo Please check the output for errors and try again.
        echo.
        pause
        exit /b 1
    )
) else (
    echo Found %WHEEL_COUNT% wheel files in the 'wheels' directory.
)

:: Check for GTK3 Runtime installer
if not exist "installers\gtk3-runtime-installer.exe" (
    echo GTK3 Runtime installer not found. Downloading...
    python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe', 'installers\\gtk3-runtime-installer.exe')"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to download GTK3 Runtime installer.
        echo Please download it manually from:
        echo https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
        echo and place it in the 'installers' directory.
        echo.
        pause
        exit /b 1
    )
)

:: Test WeasyPrint installation locally
echo Testing WeasyPrint installation...
python scripts\test_weasyprint.py
if %errorlevel% neq 0 (
    echo WARNING: WeasyPrint test failed. The installer may not be able to install WeasyPrint correctly.
    echo You can continue building the installer, but PDF generation may not work.
    echo.
    choice /C YN /M "Do you want to continue building the installer anyway?"
    if %errorlevel% equ 2 (
        echo Build cancelled.
        exit /b 1
    )
)

:: Build the installer
echo Building installer...
iscc "scripts\installer.iss"
if %errorlevel% neq 0 (
    echo ERROR: Failed to build installer.
    echo Check the Inno Setup compiler output for errors.
    echo.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo Installer build complete!
echo =======================================================
echo Installer is located in: installer\output\handyman-kpi-system-setup.exe
echo.

pause
