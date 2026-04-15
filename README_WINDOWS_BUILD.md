# Company Tracker Windows Build

## Build on Windows

1. Open this folder in Windows.
2. Run `build_windows.bat` or `build_windows.ps1`.
3. After the build finishes, use:

`dist\CompanyTracker\CompanyTracker.exe`

## Notes

- This uses `PyInstaller`.
- The build script generates `assets/company_tracker.ico` automatically.
- `dday_data.json` is bundled as initial data.
- If you want saved data to persist separately per user, the app should later be changed to store data under `%APPDATA%` instead of next to the script.
