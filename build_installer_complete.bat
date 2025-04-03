@echo off
setlocal EnableDelayedExpansion

echo =======================================================
echo Building Complete Handyman KPI System Installer
echo =======================================================
echo.

:: Find Inno Setup
set "ISCC_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\iscc.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\iscc.exe"
if exist "C:\Program Files\Inno Setup 6\iscc.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\iscc.exe"
if exist "C:\Program Files (x86)\Inno Setup 5\iscc.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 5\iscc.exe"
if exist "C:\Program Files\Inno Setup 5\iscc.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 5\iscc.exe"

if not defined ISCC_PATH (
    where iscc >nul 2>&1
    if !errorlevel! equ 0 (
        set "ISCC_PATH=iscc"
    ) else (
        echo ERROR: Could not find Inno Setup Compiler.
        echo Please enter the full path to iscc.exe:
        set /p ISCC_PATH=
        
        if not exist "!ISCC_PATH!" (
            echo Invalid path. Exiting.
            pause
            exit /b 1
        )
    )
)

echo Using Inno Setup at: %ISCC_PATH%
echo.

:: Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH.
    echo Please make sure Python is installed and added to PATH.
    echo.
    pause
    exit /b 1
)

:: Create required directories if they don't exist
echo Creating required directories...
if not exist "installer" mkdir installer
if not exist "installer\output" mkdir installer\output
if not exist "wheels" mkdir wheels
if not exist "installers" mkdir installers

:: Verify required files exist
echo Checking required files...
if not exist "handyman_kpi_launcher_detached.py" (
    echo ERROR: handyman_kpi_launcher_detached.py not found.
    echo This file is required for the installer.
    echo.
    pause
    exit /b 1
)

if not exist "initialize_database.py" (
    echo ERROR: initialize_database.py not found.
    echo This file is required for the installer.
    echo.
    pause
    exit /b 1
)

:: Create a comprehensive installer script
echo Creating comprehensive installer script...

