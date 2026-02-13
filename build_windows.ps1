param(
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/4] Creating virtual environment"
& $PythonExe -m venv .venv

Write-Host "[2/4] Installing dependencies"
& .\.venv\Scripts\python -m pip install --upgrade pip
& .\.venv\Scripts\python -m pip install -r requirements.txt pyinstaller

Write-Host "[3/4] Building executable"
& .\.venv\Scripts\pyinstaller --noconfirm --onefile --windowed --name InclusiVoice src\main.py

Write-Host "[4/4] Output"
Write-Host "Built executable at dist\InclusiVoice.exe"
