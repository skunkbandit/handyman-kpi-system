@echo off
echo Rebuilding installer with latest code fixes...

REM Copy latest application code to src directory
xcopy /E /Y /I "..\kpi-system" ".\src\kpi-system"

REM Build the installer
call build_installer.bat

echo Installer rebuild completed. The new installer is available in the output directory.
pause
