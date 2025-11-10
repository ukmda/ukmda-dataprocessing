#define MyAppName "UKMON Fireball Analyser"

[Setup]
AppName=UKMON Fireball Analyser
AppVersion="1.0.0"
AppPublisher=UK Meteor Network
AppPublisherURL=https://www.ukmeteornetwork.org
DefaultDirName={localappdata}\programs\fbAnalyser
DefaultGroupName=UKMON_fbAnalyser
UninstallDisplayIcon={app}\fireballCollector.exe
Compression=lzma2
SolidCompression=yes
OutputDir={src}
OutputBaseFilename=setup_fireballCollector
PrivilegesRequired=lowest

[Files]
Source: ".\dist\fireballCollector.exe"; DestDir: "{app}"
Source: ".\dist\noimage.jpg"; DestDir: "{app}"
Source: ".\dist\ukmda.ico"; DestDir: "{app}"
Source: ".\dist\download_events.sh"; DestDir: "{app}"
Source: ".\dist\config.ini.sample"; DestDir: "{app}"; Permissions: users-modify

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; 

[Icons]
Name: "{group}\Fireball Analyser"; Filename: "{app}\fireballCollector.exe"; IconFilename: "{app}\ukmda.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\fireballCollector.exe"; Tasks: desktopicon; WorkingDir: {app}; IconFilename: "{app}\ukmda.ico"
