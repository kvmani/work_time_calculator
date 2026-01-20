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
- Quick Tkinter check:
    python -m tkinter

## Build EXE (PyInstaller)
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
- Missing Tkinter: reinstall Python with Tcl/Tk enabled; verify via python -m tkinter.
- EXE opens then closes: build without --windowed or run EXE from cmd.
- Antivirus flags onefile: use onedir and allowlist the folder.
- ISCC.exe not found: check default paths under Program Files or add to PATH.
