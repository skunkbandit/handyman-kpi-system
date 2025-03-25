#define MyAppName "Handyman KPI System"
#define MyAppVersion "{{VERSION}}"
#define MyAppPublisher "Handyman KPI"
#define MyAppURL "https://github.com/skunkbandit/handyman-kpi-system"
#define MyAppExeName "handyman_kpi_launcher.exe"
#define MyAppAssocName "Handyman KPI System"
#define MyAppAssocExt ".kpi"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

#define SourceDir "{{APP_DIR}}"
#define PythonDir "{{PYTHON_DIR}}"
#define OutputDir "{{OUTPUT_DIR}}"

[Setup]
AppId={{5C3D7B7C-30E4-488F-856A-40E77E2F88D4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile={#SourceDir}\LICENSE
OutputDir={#OutputDir}
OutputBaseFilename=handyman-kpi-system-setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
SetupIconFile={#SourceDir}\resources\icons\handyman_kpi.ico
UninstallDisplayIcon={app}\resources\icons\handyman_kpi.ico
WizardSmallImageFile={#SourceDir}\resources\images\wizard-image.bmp
WizardImageFile={#SourceDir}\resources\images\wizard-image-large.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Python embedded distribution
Source: "{#PythonDir}\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs
; Application files
Source: "{#SourceDir}\*"; Excludes: "*.git,.gitignore,.vscode,tests,*.pyc,__pycache__"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\resources\icons\handyman_kpi.ico"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".kpi"; ValueData: ""

[UninstallRun]
Filename: "{cmd}"; Parameters: "/c rd /s /q ""{app}"""; Flags: runhidden

[Code]
// Custom functions and procedures for the installation process

// Check if Python is already installed
function CheckPythonInstallation(): Boolean;
begin
  Result := True;
  // No need to check for Python since we're using embedded distribution
end;

// Check system requirements
function CheckSystemRequirements(): Boolean;
var
  OSVersion: TWindowsVersion;
begin
  Result := True;
  
  // Check Windows version
  GetWindowsVersionEx(OSVersion);
  if OSVersion.Major < 10 then
  begin
    MsgBox('This application requires Windows 10 or later.', mbError, MB_OK);
    Result := False;
  end;
  
  // Check for .NET Framework 4.7.2 or later (if needed)
  // ...
  
  // Check for required Windows features (if needed)
  // ...
end;

// Initialize the setup process
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check system requirements
  if not CheckSystemRequirements() then
  begin
    Result := False;
    Exit;
  end;
  
  // Additional initialization steps (if needed)
  // ...
end;

// Initialize the wizard
procedure InitializeWizard();
begin
  // Additional wizard customization (if needed)
  // ...
end;

// Before installation
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  
  // Additional preparation steps (if needed)
  // ...
end;

// After installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Additional post-installation steps (if needed)
    // ...
  end;
end;

// Before uninstallation
function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  // Additional uninstallation preparation steps (if needed)
  // ...
end;

// After uninstallation
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Additional post-uninstallation steps (if needed)
    // ...
  end;
end;