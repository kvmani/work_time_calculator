; Work Time Calculator installer script
; Edit AppId, AppName, AppVersion, and AppPublisher before release.

#define AppId "{{11111111-1111-1111-1111-111111111111}}"
#define AppName "Work Time Calculator"
#define AppVersion "1.0.0"
#define AppPublisher "YOUR COMPANY"
#define AppExeName "WorkTimeCalculator.exe"
#define OutputBase "WorkTimeCalculatorSetup"
#define RepoRoot ".."
#define LicenseFilePath "{#RepoRoot}\\installer\\LICENSE.txt"
#define AppIconPath "..\\assets\\app.ico"

#if FileExists(AppIconPath)
  #define HasIcon
#endif

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppVerName={#AppName} {#AppVersion}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir={#RepoRoot}\output
OutputBaseFilename={#OutputBase}
LicenseFile={#LicenseFilePath}
WizardStyle=modern
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\{#AppExeName}
ArchitecturesInstallIn64BitMode=x64

#ifdef HasIcon
SetupIconFile={#AppIconPath}
#endif

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\\dist\\WorkTimeCalculator\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\{#AppName}"; Filename: "{app}\\{#AppExeName}"
Name: "{commondesktop}\\{#AppName}"; Filename: "{app}\\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
