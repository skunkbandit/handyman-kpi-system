@echo off
echo ================================================
echo Handyman KPI System - Mock Reports Fix
echo ================================================
echo.

set INSTALLED_APP=C:\Users\dtest\AppData\Local\Programs\Handyman KPI System

REM Step 1: Stopping any running instances
echo Step 1: Stopping any running instances...
taskkill /F /IM python.exe 2>nul

REM Step 2: Create mock reports module to prevent WeasyPrint import
echo.
echo Step 2: Creating mock reports module...

set REPORTS_DIR=%INSTALLED_APP%\app\reports
echo Creating backup of reports directory...
if not exist "%REPORTS_DIR%.bak" (
    xcopy /E /I /Y "%REPORTS_DIR%" "%REPORTS_DIR%.bak"
)

REM Clear existing reports directory
if exist "%REPORTS_DIR%" (
    rd /S /Q "%REPORTS_DIR%"
)
mkdir "%REPORTS_DIR%"

REM Create mock __init__.py
echo """Mock reports module""" > "%REPORTS_DIR%\__init__.py"
echo. >> "%REPORTS_DIR%\__init__.py"

REM Create mock base.py
echo """Mock report generator base class""" > "%REPORTS_DIR%\base.py"
echo. >> "%REPORTS_DIR%\base.py"
echo class ReportGenerator: >> "%REPORTS_DIR%\base.py"
echo     """Mockup of report generator that doesn't import WeasyPrint""" >> "%REPORTS_DIR%\base.py"
echo     def __init__(self, *args, **kwargs): >> "%REPORTS_DIR%\base.py"
echo         self.name = "Mock Report" >> "%REPORTS_DIR%\base.py"
echo         self.supported_formats = ["html", "pdf"] >> "%REPORTS_DIR%\base.py"
echo. >> "%REPORTS_DIR%\base.py"
echo     def generate(self, *args, **kwargs): >> "%REPORTS_DIR%\base.py"
echo         return "This is a mock report. Real reports are unavailable in emergency mode." >> "%REPORTS_DIR%\base.py"
echo. >> "%REPORTS_DIR%\base.py"

REM Create mock generators.py
echo """Mock report generators""" > "%REPORTS_DIR%\generators.py"
echo. >> "%REPORTS_DIR%\generators.py"
echo from .base import ReportGenerator >> "%REPORTS_DIR%\generators.py"
echo. >> "%REPORTS_DIR%\generators.py"
echo def get_report_generator(report_type): >> "%REPORTS_DIR%\generators.py"
echo     """Return a mock report generator""" >> "%REPORTS_DIR%\generators.py"
echo     return ReportGenerator() >> "%REPORTS_DIR%\generators.py"
echo. >> "%REPORTS_DIR%\generators.py"
echo def get_available_report_types(): >> "%REPORTS_DIR%\generators.py"
echo     """Return mock available report types""" >> "%REPORTS_DIR%\generators.py"
echo     return [ >> "%REPORTS_DIR%\generators.py"
echo         {"id": "mock", "name": "Mock Report", "description": "Real reports are disabled in emergency mode"} >> "%REPORTS_DIR%\generators.py"
echo     ] >> "%REPORTS_DIR%\generators.py"
echo. >> "%REPORTS_DIR%\generators.py"

REM Create mock employee_performance.py
echo """Mock employee performance report""" > "%REPORTS_DIR%\employee_performance.py"
echo. >> "%REPORTS_DIR%\employee_performance.py"
echo from .base import ReportGenerator >> "%REPORTS_DIR%\employee_performance.py"
echo. >> "%REPORTS_DIR%\employee_performance.py"
echo class EmployeePerformanceReport(ReportGenerator): >> "%REPORTS_DIR%\employee_performance.py"
echo     """Mock employee performance report""" >> "%REPORTS_DIR%\employee_performance.py"
echo     def __init__(self, *args, **kwargs): >> "%REPORTS_DIR%\employee_performance.py"
echo         super().__init__() >> "%REPORTS_DIR%\employee_performance.py"
echo         self.name = "Employee Performance" >> "%REPORTS_DIR%\employee_performance.py"
echo. >> "%REPORTS_DIR%\employee_performance.py"
echo     def generate(self, *args, **kwargs): >> "%REPORTS_DIR%\employee_performance.py"
echo         return "This is a mock employee performance report. Real reports are unavailable in emergency mode." >> "%REPORTS_DIR%\employee_performance.py"
echo. >> "%REPORTS_DIR%\employee_performance.py"

REM Step 3: Fix auth blueprint in auth.py
echo.
echo Step 3: Fixing auth blueprint in auth.py...
set AUTH_FILE=%INSTALLED_APP%\app\routes\auth.py
echo Creating backup...
copy /Y "%AUTH_FILE%" "%AUTH_FILE%.bak"
echo Replacing auth_bp with bp...
powershell -Command "(Get-Content '%AUTH_FILE%') -replace 'auth_bp', 'bp' | Set-Content '%AUTH_FILE%'"

echo.
echo Mock Reports Fix Completed!
echo.
echo This fix replaces the reports module with mock classes that have the same
echo interface but don't depend on WeasyPrint. The application should now start
echo and basic functionality should work, but report generation will be disabled.
echo.
echo Please try starting the application again.

pause
