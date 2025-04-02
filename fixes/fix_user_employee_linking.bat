@echo off
echo ================================================
echo Fixing User-Employee Linking Issue (Direct Fix)
echo ================================================

REM Get current directory
set SCRIPT_DIR=%~dp0
echo Working directory: %SCRIPT_DIR%

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please make sure Python is installed and in your PATH.
    goto error
)

REM Check if script exists
if not exist "%SCRIPT_DIR%fix_user_employee_linking_direct.py" (
    echo ERROR: fix_user_employee_linking_direct.py not found in current directory.
    echo Current directory: %SCRIPT_DIR%
    goto error
)

REM Check if fixed template files exist
if not exist "%SCRIPT_DIR%templates\auth\fixed_create_user.html" (
    echo ERROR: fixed_create_user.html not found in %SCRIPT_DIR%templates\auth\
    goto error
)

if not exist "%SCRIPT_DIR%templates\auth\fixed_edit_user.html" (
    echo ERROR: fixed_edit_user.html not found in %SCRIPT_DIR%templates\auth\
    goto error
)

if not exist "%SCRIPT_DIR%templates\auth\fixed_user_management.html" (
    echo ERROR: fixed_user_management.html not found in %SCRIPT_DIR%templates\auth\
    goto error
)

REM Run the Python script
python "%SCRIPT_DIR%fix_user_employee_linking_direct.py"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fix script failed.
    goto error
)

echo.
echo Fix applied successfully!
echo The user-employee linking issue has been fixed.
echo.
pause
exit /b 0

:error
echo.
echo Fix failed. Please check the error message above.
pause
exit /b 1
