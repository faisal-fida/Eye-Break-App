[Setup]
AppName=Eye Break App
AppVersion=1.0
DefaultDirName={commonpf}\EyeBreakApp
DefaultGroupName=Eye Break App
UninstallDisplayIcon={app}\EyeBreakApp.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Examples Output

[Files]
Source: "{#SourcePath}\EyeBreakApp.exe"; DestDir: "{app}"
Source: "{#SourcePath}\azure.tcl"; DestDir: "{app}"
Source: "C:\Users\Faisal\Videos\Eye Break\theme\*"; DestDir: "{app}\theme"; Flags: recursesubdirs

[Icons]
Name: "{group}\Eye Break App"; Filename: "{app}\EyeBreakApp.exe"
Name: "{commondesktop}\Eye Break App"; Filename: "{app}\EyeBreakApp.exe"

[Run]
Filename: "{app}\EyeBreakApp.exe"; Description: "Launch Eye Break App"; Flags: postinstall nowait

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "EyeBreakApp"; ValueData: """{app}\EyeBreakApp.exe"""; Flags: uninsdeletevalue

[Code]
var
  SourcePath: string;

procedure InitializeWizard;
begin
  SourcePath := ExpandConstant('{src}');
end;