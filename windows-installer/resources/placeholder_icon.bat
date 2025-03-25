@echo off
REM This batch file creates a simple placeholder icon file
REM It copies a standard Windows icon to use as a placeholder

echo Creating placeholder icon...
copy %windir%\system32\shell32.dll,22 icon.ico
if %errorlevel% neq 0 (
    echo Failed to copy icon. Using a different approach...
    copy %windir%\system32\mmsys.cpl,1 icon.ico
)
if %errorlevel% neq 0 (
    echo Failed again. Creating an empty icon file...
    echo Icon > icon.ico
)

echo Placeholder icon created.
