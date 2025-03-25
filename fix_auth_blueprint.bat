@echo off
echo Fixing auth blueprint in the installed application...

set INSTALLED_APP=C:\Users\dtest\AppData\Local\Programs\Handyman KPI System
set AUTH_FILE=%INSTALLED_APP%\app\routes\auth.py

echo Searching for "auth_bp" in auth.py...
findstr /C:"auth_bp" "%AUTH_FILE%" > nul
if %errorlevel% equ 0 (
    echo Found references to auth_bp, replacing with bp...
    
    echo Creating backup...
    copy /Y "%AUTH_FILE%" "%AUTH_FILE%.bak"
    
    echo Replacing auth_bp with bp...
    powershell -Command "(Get-Content '%AUTH_FILE%') -replace 'auth_bp', 'bp' | Set-Content '%AUTH_FILE%'"
    
    echo Blueprint fix completed.
) else (
    echo No references to auth_bp found in auth.py, no changes needed.
)

echo Fixing complete.
pause
