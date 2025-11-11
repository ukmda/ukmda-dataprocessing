#define MyAppName "UKMON Camera Management"

[Setup]
AppName=UKMON Camera Management
AppVersion="2.0.0"
AppPublisher=UK Meteor Network
AppPublisherURL=https://www.ukmeteornetwork.org
DefaultDirName={localappdata}\programs\cameraMgmt
DefaultGroupName=UKMON
UninstallDisplayIcon={app}\stationMaint2.exe
Compression=lzma2
SolidCompression=yes
OutputDir=e:\temp
OutputBaseFilename=setup_cameraMgmt
PrivilegesRequired=lowest

[Files]
Source: ".\dist\stationMaint2.exe"; DestDir: "{app}"
Source: ".\camera.ico"; DestDir: "{app}"
Source: ".\stationmaint.ini.sample"; DestDir: "{app}"; Permissions: users-modify
Source: "..\README.md"; DestDir: "{app}"; Permissions: users-modify

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; 

[Icons]
Name: "{group}\Camera Management"; Filename: "{app}\stationMaint2.exe"; IconFilename: "{app}\camera.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\stationMaint2.exe"; Tasks: desktopicon; WorkingDir: {app}; IconFilename: "{app}\camera.ico"
