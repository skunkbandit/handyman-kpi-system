@echo off
setlocal EnableDelayedExpansion

echo =======================================================
echo Building Handyman KPI System Installer - FIXED VERSION
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

:: Download wheel files if needed and if script exists
set "WHEEL_COUNT=0"
for %%F in (wheels\*.whl) do set /a WHEEL_COUNT+=1

if exist "scripts\download_wheels.py" (
    if %WHEEL_COUNT% equ 0 (
        echo No wheel files found. Checking if we can download dependencies...
        python scripts\download_wheels.py
        if %errorlevel% neq 0 (
            echo WARNING: Failed to download wheel files.
            echo The installer will still build but may not include all dependencies.
            echo.
        )
    ) else (
        echo Found %WHEEL_COUNT% wheel files in the 'wheels' directory.
    )
)

:: Check for GTK3 Runtime installer
if not exist "installers\gtk3-runtime-installer.exe" (
    echo GTK3 Runtime installer not found. Attempting to download...
    python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe', 'installers\\gtk3-runtime-installer.exe')"
    if %errorlevel% neq 0 (
        echo WARNING: Failed to download GTK3 Runtime installer.
        echo The installer will still build but may not include GTK3 Runtime.
        echo.
    )
)

:: Test WeasyPrint installation if the test script exists
if exist "scripts\test_weasyprint.py" (
    echo Testing WeasyPrint installation...
    python scripts\test_weasyprint.py
    if %errorlevel% neq 0 (
        echo WARNING: WeasyPrint test failed. The installer may not be able to install WeasyPrint correctly.
        echo You can continue building the installer, but PDF generation may not work.
        echo.
        choice /C YN /M "Do you want to continue building the installer anyway?"
        if !errorlevel! equ 2 (
            echo Build cancelled.
            exit /b 1
        )
    )
)

:: Create a temporary configuration file to define which directories exist
echo Creating configuration file for installer...
> scripts\config.iss echo ; Auto-generated configuration for installer

:: Check which optional directories and files exist
if exist "kpi-system" (
    echo #define INCLUDE_KPI_SYSTEM >> scripts\config.iss
    echo Found kpi-system directory, will include in installer
)

if exist "resources" (
    echo #define INCLUDE_RESOURCES >> scripts\config.iss
    echo Found resources directory, will include in installer
)

if exist "wheels" (
    if %WHEEL_COUNT% gtr 0 (
        echo #define INCLUDE_WHEELS >> scripts\config.iss
        echo Found wheel files, will include in installer
    )
)

if exist "installers\gtk3-runtime-installer.exe" (
    echo #define INCLUDE_INSTALLERS >> scripts\config.iss
    echo Found GTK3 runtime installer, will include in installer
)

if exist "scripts\install_weasyprint.bat" (
    if exist "scripts\create_shortcuts.ps1" (
        echo #define INCLUDE_SCRIPTS >> scripts\config.iss
        echo Found script files, will include in installer
    )
)

if exist "README.md" (
    echo #define INCLUDE_README >> scripts\config.iss
    echo Found README.md, will include in installer
)

if exist "LICENSE" (
    echo #define INCLUDE_LICENSE >> scripts\config.iss
    echo Found LICENSE file, will include in installer
)

:: Create the updated installer script with proper paths
echo Creating fixed installer script...

