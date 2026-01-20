@echo off
setlocal enableextensions

set "ROOT=%~dp0"
cd /d "%ROOT%" || (echo [ERROR] Failed to change directory. & exit /b 1)

echo [INFO] Work Time Calculator build script

if not exist "work_time_calculator.py" (
  echo [ERROR] work_time_calculator.py not found in %CD%.
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found in PATH. Install Python 3.8+ and try again.
  exit /b 1
)

if not exist ".venv\Scripts\activate.bat" (
  echo [INFO] Creating virtual environment in .venv...
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] Failed to activate virtual environment.
  exit /b 1
)

echo [INFO] Installing requirements...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Failed to install requirements.
  exit /b 1
)

set "ICON_ARG="
if exist "assets\app.ico" (
  set "ICON_ARG=--icon assets\app.ico"
) else (
  echo [WARN] assets\app.ico not found. Building without an icon.
)

set "VERSION_ARG="
if exist "version_info.txt" (
  set "VERSION_ARG=--version-file version_info.txt"
) else (
  echo [WARN] version_info.txt not found. Building without version metadata.
)

echo [INFO] Building EXE with PyInstaller (onedir)...
pyinstaller --noconfirm --clean --windowed --name WorkTimeCalculator %ICON_ARG% %VERSION_ARG% work_time_calculator.py
if errorlevel 1 (
  echo [ERROR] PyInstaller build failed.
  exit /b 1
)

echo [INFO] Looking for Inno Setup compiler (ISCC.exe)...
set "ISCC_PATH="
for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not defined ISCC_PATH set "ISCC_PATH=%%I"
if not defined ISCC_PATH if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not defined ISCC_PATH if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC_PATH (
  echo [INFO] Running Inno Setup compiler...
  "%ISCC_PATH%" "installer\installer.iss"
  if errorlevel 1 (
    echo [ERROR] Inno Setup build failed.
    exit /b 1
  )
) else (
  echo [INFO] Inno Setup compiler not found.
  echo [INFO] To build the installer, install Inno Setup 6 and run:
  echo   ISCC.exe installer\installer.iss
)

echo [INFO] Done.
endlocal
exit /b 0
