@echo off
echo Backing up original files...
if not exist "src\app" mkdir "src\app"
copy "src\app\__init__.py" "src\app\__init__.py.backup"
copy "src\launcher.py" "src\launcher.py.backup"
copy "src\wsgi.py" "src\wsgi.py.backup"
echo Files backed up successfully.
pause