# PowerShell script to create improved desktop shortcuts
# For Handyman KPI System

# Get desktop path
$desktopPath = [Environment]::GetFolderPath("Desktop")

# Find Python and pythonw paths
$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
$pythonwExe = $pythonExe -replace "python.exe", "pythonw.exe"

# Check if pythonw.exe exists
if (-not (Test-Path $pythonwExe)) {
    Write-Output "pythonw.exe not found at: $pythonwExe"
    # Try common installation locations
    $possiblePaths = @(
        "${env:ProgramFiles}\Python\pythonw.exe",
        "${env:ProgramFiles}\Python39\pythonw.exe",
        "${env:ProgramFiles}\Python310\pythonw.exe",
        "${env:ProgramFiles(x86)}\Python\pythonw.exe",
        "${env:ProgramFiles(x86)}\Python39\pythonw.exe",
        "${env:ProgramFiles(x86)}\Python310\pythonw.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $pythonwExe = $path
            Write-Output "Found pythonw.exe at: $pythonwExe"
            break
        }
    }
    
    # If still not found, use python.exe as fallback
    if (-not (Test-Path $pythonwExe)) {
        Write-Output "pythonw.exe not found, using python.exe instead"
        $pythonwExe = $pythonExe
    }
}

# Get installation directory
$installDir = $PSScriptRoot | Split-Path -Parent
$launcherPath = Join-Path -Path $installDir -ChildPath "handyman_kpi_launcher_detached.py"
$iconPath = Join-Path -Path $installDir -ChildPath "resources\logo.ico"

# Create Desktop Shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$desktopPath\Handyman KPI System.lnk")
$Shortcut.TargetPath = $pythonwExe
$Shortcut.Arguments = "`"$launcherPath`""
$Shortcut.WorkingDirectory = $installDir
$Shortcut.IconLocation = $iconPath
$Shortcut.Description = "Handyman KPI System"
$Shortcut.WindowStyle = 7  # Minimized
$Shortcut.Save()

Write-Output "Created main desktop shortcut"

# Create Browser Shortcut
$browserShortcutPath = "$desktopPath\Handyman KPI System (Browser).url"
@"
[InternetShortcut]
URL=http://localhost:5000
IconIndex=0
IconFile=$iconPath
"@ | Out-File $browserShortcutPath -Encoding ascii

Write-Output "Created browser shortcut"
Write-Output "Desktop shortcuts created successfully!"