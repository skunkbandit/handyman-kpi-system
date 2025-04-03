; Handyman KPI System Installer Script
; Created with Inno Setup 6.2.0

#define MyAppName "Handyman KPI System"
#define MyAppVersion "1.2.0"
#define MyAppPublisher "Handyman Solutions"
#define MyAppURL "https://github.com/skunkbandit/handyman-kpi-system"
#define MyAppExeName "handyman_kpi_launcher_detached.py"

[Setup]
; Basic installer settings
AppId={{C65B49B8-8334-4EDF-821A-AE099B5B5D64}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Compression settings
Compression=lzma2
SolidCompression=yes
; Installer appearance and behavior
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes
; Output settings
OutputDir=installer\output
OutputBaseFilename=handyman-kpi-system-setup
SetupIconFile=resources\logo.ico
UninstallDisplayIcon={app}\resources\logo.ico
; Privileges and compatibility
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
; Other settings
UsePreviousAppDir=yes
UsePreviousGroup=yes
ChangesEnvironment=yes
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application files
Source: "kpi-system\*"; DestDir: "{app}\kpi-system"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "handyman_kpi_launcher_detached.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "initialize_database.py"; DestDir: "{app}"; Flags: ignoreversion

; WeasyPrint wheels and dependencies
Source: "wheels\*"; DestDir: "{app}\wheels"; Flags: ignoreversion createallsubdirs
Source: "installers\gtk3-runtime-installer.exe"; DestDir: "{app}\installers"; Flags: ignoreversion
Source: "scripts\install_weasyprint.bat"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "scripts\create_shortcuts.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion

; License and documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Create directories with proper permissions
Name: "{localappdata}\{#MyAppName}"; Permissions: users-modify
Name: "{localappdata}\{#MyAppName}\logs"; Permissions: users-modify
Name: "{localappdata}\{#MyAppName}\database"; Permissions: users-modify
Name: "{localappdata}\{#MyAppName}\config"; Permissions: users-modify

[Icons]
; Create start menu and desktop shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\resources\logo.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\resources\logo.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; IconFilename: "{app}\resources\logo.ico"; Tasks: quicklaunchicon

[Run]
; Post-installation tasks
Filename: "{app}\scripts\install_weasyprint.bat"; Description: "Installing WeasyPrint..."; WorkingDir: "{app}"; Flags: runhidden waituntilterminated
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\scripts\create_shortcuts.ps1"""; Description: "Creating desktop shortcuts..."; WorkingDir: "{app}"; Flags: runhidden waituntilterminated
Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\initialize_database.py"""; Description: "Initializing database..."; WorkingDir: "{app}"; Flags: runhidden waituntilterminated
Filename: "{autopf}\Python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Store installation path in registry
Root: HKLM; Subkey: "SOFTWARE\{#MyAppName}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "SOFTWARE\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[UninstallDelete]
; Clean up files during uninstall
Type: files; Name: "{userdesktop}\{#MyAppName} (Browser).url"
Type: dirifempty; Name: "{app}"

[Code]
// Check if Python 3.8+ is installed
function IsPythonInstalled(): Boolean;
var
  PythonPath: String;
  ResultCode: Integer;
begin
  // Try to find Python executable
  Result := False;
  
  // Check for Python in PATH
  if Exec('where', 'python', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
    begin
      Result := True;
      Exit;
    end;
  end;
  
  // Check common installation locations
  if FileExists(ExpandConstant('{autopf}\Python\python.exe')) then
  begin
    Result := True;
    Exit;
  end;
  
  if FileExists(ExpandConstant('{autopf}\Python39\python.exe')) then
  begin
    Result := True;
    Exit;
  end;
  
  if FileExists(ExpandConstant('{autopf}\Python310\python.exe')) then
  begin
    Result := True;
    Exit;
  end;
end;

// Pre-installation check
function InitializeSetup(): Boolean;
begin
  // Check for Python
  if not IsPythonInstalled() then
  begin
    MsgBox('Python 3.8 or higher is required to run Handyman KPI System.' + #13#10 +
           'Please install Python from https://www.python.org/downloads/' + #13#10 +
           'and make sure to check "Add Python to PATH" during installation.',
           mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  Result := True;
end;

// Create browser shortcut after installation
procedure CreateBrowserShortcut();
var
  DesktopPath: String;
  ShortcutPath: String;
begin
  DesktopPath := ExpandConstant('{userdesktop}');
  ShortcutPath := DesktopPath + '\' + ExpandConstant('{#MyAppName}') + ' (Browser).url';
  
  if not FileExists(ShortcutPath) then
  begin
    SaveStringToFile(ShortcutPath, '[InternetShortcut]' + #13#10 + 'URL=http://localhost:5000' + #13#10 + 'IconIndex=0', False);
  end;
end;

// Create additional shortcuts or perform other tasks after installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    CreateBrowserShortcut();
  end;
end;