echo ; Fixed Handyman KPI System Installer Script > scripts\installer_fixed.iss
echo ; Created with paths adjusted for compatibility >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo #define MyAppName "Handyman KPI System" >> scripts\installer_fixed.iss
echo #define MyAppVersion "1.2.0" >> scripts\installer_fixed.iss
echo #define MyAppPublisher "Handyman Solutions" >> scripts\installer_fixed.iss
echo #define MyAppURL "https://github.com/skunkbandit/handyman-kpi-system" >> scripts\installer_fixed.iss
echo #define MyAppExeName "handyman_kpi_launcher_detached.py" >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo [Setup] >> scripts\installer_fixed.iss
echo ; Basic installer settings >> scripts\installer_fixed.iss
echo AppId={{C65B49B8-8334-4EDF-821A-AE099B5B5D64} >> scripts\installer_fixed.iss
echo AppName={#MyAppName} >> scripts\installer_fixed.iss
echo AppVersion={#MyAppVersion} >> scripts\installer_fixed.iss
echo AppPublisher={#MyAppPublisher} >> scripts\installer_fixed.iss
echo AppPublisherURL={#MyAppURL} >> scripts\installer_fixed.iss
echo AppSupportURL={#MyAppURL} >> scripts\installer_fixed.iss
echo AppUpdatesURL={#MyAppURL} >> scripts\installer_fixed.iss
echo DefaultDirName={autopf}\{#MyAppName} >> scripts\installer_fixed.iss
echo DefaultGroupName={#MyAppName} >> scripts\installer_fixed.iss
echo AllowNoIcons=yes >> scripts\installer_fixed.iss
echo ; Compression settings >> scripts\installer_fixed.iss
echo Compression=lzma2 >> scripts\installer_fixed.iss
echo SolidCompression=yes >> scripts\installer_fixed.iss
echo ; Installer appearance and behavior >> scripts\installer_fixed.iss
echo WizardStyle=modern >> scripts\installer_fixed.iss
echo DisableWelcomePage=no >> scripts\installer_fixed.iss
echo DisableDirPage=no >> scripts\installer_fixed.iss
echo DisableProgramGroupPage=yes >> scripts\installer_fixed.iss
echo ; Output settings >> scripts\installer_fixed.iss
echo OutputDir=..\installer\output >> scripts\installer_fixed.iss
echo OutputBaseFilename=handyman-kpi-system-setup >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

:: Add icon references only if resources exist
if exist "resources\logo.ico" (
    echo SetupIconFile=..\resources\logo.ico >> scripts\installer_fixed.iss
    echo UninstallDisplayIcon={app}\resources\logo.ico >> scripts\installer_fixed.iss
)

echo ; Privileges and compatibility >> scripts\installer_fixed.iss
echo PrivilegesRequired=admin >> scripts\installer_fixed.iss
echo ArchitecturesInstallIn64BitMode=x64 >> scripts\installer_fixed.iss
echo ; Other settings >> scripts\installer_fixed.iss
echo UsePreviousAppDir=yes >> scripts\installer_fixed.iss
echo UsePreviousGroup=yes >> scripts\installer_fixed.iss
echo ChangesEnvironment=yes >> scripts\installer_fixed.iss
echo CloseApplications=yes >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo [Languages] >> scripts\installer_fixed.iss
echo Name: "english"; MessagesFile: "compiler:Default.isl" >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo [Tasks] >> scripts\installer_fixed.iss
echo Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked >> scripts\installer_fixed.iss
echo Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo [Files] >> scripts\installer_fixed.iss
echo ; Main application files - only include what we know exists >> scripts\installer_fixed.iss
echo Source: "..\handyman_kpi_launcher_detached.py"; DestDir: "{app}"; Flags: ignoreversion >> scripts\installer_fixed.iss
echo Source: "..\initialize_database.py"; DestDir: "{app}"; Flags: ignoreversion >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo ; Include KPI system directory if it exists >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_KPI_SYSTEM >> scripts\installer_fixed.iss
echo Source: "..\kpi-system\*"; DestDir: "{app}\kpi-system"; Flags: ignoreversion recursesubdirs createallsubdirs >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo ; Include resources directory if it exists >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_RESOURCES >> scripts\installer_fixed.iss
echo Source: "..\resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo ; Include wheels directory if it exists >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_WHEELS >> scripts\installer_fixed.iss
echo Source: "..\wheels\*"; DestDir: "{app}\wheels"; Flags: ignoreversion createallsubdirs >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo ; Include installers directory if it exists >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_INSTALLERS >> scripts\installer_fixed.iss
echo Source: "..\installers\gtk3-runtime-installer.exe"; DestDir: "{app}\installers"; Flags: ignoreversion >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo ; Include scripts if they exist >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_SCRIPTS >> scripts\installer_fixed.iss
echo Source: "..\scripts\install_weasyprint.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion >> scripts\installer_fixed.iss
echo Source: "..\scripts\create_shortcuts.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo ; Include README and LICENSE if they exist >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_README >> scripts\installer_fixed.iss
echo Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo #ifdef INCLUDE_LICENSE >> scripts\installer_fixed.iss
echo Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo [Dirs] >> scripts\installer_fixed.iss
echo ; Create directories with proper permissions >> scripts\installer_fixed.iss
echo Name: "{localappdata}\{#MyAppName}"; Permissions: users-modify >> scripts\installer_fixed.iss
echo Name: "{localappdata}\{#MyAppName}\logs"; Permissions: users-modify >> scripts\installer_fixed.iss
echo Name: "{localappdata}\{#MyAppName}\database"; Permissions: users-modify >> scripts\installer_fixed.iss
echo Name: "{localappdata}\{#MyAppName}\config"; Permissions: users-modify >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo [Icons] >> scripts\installer_fixed.iss
echo ; Create start menu shortcuts >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_RESOURCES >> scripts\installer_fixed.iss
echo Name: "{group}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\resources\logo.ico" >> scripts\installer_fixed.iss
echo #else >> scripts\installer_fixed.iss
echo Name: "{group}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}" >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}" >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo ; Desktop icon conditionally based on task selection >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_RESOURCES >> scripts\installer_fixed.iss
echo Name: "{autodesktop}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\resources\logo.ico"; Tasks: desktopicon >> scripts\installer_fixed.iss
echo #else >> scripts\installer_fixed.iss
echo Name: "{autodesktop}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; Tasks: desktopicon >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo ; Quick Launch icon only if task selected >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_RESOURCES >> scripts\installer_fixed.iss
echo Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\resources\logo.ico"; Tasks: quicklaunchicon >> scripts\installer_fixed.iss
echo #else >> scripts\installer_fixed.iss
echo Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; Tasks: quicklaunchicon >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo [Run] >> scripts\installer_fixed.iss
echo ; Only include scripts if they exist >> scripts\installer_fixed.iss
echo #ifdef INCLUDE_SCRIPTS >> scripts\installer_fixed.iss
echo Filename: "{app}\scripts\install_weasyprint.bat"; WorkingDir: "{app}"; Flags: runhidden waituntilterminated >> scripts\installer_fixed.iss
echo Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\scripts\create_shortcuts.ps1"""; WorkingDir: "{app}"; Flags: runhidden waituntilterminated >> scripts\installer_fixed.iss
echo #endif >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\initialize_database.py"""; WorkingDir: "{app}"; Flags: runhidden waituntilterminated >> scripts\installer_fixed.iss
echo Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo [Registry] >> scripts\installer_fixed.iss
echo ; Store installation path in registry >> scripts\installer_fixed.iss
echo Root: HKLM; Subkey: "SOFTWARE\{#MyAppName}"; Flags: uninsdeletekey >> scripts\installer_fixed.iss
echo Root: HKLM; Subkey: "SOFTWARE\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}" >> scripts\installer_fixed.iss
echo Root: HKLM; Subkey: "SOFTWARE\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}" >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo [UninstallDelete] >> scripts\installer_fixed.iss
echo ; Clean up files during uninstall >> scripts\installer_fixed.iss
echo Type: files; Name: "{userdesktop}\{#MyAppName} (Browser).url" >> scripts\installer_fixed.iss
echo Type: dirifempty; Name: "{app}" >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo [Code] >> scripts\installer_fixed.iss
echo // Check if Python 3.8+ is installed >> scripts\installer_fixed.iss
echo function IsPythonInstalled(): Boolean; >> scripts\installer_fixed.iss
echo var >> scripts\installer_fixed.iss
echo   PythonPath: String; >> scripts\installer_fixed.iss
echo   ResultCode: Integer; >> scripts\installer_fixed.iss
echo begin >> scripts\installer_fixed.iss
echo   // Try to find Python executable >> scripts\installer_fixed.iss
echo   Result := False; >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo   // Check for Python in PATH >> scripts\installer_fixed.iss
echo   if Exec('where', 'python', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then >> scripts\installer_fixed.iss
echo   begin >> scripts\installer_fixed.iss
echo     if ResultCode = 0 then >> scripts\installer_fixed.iss
echo     begin >> scripts\installer_fixed.iss
echo       Result := True; >> scripts\installer_fixed.iss
echo       Exit; >> scripts\installer_fixed.iss
echo     end; >> scripts\installer_fixed.iss
echo   end; >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo   // Check common installation locations >> scripts\installer_fixed.iss
echo   if FileExists(ExpandConstant('{autopf}\Python\python.exe')) then >> scripts\installer_fixed.iss
echo   begin >> scripts\installer_fixed.iss
echo     Result := True; >> scripts\installer_fixed.iss
echo     Exit; >> scripts\installer_fixed.iss
echo   end; >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo   if FileExists(ExpandConstant('{autopf}\Python39\python.exe')) then >> scripts\installer_fixed.iss
echo   begin >> scripts\installer_fixed.iss
echo     Result := True; >> scripts\installer_fixed.iss
echo     Exit; >> scripts\installer_fixed.iss
echo   end; >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo   if FileExists(ExpandConstant('{autopf}\Python310\python.exe')) then >> scripts\installer_fixed.iss
echo   begin >> scripts\installer_fixed.iss
echo     Result := True; >> scripts\installer_fixed.iss
echo     Exit; >> scripts\installer_fixed.iss
echo   end; >> scripts\installer_fixed.iss
echo end; >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo // Pre-installation check >> scripts\installer_fixed.iss
echo function InitializeSetup(): Boolean; >> scripts\installer_fixed.iss
echo begin >> scripts\installer_fixed.iss
echo   // Check for Python >> scripts\installer_fixed.iss
echo   if not IsPythonInstalled() then >> scripts\installer_fixed.iss
echo   begin >> scripts\installer_fixed.iss
echo     MsgBox('Python 3.8 or higher is required to run Handyman KPI System.' + #13#10 + >> scripts\installer_fixed.iss
echo            'Please install Python from https://www.python.org/downloads/' + #13#10 + >> scripts\installer_fixed.iss
echo            'and make sure to check "Add Python to PATH" during installation.', >> scripts\installer_fixed.iss
echo            mbError, MB_OK); >> scripts\installer_fixed.iss
echo     Result := False; >> scripts\installer_fixed.iss
echo     Exit; >> scripts\installer_fixed.iss
echo   end; >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo   Result := True; >> scripts\installer_fixed.iss
echo end; >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo // Create browser shortcut after installation >> scripts\installer_fixed.iss
echo procedure CreateBrowserShortcut(); >> scripts\installer_fixed.iss
echo var >> scripts\installer_fixed.iss
echo   DesktopPath: String; >> scripts\installer_fixed.iss
echo   ShortcutPath: String; >> scripts\installer_fixed.iss
echo begin >> scripts\installer_fixed.iss
echo   DesktopPath := ExpandConstant('{userdesktop}'); >> scripts\installer_fixed.iss
echo   ShortcutPath := DesktopPath + '\' + ExpandConstant('{#MyAppName}') + ' (Browser).url'; >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss
echo   if not FileExists(ShortcutPath) then >> scripts\installer_fixed.iss
echo   begin >> scripts\installer_fixed.iss
echo     SaveStringToFile(ShortcutPath, '[InternetShortcut]' + #13#10 + 'URL=http://localhost:5000' + #13#10 + 'IconIndex=0', False); >> scripts\installer_fixed.iss
echo   end; >> scripts\installer_fixed.iss
echo end; >> scripts\installer_fixed.iss
echo. >> scripts\installer_fixed.iss

echo // Create additional shortcuts or perform other tasks after installation >> scripts\installer_fixed.iss
echo procedure CurStepChanged(CurStep: TSetupStep); >> scripts\installer_fixed.iss
echo begin >> scripts\installer_fixed.iss
echo   if CurStep = ssPostInstall then >> scripts\installer_fixed.iss
echo   begin >> scripts\installer_fixed.iss
echo     CreateBrowserShortcut(); >> scripts\installer_fixed.iss
echo   end; >> scripts\installer_fixed.iss
echo end; >> scripts\installer_fixed.iss

echo.
echo =======================================================
echo Creating and building installer...
echo =======================================================
echo.

:: Create combined script
copy /y scripts\config.iss + scripts\installer_fixed.iss scripts\installer_combined.iss
if %errorlevel% neq 0 (
    echo ERROR: Failed to create combined installer script.
    echo.
    pause
    exit /b 1
)

:: Build the installer
echo Building installer using %ISCC_PATH%...
"%ISCC_PATH%" "scripts\installer_combined.iss"
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