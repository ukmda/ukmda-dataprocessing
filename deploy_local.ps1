# script to deploy the Windows scripts locally on my PC
set-location $PSScriptRoot
# load the helper functions
. .\DailyChecks\helperfunctions.ps1
# read the inifile
$ini=get-inicontent 'tackley_tc.ini'
$targ=$ini['camera']['localfolder']+'\..\scripts\'
$targ=$targ.replace('/','\')

xcopy /dy /exclude:exclude.rsp .\DailyChecks\*.ps1 $targ
xcopy /dy /exclude:exclude.rsp .\DataCollection\*.ps1 $targ
xcopy /dy /exclude:exclude.rsp *.ini $targ

xcopy /dy /exclude:exclude.rsp .\NewAnalysis\*.py $targ
xcopy /dy /exclude:exclude.rsp .\NewAnalysis\*.ps1 $targ
xcopy /dy /exclude:exclude.rsp .\NewAnalysis\FormatConverters\*.py $targ
xcopy /dy /exclude:exclude.rsp .\NewAnalysis\orbitSolver\*.py $targ
xcopy /dy /exclude:exclude.rsp .\NewAnalysis\orbitSolver\*.ps1 $targ

if ((test-path $targ\CameraCurator) -eq 0 ){ mkdir $targ\CameraCurator }
xcopy /dy /exclude:exclude.rsp .\NewAnalysis\CameraCurator\*.py $targ\CameraCurator

if ((test-path $targ\UFOHandler) -eq 0 ){ mkdir $targ\UFOHandler }
xcopy /dy /exclude:exclude.rsp .\NewAnalysis\UFOHandler\*.py $targ\UFOHandler

xcopy /dy .\Pi_Cameras\sunwait-src\sunwait.exe $targ
xcopy /dy .\UKMonCPPTools\stacker\build\Release\stacker.exe $targ
