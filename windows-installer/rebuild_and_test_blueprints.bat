@echo off
echo ========================================
echo Handyman KPI System - Rebuild with Blueprints
echo ========================================

cd "%~dp0windows-installer"

echo.
echo Building installer...
echo ========================================
call rebuild_installer.bat

echo.
echo Installation and Testing Instructions:
echo ========================================
echo 1. Run the installer from 'windows-installer\output\handyman-kpi-system-setup.exe'
echo 2. Follow the installation steps
echo 3. Launch the application from the Start Menu or Desktop shortcut
echo 4. The application should now show the login page from the auth blueprint
echo 5. Verify login functionality and error page rendering
echo.
echo Note: We have re-enabled the main and auth blueprints.
echo If there are any errors, please check the following:
echo  - Missing template files in the templates directory
echo  - Missing packages in the Python environment
echo  - Database connection issues
echo.
pause