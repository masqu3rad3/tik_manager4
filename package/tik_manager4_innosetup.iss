#define appName "Tik Manager4"
#define appVersion "4.3.0-alpha"

[Setup]
AppId={{0BAFF3AF-5D10-4CA9-9232-428F16D17175}
AppName={#appName}
AppVersion={#appVersion}
DefaultDirName={commonpf64}\TikWorks\tik_manager4
DefaultGroupName=Tik Works
UninstallDisplayIcon={app}\MyProg.exe
Compression=lzma2
SolidCompression=yes
OutputBaseFilename=TikManager4_v{#appVersion}
SetupIconFile=..\tik_manager4\ui\theme\rc\tik_main.ico
WizardStyle=modern
OutputDir=".\build"

DisableWelcomePage=no
LicenseFile="..\LICENSE"
; InfoBeforeFile=readme.txt
; UserInfoPage=yes
; PrivilegesRequired=lowest
DisableDirPage=no
DisableProgramGroupPage=yes
InfoAfterFile="..\README.md"

[Files]
Source: "..\tik_manager4\*"; Excludes: "build,__pycache__,*.pyc,*.spec,.pytest_cache"; DestDir: "{app}"; Flags: ignoreversion createallsubdirs recursesubdirs

[Icons]
Name: "{group}\{#appName}"; Filename: "{app}\MyProg.exe"
Name: "{autoprograms}\{#appName}"; Filename: "{app}\dist\tik4\tik4_standalone.exe"
Name: "{autoprograms}\Tik4Photoshop"; Filename: "{app}\dist\tik4\tik4_photoshop.exe"
Name: "{autodesktop}\{#appName}"; Filename: "{app}\dist\tik4\tik4_standalone.exe"; Tasks: desktopicon
Name: "{autodesktop}\Tik4Photoshop"; Filename: "{app}\dist\tik4\tik4_photoshop.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "Maya"; Description: "Maya"; Flags: checkedonce
Name: "Houdini"; Description: "Houdini"; Flags: checkedonce
Name: "Max"; Description: "3dsMax"; Flags: checkedonce
Name: "Blender"; Description: "Blender"; Flags: checkedonce
Name: "Nuke"; Description: "Nuke"; Flags: checkedonce
Name: "Photoshop"; Description: "Photoshop"; Flags: checkedonce
Name: "Katana"; Description: "Katana"; Flags: checkedonce
Name: "Mari"; Description: "Mari"; Flags: checkedonce
Name: "Gaffer"; Description: "Gaffer"; Flags: checkedonce
Name: "Substance"; Description: "Substance 3d Painter"; Flags: checkedonce


[Code]
type
  IntegerArray = array [1..10] of integer;
var
  OutputProgressWizardPage: TOutputProgressWizardPage;
  OutputProgressWizardPageAfterID: Integer;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  Position, Max: Integer;
begin
  if CurPageID = OutputProgressWizardPageAfterID then begin
    try
      Max := 25;
      for Position := 0 to Max do begin
        OutputProgressWizardPage.SetProgress(Position, Max);
        if Position = 0 then
          OutputProgressWizardPage.Show;
        Sleep(2000 div Max);
      end;
    finally
      OutputProgressWizardPage.Hide;
    end;
  end;
  Result := True;
end;

function GetActiveTasks(ss: String): String;
var
  strFlag: String;
begin
  strFlag := ' ';
    if WizardIsTaskSelected('Maya') then
      strFlag := strFlag + 'Maya';
    if WizardIsTaskSelected('Houdini') then
      strFlag := strFlag + ' ' + 'Houdini';
    if WizardIsTaskSelected('Max') then
      strFlag := strFlag + ' ' + '3dsMax';
    if WizardIsTaskSelected('Blender') then
      strFlag := strFlag + ' ' + 'Blender';
    if WizardIsTaskSelected('Nuke') then
      strFlag := strFlag + ' ' + 'Nuke';
    if WizardIsTaskSelected('Photoshop') then
      strFlag := strFlag + ' ' + 'Photoshop';
    if WizardIsTaskSelected('Katana') then
      strFlag := strFlag + ' ' + 'Katana';
    if WizardIsTaskSelected('Mari') then
      strFlag := strFlag + ' ' + 'Mari';
    if WizardIsTaskSelected('Gaffer') then
      strFlag := strFlag + ' ' + 'Gaffer';
    if WizardIsTaskSelected('Substance') then
      strFlag := strFlag + ' ' + 'Substance';
result := strFlag;
end;

////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;


/////////////////////////////////////////////////////////////////////
function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;


/////////////////////////////////////////////////////////////////////
function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
// Return Values:
// 1 - uninstall string is empty
// 2 - error executing the UnInstallString
// 3 - successfully executed the UnInstallString

  // default return value
  Result := 0;

  // get the uninstall string of the old app
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

/////////////////////////////////////////////////////////////////////
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;


[Run]
Filename: "{app}\dist\tik4\install_dccs.exe"; Parameters: "-b {code:GetActiveTasks}";

