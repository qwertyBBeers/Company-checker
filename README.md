# Company Tracker

Windows desktop interview D-Day tracker built with Python and PyQt6.

This app starts as a compact widget-style window and expands into a detailed view for managing company interview schedules, notes, and related links.

## Features

- Compact widget mode with countdown list
- Expandable detail view for memo, interview info, and links
- Real-time D-Day countdown with seconds
- Drag-and-drop company ordering
- Sort by nearest interview date
- Frameless movable window
- Light/Dark mode toggle
- Local JSON persistence
- Windows `.exe` build script with icon packaging

## Tech Stack

- Python 3.x
- PyQt6
- Local JSON storage
- PyInstaller for Windows packaging

## Project Structure

```text
app.py
requirements.txt
build_windows.bat
build_windows.ps1
README.md
README_WINDOWS_BUILD.md
scripts/
  generate_icon.py
dday_data.example.json
```

## Local Run

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Windows Build

Build a packaged Windows app with:

```powershell
build_windows.bat
```

or

```powershell
.\build_windows.ps1
```

Output:

```text
dist\CompanyTracker\CompanyTracker.exe
```

More packaging notes are in [README_WINDOWS_BUILD.md](README_WINDOWS_BUILD.md).

## Data File

Runtime data is stored in `dday_data.json`.

- `dday_data.json` is ignored by git.
- `dday_data.example.json` is included as a repo-safe sample.

## Recommended Git Upload Flow

```bash
git init
git add .
git status
git commit -m "Initial commit: Company Tracker"
```

Before pushing, check that these are not staged:

- `.venv/`
- `__pycache__/`
- `dist/`
- `build/`
- `assets/`
- `dday_data.json`

## Notes

- The current data file is stored next to the app for simplicity.
- If you later want a more production-like app, move data storage to `%APPDATA%` on Windows.
