@echo off
echo Building the installer...
cd windows-installer
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" installer.iss
echo Done!