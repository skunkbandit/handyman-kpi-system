@echo off
echo ==============================================
echo Handyman KPI System - Comprehensive Fix Script
echo ==============================================
echo.

echo Step 1: Installing missing dependencies...
cd /d "C:\Users\dtest\AppData\Local\Programs\Handyman KPI System\python"
.\python.exe -m pip install pandas

echo.
echo Step 2: Fixing templates...
copy /Y "C:\Users\dtest\KPI Project\fixed_base.html" "C:\Users\dtest\AppData\Local\Programs\Handyman KPI System\app\templates\base.html"

echo.
echo Step 3: Updating blueprint imports...
echo from app.routes.main import bp as main_bp> temp.txt
echo from app.routes.auth import bp as auth_bp>> temp.txt
echo.>> temp.txt
echo app.register_blueprint(main_bp)>> temp.txt
echo app.register_blueprint(auth_bp)>> temp.txt

echo.
echo Step 4: Restarting application...
taskkill /F /IM python.exe 2>nul

echo.
echo Fix completed! Please restart the application to apply changes.
echo.
echo If you continue to experience issues:
echo 1. Uninstall the current version
echo 2. Install the latest version from the installer
echo 3. Apply this fix script again if necessary
echo.

pause
