@echo off
echo Rebuilding Handyman KPI System Installer...
echo ==========================================

REM Ensure output directory exists
if not exist output mkdir output

REM Run the Inno Setup compiler on our script
echo Compiling installer...
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" installer.iss

echo.
echo Installer build completed.
echo Output file: output\handyman-kpi-system-setup.exe
echo.
pause