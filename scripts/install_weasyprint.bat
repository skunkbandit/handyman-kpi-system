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

:: Create logs directory
set "APPDATA_DIR=%LOCALAPPDATA%\Handyman KPI System"
set "LOG_DIR=%APPDATA_DIR%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Create log file
set "LOG_FILE=%LOG_DIR%\weasyprint_install.log"
echo Installing WeasyPrint at %DATE% %TIME% > "%LOG_FILE%"

:: Check if GTK3 Runtime is already installed
if not exist "C:\Program Files\GTK3-Runtime\bin\gtk3-demo.exe" (
    if exist "%~dp0..\installers\gtk3-runtime-installer.exe" (
        echo Installing GTK3 Runtime...
        echo Installing GTK3 Runtime... >> "%LOG_FILE%"
        start /wait "" "%~dp0..\installers\gtk3-runtime-installer.exe" /S
        echo GTK3 Runtime installed.
        echo GTK3 Runtime installed. >> "%LOG_FILE%"
    ) else (
        echo WARNING: GTK3 Runtime installer not found.
        echo WARNING: GTK3 Runtime installer not found. >> "%LOG_FILE%"
        echo WeasyPrint may not function correctly without GTK3 Runtime.
        echo You may need to install GTK3 manually from:
        echo https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
        echo.
    )
) else (
    echo GTK3 Runtime is already installed.
    echo GTK3 Runtime is already installed. >> "%LOG_FILE%"
)

:: Count wheel files in the wheels directory
set "WHEEL_COUNT=0"
for %%F in ("%WHEELS_DIR%\*.whl") do set /a WHEEL_COUNT+=1

:: Install dependencies
if %WHEEL_COUNT% gtr 0 (
    echo Installing WeasyPrint and dependencies from wheel files...
    echo Installing WeasyPrint and dependencies from wheel files... >> "%LOG_FILE%"
    
    :: First try installing all dependencies at once
    %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" weasyprint >> "%LOG_FILE%" 2>&1
    if %errorlevel% neq 0 (
        echo First attempt failed, trying to install dependencies individually...
        echo First attempt failed, trying to install dependencies individually... >> "%LOG_FILE%"
        
        :: Install major dependencies first
        %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" cffi >> "%LOG_FILE%" 2>&1
        %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" pycparser >> "%LOG_FILE%" 2>&1
        %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" cairocffi >> "%LOG_FILE%" 2>&1
        %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" cssselect2 >> "%LOG_FILE%" 2>&1
        %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" tinycss2 >> "%LOG_FILE%" 2>&1
        %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" html5lib >> "%LOG_FILE%" 2>&1
        %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" Pillow >> "%LOG_FILE%" 2>&1
        
        :: Finally install WeasyPrint
        %PYTHON_EXE% -m pip install --no-index --find-links="%WHEELS_DIR%" weasyprint >> "%LOG_FILE%" 2>&1
    )
) else (
    echo No wheel files found, attempting to install from PyPI...
    echo No wheel files found, attempting to install from PyPI... >> "%LOG_FILE%"
    %PYTHON_EXE% -m pip install weasyprint >> "%LOG_FILE%" 2>&1
)

:: Check if WeasyPrint was installed successfully
%PYTHON_EXE% -c "import weasyprint" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo WeasyPrint installed successfully!
    echo WeasyPrint installed successfully! >> "%LOG_FILE%"
) else (
    echo.
    echo WARNING: WeasyPrint installation may have failed.
    echo WARNING: WeasyPrint installation may have failed. >> "%LOG_FILE%"
    echo Check the log file for details: %LOG_FILE%
)

:: Install other required dependencies for the application
echo.
echo Installing other application dependencies...
echo Installing other application dependencies... >> "%LOG_FILE%"
%PYTHON_EXE% -m pip install Flask Flask-SQLAlchemy Flask-Login Flask-WTF Werkzeug >> "%LOG_FILE%" 2>&1

echo.
echo =======================================================
echo Installation complete!
echo =======================================================
echo.
echo Log file: %LOG_FILE%

exit /b 0
