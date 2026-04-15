$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
    py -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt
python .\scripts\generate_icon.py

pyinstaller `
  --noconfirm `
  --clean `
  --windowed `
  --name "CompanyTracker" `
  --icon "assets\company_tracker.ico" `
  --add-data "assets;assets" `
  --add-data "dday_data.json;." `
  app.py

Write-Host ""
Write-Host "Build complete: dist\CompanyTracker\CompanyTracker.exe"