echo ; Complete Handyman KPI System Installer Script > scripts\installer_complete.iss
echo ; Created to include all necessary components >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo #define MyAppName "Handyman KPI System" >> scripts\installer_complete.iss
echo #define MyAppVersion "1.2.0" >> scripts\installer_complete.iss
echo #define MyAppPublisher "Handyman Solutions" >> scripts\installer_complete.iss
echo #define MyAppURL "https://github.com/skunkbandit/handyman-kpi-system" >> scripts\installer_complete.iss
echo #define MyAppExeName "handyman_kpi_launcher_detached.py" >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo [Setup] >> scripts\installer_complete.iss
echo ; Basic installer settings >> scripts\installer_complete.iss
echo AppId={{C65B49B8-8334-4EDF-821A-AE099B5B5D64} >> scripts\installer_complete.iss
echo AppName={#MyAppName} >> scripts\installer_complete.iss
echo AppVersion={#MyAppVersion} >> scripts\installer_complete.iss
echo AppPublisher={#MyAppPublisher} >> scripts\installer_complete.iss
echo AppPublisherURL={#MyAppURL} >> scripts\installer_complete.iss
echo AppSupportURL={#MyAppURL} >> scripts\installer_complete.iss
echo AppUpdatesURL={#MyAppURL} >> scripts\installer_complete.iss
echo DefaultDirName={autopf}\{#MyAppName} >> scripts\installer_complete.iss
echo DefaultGroupName={#MyAppName} >> scripts\installer_complete.iss
echo AllowNoIcons=yes >> scripts\installer_complete.iss
echo ; Compression settings >> scripts\installer_complete.iss
echo Compression=lzma2 >> scripts\installer_complete.iss
echo SolidCompression=yes >> scripts\installer_complete.iss
echo ; Installer appearance and behavior >> scripts\installer_complete.iss
echo WizardStyle=modern >> scripts\installer_complete.iss
echo DisableWelcomePage=no >> scripts\installer_complete.iss
echo DisableDirPage=no >> scripts\installer_complete.iss
echo DisableProgramGroupPage=yes >> scripts\installer_complete.iss
echo ; Output settings >> scripts\installer_complete.iss
echo OutputDir=..\installer\output >> scripts\installer_complete.iss
echo OutputBaseFilename=handyman-kpi-system-setup >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

:: Add icon references if resources exist
if exist "resources\logo.ico" (
    echo SetupIconFile=..\resources\logo.ico >> scripts\installer_complete.iss
    echo UninstallDisplayIcon={app}\resources\logo.ico >> scripts\installer_complete.iss
)

echo ; Privileges and compatibility >> scripts\installer_complete.iss
echo PrivilegesRequired=admin >> scripts\installer_complete.iss
echo ArchitecturesInstallIn64BitMode=x64 >> scripts\installer_complete.iss
echo ; Other settings >> scripts\installer_complete.iss
echo UsePreviousAppDir=yes >> scripts\installer_complete.iss
echo UsePreviousGroup=yes >> scripts\installer_complete.iss
echo ChangesEnvironment=yes >> scripts\installer_complete.iss
echo CloseApplications=yes >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo [Languages] >> scripts\installer_complete.iss
echo Name: "english"; MessagesFile: "compiler:Default.isl" >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo [Tasks] >> scripts\installer_complete.iss
echo Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked >> scripts\installer_complete.iss
echo Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo [Files] >> scripts\installer_complete.iss
echo ; Core Python files >> scripts\installer_complete.iss
echo Source: "..\handyman_kpi_launcher_detached.py"; DestDir: "{app}"; Flags: ignoreversion >> scripts\installer_complete.iss
echo Source: "..\initialize_database.py"; DestDir: "{app}"; Flags: ignoreversion >> scripts\installer_complete.iss
echo Source: "..\handyman_kpi_launcher_detached.pyw"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\*.py"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo ; CRITICAL DIRECTORIES - Main application components >> scripts\installer_complete.iss
echo Source: "..\backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\database\*"; DestDir: "{app}\database"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\kpi-system\*"; DestDir: "{app}\kpi-system"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo ; Support directories >> scripts\installer_complete.iss
echo Source: "..\installers\*"; DestDir: "{app}\installers"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\wheels\*"; DestDir: "{app}\wheels"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\logs\*"; DestDir: "{app}\logs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\windows-installer\*"; DestDir: "{app}\windows-installer"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo ; Any other critical files or directories >> scripts\installer_complete.iss
echo Source: "..\fixes\*"; DestDir: "{app}\fixes"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo ; Extra files - will be skipped if they don't exist >> scripts\installer_complete.iss
echo Source: "..\*.bat"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\*.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\*.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist >> scripts\installer_complete.iss
echo Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo [Dirs] >> scripts\installer_complete.iss
echo ; Create directories with proper permissions >> scripts\installer_complete.iss
echo Name: "{localappdata}\{#MyAppName}"; Permissions: users-modify >> scripts\installer_complete.iss
echo Name: "{localappdata}\{#MyAppName}\logs"; Permissions: users-modify >> scripts\installer_complete.iss
echo Name: "{localappdata}\{#MyAppName}\database"; Permissions: users-modify >> scripts\installer_complete.iss
echo Name: "{localappdata}\{#MyAppName}\config"; Permissions: users-modify >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo [Icons] >> scripts\installer_complete.iss
echo ; Create start menu shortcuts >> scripts\installer_complete.iss
if exist "resources\logo.ico" (
    echo Name: "{group}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\resources\logo.ico" >> scripts\installer_complete.iss
    echo Name: "{autodesktop}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\resources\logo.ico"; Tasks: desktopicon >> scripts\installer_complete.iss
    echo Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\resources\logo.ico"; Tasks: quicklaunchicon >> scripts\installer_complete.iss
) else (
    echo Name: "{group}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}" >> scripts\installer_complete.iss
    echo Name: "{autodesktop}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; Tasks: desktopicon >> scripts\installer_complete.iss
    echo Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; Tasks: quicklaunchicon >> scripts\installer_complete.iss
)
echo Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}" >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo [Run] >> scripts\installer_complete.iss
if exist "scripts\install_weasyprint.bat" (
    echo Filename: "{app}\scripts\install_weasyprint.bat"; WorkingDir: "{app}"; Flags: runhidden waituntilterminated >> scripts\installer_complete.iss
)
if exist "scripts\create_shortcuts.ps1" (
    echo Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\scripts\create_shortcuts.ps1"""; WorkingDir: "{app}"; Flags: runhidden waituntilterminated >> scripts\installer_complete.iss
)
echo Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\initialize_database.py"""; WorkingDir: "{app}"; Flags: runhidden waituntilterminated >> scripts\installer_complete.iss
echo Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo [Registry] >> scripts\installer_complete.iss
echo ; Store installation path in registry >> scripts\installer_complete.iss
echo Root: HKLM; Subkey: "SOFTWARE\{#MyAppName}"; Flags: uninsdeletekey >> scripts\installer_complete.iss
echo Root: HKLM; Subkey: "SOFTWARE\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}" >> scripts\installer_complete.iss
echo Root: HKLM; Subkey: "SOFTWARE\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}" >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo [UninstallDelete] >> scripts\installer_complete.iss
echo ; Clean up files during uninstall >> scripts\installer_complete.iss
echo Type: files; Name: "{userdesktop}\{#MyAppName} (Browser).url" >> scripts\installer_complete.iss
echo Type: dirifempty; Name: "{app}" >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo [Code] >> scripts\installer_complete.iss
echo // Check if Python 3.8+ is installed >> scripts\installer_complete.iss
echo function IsPythonInstalled(): Boolean; >> scripts\installer_complete.iss
echo var >> scripts\installer_complete.iss
echo   PythonPath: String; >> scripts\installer_complete.iss
echo   ResultCode: Integer; >> scripts\installer_complete.iss
echo begin >> scripts\installer_complete.iss
echo   // Try to find Python executable >> scripts\installer_complete.iss
echo   Result := False; >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo   // Check for Python in PATH >> scripts\installer_complete.iss
echo   if Exec('where', 'python', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then >> scripts\installer_complete.iss
echo   begin >> scripts\installer_complete.iss
echo     if ResultCode = 0 then >> scripts\installer_complete.iss
echo     begin >> scripts\installer_complete.iss
echo       Result := True; >> scripts\installer_complete.iss
echo       Exit; >> scripts\installer_complete.iss
echo     end; >> scripts\installer_complete.iss
echo   end; >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo   // Check common installation locations >> scripts\installer_complete.iss
echo   if FileExists(ExpandConstant('{autopf}\Python\python.exe')) then >> scripts\installer_complete.iss
echo   begin >> scripts\installer_complete.iss
echo     Result := True; >> scripts\installer_complete.iss
echo     Exit; >> scripts\installer_complete.iss
echo   end; >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo   if FileExists(ExpandConstant('{autopf}\Python39\python.exe')) then >> scripts\installer_complete.iss
echo   begin >> scripts\installer_complete.iss
echo     Result := True; >> scripts\installer_complete.iss
echo     Exit; >> scripts\installer_complete.iss
echo   end; >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo   if FileExists(ExpandConstant('{autopf}\Python310\python.exe')) then >> scripts\installer_complete.iss
echo   begin >> scripts\installer_complete.iss
echo     Result := True; >> scripts\installer_complete.iss
echo     Exit; >> scripts\installer_complete.iss
echo   end; >> scripts\installer_complete.iss
echo end; >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo // Pre-installation check >> scripts\installer_complete.iss
echo function InitializeSetup(): Boolean; >> scripts\installer_complete.iss
echo begin >> scripts\installer_complete.iss
echo   // Check for Python >> scripts\installer_complete.iss
echo   if not IsPythonInstalled() then >> scripts\installer_complete.iss
echo   begin >> scripts\installer_complete.iss
echo     MsgBox('Python 3.8 or higher is required to run Handyman KPI System.' + #13#10 + >> scripts\installer_complete.iss
echo            'Please install Python from https://www.python.org/downloads/' + #13#10 + >> scripts\installer_complete.iss
echo            'and make sure to check "Add Python to PATH" during installation.', >> scripts\installer_complete.iss
echo            mbError, MB_OK); >> scripts\installer_complete.iss
echo     Result := False; >> scripts\installer_complete.iss
echo     Exit; >> scripts\installer_complete.iss
echo   end; >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo   Result := True; >> scripts\installer_complete.iss
echo end; >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo // Create browser shortcut after installation >> scripts\installer_complete.iss
echo procedure CreateBrowserShortcut(); >> scripts\installer_complete.iss
echo var >> scripts\installer_complete.iss
echo   DesktopPath: String; >> scripts\installer_complete.iss
echo   ShortcutPath: String; >> scripts\installer_complete.iss
echo begin >> scripts\installer_complete.iss
echo   DesktopPath := ExpandConstant('{userdesktop}'); >> scripts\installer_complete.iss
echo   ShortcutPath := DesktopPath + '\' + ExpandConstant('{#MyAppName}') + ' (Browser).url'; >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss
echo   if not FileExists(ShortcutPath) then >> scripts\installer_complete.iss
echo   begin >> scripts\installer_complete.iss
echo     SaveStringToFile(ShortcutPath, '[InternetShortcut]' + #13#10 + 'URL=http://localhost:5000' + #13#10 + 'IconIndex=0', False); >> scripts\installer_complete.iss
echo   end; >> scripts\installer_complete.iss
echo end; >> scripts\installer_complete.iss
echo. >> scripts\installer_complete.iss

echo // Create additional shortcuts or perform other tasks after installation >> scripts\installer_complete.iss
echo procedure CurStepChanged(CurStep: TSetupStep); >> scripts\installer_complete.iss
echo begin >> scripts\installer_complete.iss
echo   if CurStep = ssPostInstall then >> scripts\installer_complete.iss
echo   begin >> scripts\installer_complete.iss
echo     CreateBrowserShortcut(); >> scripts\installer_complete.iss
echo   end; >> scripts\installer_complete.iss
echo end; >> scripts\installer_complete.iss

echo.
echo =======================================================
echo Building complete installer...
echo =======================================================
echo.

:: Build the installer
echo Building installer using %ISCC_PATH%...
"%ISCC_PATH%" "scripts\installer_complete.iss"
if %errorlevel% neq 0 (
    echo ERROR: Failed to build installer.
    echo Check the Inno Setup compiler output for errors.
    echo.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo Installer build complete!
echo =======================================================
echo Installer is located in: installer\output\handyman-kpi-system-setup.exe
echo.

:: Create a copy with date for version tracking
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=!dt:~0,4!"
set "MM=!dt:~4,2!"
set "DD=!dt:~6,2!"
set "date_stamp=!YYYY!!MM!!DD!"

copy "installer\output\handyman-kpi-system-setup.exe" "installer\output\handyman-kpi-system-setup-!date_stamp!.exe" >nul
if %errorlevel% equ 0 (
    echo Created dated backup copy: installer\output\handyman-kpi-system-setup-!date_stamp!.exe
)

pause