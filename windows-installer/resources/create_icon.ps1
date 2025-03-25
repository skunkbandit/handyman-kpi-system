
# PowerShell script to create a basic icon file from shell32.dll
$iconFile = [System.IO.Path]::Combine($PSScriptRoot, "icon.ico")

# Create a simple icon file
Add-Type -AssemblyName System.Drawing
$iconImage = New-Object System.Drawing.Bitmap(32, 32)
$iconGraphics = [System.Drawing.Graphics]::FromImage($iconImage)
$iconGraphics.Clear([System.Drawing.Color]::Blue)

# Draw a simple geometric pattern to represent a KPI dashboard
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::White, 2)

# Draw a simple bar chart pattern
$iconGraphics.FillRectangle($brush, 5, 20, 5, 8)
$iconGraphics.FillRectangle($brush, 12, 15, 5, 13)
$iconGraphics.FillRectangle($brush, 19, 10, 5, 18)

# Save to ico file
$iconImage.Save($iconFile, [System.Drawing.Imaging.ImageFormat]::Icon)

# Clean up resources
$iconGraphics.Dispose()
$iconImage.Dispose()
$brush.Dispose()
$pen.Dispose()

Write-Host "Icon created at $iconFile"
