# Work Time Calculator

Cross-platform Tkinter desktop app that calculates daily work time from multiple intervals. Provides live totals and milestone projections. Supports Windows and Linux (including WSL with a GUI).

## Features
- Multiple intervals with optional open interval (end blank uses current time).
- Validates overlaps and same-day order (no cross-midnight).
- Editable daily target duration (default 08:30:00).
- Live clock, totals, progress bar, and milestone projections.
- Copy summary to clipboard for reporting.

## Usage reference
Inputs:
- Date: today (read-only).
- Target: expected daily duration. Formats: H, H:MM, H:MM:SS (example: 8:30 or 08:30:00).
- Start: interval start time (example: 9, 09:15, 9:15 am, 21:07).
- End: interval end time. Leave blank for an open interval.
- Select: checkbox used by Remove/End Now actions.

Rules:
- End must be after Start on the same day (no cross-midnight).
- Intervals may not overlap.
- Only one open interval is allowed.

Outputs:
- Worked: total time across intervals (open interval uses current time).
- Remaining: time left to reach Target (never below 00:00:00).
- Overtime: time beyond Target (never below 00:00:00).
- Progress: percent of Target completed.
- Milestone: projected clock time to reach Target or the next whole overtime hour.
- Notes: per-row validation messages.

## Prerequisites
- Python 3.8+ with Tkinter.
- Windows 10/11 or a Linux desktop environment.
- Optional: Inno Setup 6 (Windows only) to build the installer.
- Optional: an app icon at `assets/app.ico` (multi-size .ico).

Quick Tkinter check:
- Windows: `py -m tkinter`
- Linux: `python3 -m tkinter`

## Run from source
Windows:
```
python work_time_calculator.py
```

Linux:
```
python3 work_time_calculator.py
```

Virtual environment (optional):
```
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux:
source .venv/bin/activate
python work_time_calculator.py
```

## Linux/WSL setup notes
- Install Tk from your OS package manager (not pip):
  - Ubuntu/Debian: `sudo apt-get install -y python3-tk`
  - Fedora: `sudo dnf install -y python3-tkinter`
  - Arch: `sudo pacman -S tk`
- In WSL, enable WSLg (Windows 11) or run an X server and set `DISPLAY`.

## Build EXE with PyInstaller (Windows)
The simplest path is to run:
```
build_installer.bat
```

Manual build (onedir recommended):
```
.venv\Scripts\activate
pip install -r requirements.txt
pyinstaller --noconfirm --clean --windowed --name WorkTimeCalculator --icon assets\app.ico --version-file version_info.txt work_time_calculator.py
```

Notes:
- If you do not have `assets/app.ico`, remove the `--icon` flag.
- If you do not want version metadata, remove the `--version-file` flag.
- Output: `dist/WorkTimeCalculator/WorkTimeCalculator.exe`

Onefile alternative (single EXE, slower start, more AV false positives):
```
pyinstaller --noconfirm --clean --windowed --onefile --name WorkTimeCalculator work_time_calculator.py
```

## Create an installer with Inno Setup (Windows)
1) Install Inno Setup 6 offline (download on a connected machine, transfer the installer, then run it on the air-gapped PC).
2) Ensure `installer/LICENSE.txt` contains the full GPLv3 or LGPLv3 text (placeholder is provided).
3) Compile the installer using either method:
   - GUI: open `installer/installer.iss` in the Inno Setup Compiler and click Compile.
   - CLI:
     ```
     ISCC.exe installer/installer.iss
     ```

Output: `output/WorkTimeCalculatorSetup.exe`

## Air-gapped workflows
### Using an internal PyPI mirror
If your environment has a mirror, install dependencies from it:
```
pip install -r requirements.txt --index-url http://YOUR-MIRROR/simple --trusted-host YOUR-MIRROR
```

You can also configure pip to always use the mirror (pip.ini), then run:
```
pip install -r requirements.txt
```

### Offline wheel download and transfer
On a connected machine:
```
pip download -r requirements.txt -d wheels
```
Copy the `wheels` folder to the air-gapped PC, then:
```
pip install --no-index --find-links wheels -r requirements.txt
```

### Offline Inno Setup transfer
Download the Inno Setup installer on a connected machine, copy it to the air-gapped PC, and run the installer locally. No internet access is required after transfer.

## Where outputs appear
- `dist/WorkTimeCalculator/WorkTimeCalculator.exe` (PyInstaller onedir build)
- `build/` (PyInstaller temporary files)
- `output/WorkTimeCalculatorSetup.exe` (Inno Setup installer)

## How to change icon, name, and version
- Icon: replace `assets/app.ico` with a multi-size .ico and rebuild.
- EXE metadata: edit `version_info.txt` (CompanyName, FileVersion, ProductVersion, etc.).
- Installer metadata: edit `installer/installer.iss` (AppId, AppName, AppVersion, AppPublisher).
  Generate a new AppId GUID in PowerShell:
  ```
  [guid]::NewGuid()
  ```
- If you rename the app, update the `--name` value in `build_installer.bat` and the `AppExeName` in `installer/installer.iss`.

## Troubleshooting
- Missing Tkinter (Linux): install `python3-tk` and verify with `python3 -m tkinter`.
- Tk GUI cannot open on Linux/WSL: ensure a desktop session or WSLg/X server and `DISPLAY` is set.
- App launches then closes: run the EXE from Command Prompt or rebuild without `--windowed` to see errors.
- Antivirus quarantines onefile EXE: prefer onedir builds and add an internal allowlist.
- Inno Setup not found: locate `ISCC.exe` (common paths: `C:\Program Files (x86)\Inno Setup 6\ISCC.exe` or `C:\Program Files\Inno Setup 6\ISCC.exe`) or use the GUI compiler.
- Icon not showing: ensure the .ico has multiple sizes; rebuild and restart Explorer to refresh icon cache.

## Optional: code signing
If your organization supports code signing, sign `WorkTimeCalculator.exe` and the installer EXE for a more professional experience.
