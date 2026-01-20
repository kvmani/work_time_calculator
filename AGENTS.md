# AGENTS

Short operational guide for maintaining and packaging this app.

## Project structure
- work_time_calculator.py: Tkinter GUI app.
- requirements.txt: build-time dependency (PyInstaller).
- build_installer.bat: creates venv, builds EXE, optionally builds installer.
- version_info.txt: Windows version metadata for the EXE.
- assets\app.ico: optional app icon (multi-size .ico).
- installer\installer.iss: Inno Setup script.
- installer\LICENSE.txt: license text placeholder.
- dist\, build\, output\: generated artifacts.

## Run from source
- Ensure Python 3.8+ with Tkinter.
- Command:
    python work_time_calculator.py
- Linux:
    python3 work_time_calculator.py
- Quick Tkinter check:
    python -m tkinter
- Linux quick check:
    python3 -m tkinter

## Linux/WSL notes
- Install Tk from your OS package manager (not pip).
  - Ubuntu/Debian: sudo apt-get install -y python3-tk
  - Fedora: sudo dnf install -y python3-tkinter
  - Arch: sudo pacman -S tk
- In WSL, enable WSLg (Windows 11) or run an X server and set DISPLAY.

## Build EXE (PyInstaller, Windows only)
- Recommended: run build_installer.bat (creates .venv and builds onedir EXE).
- Manual command:
    pyinstaller --noconfirm --clean --windowed --name WorkTimeCalculator --icon assets\app.ico --version-file version_info.txt work_time_calculator.py
- Onefile alternative (slower start, more AV false positives): add --onefile.

## Build installer (Inno Setup)
- Install Inno Setup 6 offline.
- GUI: open installer\installer.iss and click Compile.
- CLI:
    ISCC.exe installer\installer.iss
- Output appears in output\.

## Troubleshooting quick hits
- Missing Tkinter on Windows: reinstall Python with Tcl/Tk enabled; verify via python -m tkinter.
- Missing Tkinter on Linux: install python3-tk and verify via python3 -m tkinter.
- Linux GUI fails to open: ensure a desktop session or WSLg/X server and DISPLAY is set.
- EXE opens then closes: build without --windowed or run EXE from cmd.
- Antivirus flags onefile: use onedir and allowlist the folder.
- ISCC.exe not found: check default paths under Program Files or add to PATH.
