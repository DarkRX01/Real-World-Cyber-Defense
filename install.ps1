# Cyber Defense - Silent Installation Script
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "SilentlyContinue"
$ProgressPreference = "SilentlyContinue"

# Hide terminal window
$null = [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")

# Check Python
try {
    python --version | Out-Null
} catch {
    Write-Host "Downloading Python 3.11..."
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    
    $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $pythonPath = "$env:TEMP\python-setup.exe"
    
    (New-Object System.Net.WebClient).DownloadFile($pythonUrl, $pythonPath)
    
    Write-Host "Installing Python (this may take a minute)..."
    & $pythonPath /quiet InstallAllUsers=1 PrependPath=1 | Out-Null
    
    Start-Sleep -Seconds 5
    Remove-Item $pythonPath -Force -ErrorAction SilentlyContinue
    
    Write-Host "Python installed successfully!"
}

# Install packages silently
Write-Host "Setting up application..."
python -m pip install --quiet --no-cache-dir PyQt5 requests pyperclip | Out-Null

Write-Host "Launching Cyber Defense..."
& python app_main.py
