@echo off
setlocal

cd /d "%~dp0"

if not exist .venv (
    py -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\generate_icon.py

pyinstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name "CompanyTracker" ^
  --icon "assets\company_tracker.ico" ^
  --add-data "assets;assets" ^
  --add-data "dday_data.json;." ^
  app.py

echo.
echo Build complete: dist\CompanyTracker\CompanyTracker.exe
pause
