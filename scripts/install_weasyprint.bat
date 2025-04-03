@echo off
echo =======================================================
echo Installing WeasyPrint and Dependencies
echo =======================================================
echo.

set "WHEELS_DIR=%~dp0..\wheels"
set "PYTHON_EXE=python"

:: Check for Python installation
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH.
    echo Please make sure Python is installed and added to PATH.
    echo.
    exit /b 1
)

:: Create wheels directory if it doesn't exist
if not exist "%WHEELS_DIR%" mkdir "%WHEELS_DIR%"

:: Check if GTK3 Runtime is already installed
if not exist "C:\Program Files\GTK3-Runtime\bin\gtk3-demo.exe" (
    if exist "%~dp0..\installers\gtk3-runtime-installer.exe" (
        echo Installing GTK3 Runtime...
        start /wait "" "%~dp0..\installers\gtk3-runtime-installer.exe" /S
        echo GTK3 Runtime installed.
    ) else (
        echo WARNING: GTK3 Runtime installer not found.
        echo WeasyPrint may not function correctly without GTK3 Runtime.
        echo You may need to install GTK3 manually.
        echo.
    )
) else (
    echo GTK3 Runtime is already installed.
)

:: Check if WeasyPrint wheels are available
if exist "%WHEELS_DIR%\weasyprint*.whl" (
    echo Installing WeasyPrint from wheels...
    %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" weasyprint
    echo WeasyPrint installed from wheels.
) else (
    echo WeasyPrint wheel files not found. Attempting to install from PyPI...
    %PYTHON_EXE% -m pip install weasyprint
    echo WeasyPrint installed from PyPI.
)

:: Install other required dependencies
echo Installing other dependencies...
%PYTHON_EXE% -m pip install Flask Flask-SQLAlchemy Flask-Login Flask-WTF Werkzeug

echo.
echo =======================================================
echo WeasyPrint and dependencies installation complete.
echo =======================================================
