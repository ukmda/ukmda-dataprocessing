; -- Example1.iss --
; Demonstrates copying 3 files and creating an icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

#define MyAppName "ufoCurator"

[Setup]
AppName=ufoCurator
AppVersion=1.0
AppPublisher="UK Meteor Network"
AppPublisherURL=https://ukmeteornetwork.co.uk/
DefaultDirName={commonpf64}\ufoCurator
DefaultGroupName=ufoCurator
UninstallDisplayIcon={app}\curateUFO.exe
Compression=lzma2
SolidCompression=yes
OutputDir="."
OutputBaseFilename=curateUFO-setup64

[Files]
Source: ".\build\exe.win-amd64-3.8\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: ".\build\exe.win-amd64-3.8\curation.ini"; DestDir: "{app}"; Permissions: users-modify

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; 

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\curateUFO.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\curateUFO.exe"; Tasks: desktopicon; WorkingDir: {app}; IconFilename: "{app}\icon.ico"

[Code]
function InitializeSetup(): Boolean;
var
  oldVersion: String;
  uninstaller: String;
  ErrorCode: Integer;
begin
  if RegKeyExists(HKEY_LOCAL_MACHINE,'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ufoCurator_is1') then
  begin
    if MsgBox('Previous version must first be uninstalled, click ok to proceed', mbConfirmation, MB_OKCANCEL) = IDOK then
    begin
      RegQueryStringValue(HKEY_LOCAL_MACHINE,'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ufoCurator_is1','UninstallString', uninstaller);
      ShellExec('runas', uninstaller, '/SILENT', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
      Result := True;
    end else
      Result := False;
  end else 
    Result := True;
end;