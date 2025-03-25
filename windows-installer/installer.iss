#define MyAppName "Handyman KPI System"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Handyman Solutions"
#define MyAppURL "https://github.com/skunkbandit/handyman-kpi-system"
#define MyAppExeName "run_app.bat"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{B0A7F456-E039-4804-AA15-D3A9082B3F25}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=output
OutputBaseFilename=handyman-kpi-system-setup
; SetupIconFile=resources\icon.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequiredOverridesAllowed=commandline dialog
PrivilegesRequired=lowest
; UninstallDisplayIcon={app}\resources\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Python Embedded Distribution
Source: "python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs
; Application files
Source: "src\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Resources
Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs
; Note: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
