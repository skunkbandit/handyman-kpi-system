@echo off
echo Installing missing dependencies...

REM Switch to the application directory
cd /d "C:\Users\dtest\KPI Project"

REM Install pandas in the installed application environment
cd /d "C:\Users\dtest\AppData\Local\Programs\Handyman KPI System\python"
.\python.exe -m pip install pandas

echo Dependencies installation complete.
pause
