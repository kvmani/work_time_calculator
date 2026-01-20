# Work Time Calculator

A simple Windows desktop app (Tkinter GUI) that helps calculate work time. This repo includes a reproducible, novice-friendly workflow to run from source, build a standalone EXE, and package a professional Windows installer.

## Prerequisites
- Windows 10/11.
- Python 3.8+ (64-bit). Tkinter is part of the standard Windows Python installer.
- Optional: Inno Setup 6 (offline installer) to build the setup EXE.
- Optional: an app icon at assets\app.ico (multi-size .ico).

Quick Tkinter check:
    python -m tkinter

## Quick run from source
1) Open Command Prompt in this folder.
2) Run the app:
    python work_time_calculator.py

If you want a virtual environment first:
    python -m venv .venv
    .venv\Scripts\activate
    python work_time_calculator.py

## Build EXE with PyInstaller (onedir recommended)
The simplest path is to run:
    build_installer.bat

Manual build (recommended onedir):
    .venv\Scripts\activate
    pip install -r requirements.txt
    pyinstaller --noconfirm --clean --windowed --name WorkTimeCalculator --icon assets\app.ico --version-file version_info.txt work_time_calculator.py

Notes:
- If you do not have assets\app.ico, remove the --icon flag.
- If you do not want version metadata, remove the --version-file flag.
- Output: dist\WorkTimeCalculator\WorkTimeCalculator.exe

Onefile alternative (single EXE, slower start, more AV false positives):
    pyinstaller --noconfirm --clean --windowed --onefile --name WorkTimeCalculator work_time_calculator.py

## Create an installer with Inno Setup
1) Install Inno Setup 6 offline (download on a connected machine, transfer the installer, then run it on the air-gapped PC).
2) Ensure installer\LICENSE.txt contains the full GPLv3 or LGPLv3 text (placeholder is provided).
3) Compile the installer using either method:
   - GUI: open installer\installer.iss in the Inno Setup Compiler and click Compile.
   - CLI:
       ISCC.exe installer\installer.iss

Output: output\WorkTimeCalculatorSetup.exe

## Air-gapped workflows
### Using an internal PyPI mirror
If your environment has a mirror, install dependencies from it:
    pip install -r requirements.txt --index-url http://YOUR-MIRROR/simple --trusted-host YOUR-MIRROR

You can also configure pip to always use the mirror (pip.ini), then run:
    pip install -r requirements.txt

### Offline wheel download and transfer
On a connected machine:
    pip download -r requirements.txt -d wheels
Copy the wheels folder to the air-gapped PC, then:
    pip install --no-index --find-links wheels -r requirements.txt

### Offline Inno Setup transfer
Download the Inno Setup installer on a connected machine, copy it to the air-gapped PC, and run the installer locally. No internet access is required after transfer.

## Where outputs appear
- dist\WorkTimeCalculator\WorkTimeCalculator.exe (PyInstaller onedir build)
- build\ (PyInstaller temporary files)
- output\WorkTimeCalculatorSetup.exe (Inno Setup installer)

## How to change icon, name, and version
- Icon: replace assets\app.ico with a multi-size .ico and rebuild.
- EXE metadata: edit version_info.txt (CompanyName, FileVersion, ProductVersion, etc.).
- Installer metadata: edit installer\installer.iss (AppId, AppName, AppVersion, AppPublisher).
  Generate a new AppId GUID in PowerShell:
    [guid]::NewGuid()
- If you rename the app, update the --name value in build_installer.bat and the AppExeName in installer\installer.iss.

## Troubleshooting
- Missing Tkinter: run python -m tkinter. If it fails, reinstall Python and ensure Tcl/Tk is included.
- App launches then closes: run the EXE from Command Prompt or rebuild without --windowed to see errors.
- Antivirus quarantines onefile EXE: prefer onedir builds and add an internal allowlist.
- Inno Setup not found: locate ISCC.exe (common paths: C:\Program Files (x86)\Inno Setup 6\ISCC.exe or C:\Program Files\Inno Setup 6\ISCC.exe) or use the GUI compiler.
- Icon not showing: ensure the .ico has multiple sizes; rebuild and restart Explorer to refresh icon cache.

## Optional: code signing
If your organization supports code signing, sign WorkTimeCalculator.exe and the installer EXE for a more professional experience.
