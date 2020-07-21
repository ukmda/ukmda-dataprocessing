# simple script to copy then display the most recent UFO meteor captures
# and allow analysis / sanity checking before optionally uploading to UKMON

# read the inifile
set-location $PSScriptRoot
if ($args.count -eq 0) {
    $inifname='TACKLEY_TC.ini'
}
else {
    $inifname = $args[0]
}
$ini=get-content $inifname -raw | convertfrom-stringdata

# copy the latest data from the source
$yy=(get-date -uformat '%Y')
$yymm=(get-date -uformat '%Y%m')
$prvdt=
$srcpath='\\'+$ini.hostname+$ini.remotefolder+'/'+$yy+'/'+$yymm
$destpath=$ini.localfolder+'/'+$yy+'/'+$yymm
robocopy $srcpath $destpath /dcopy:DAT /tee /m /v /s /r:3 /mov

Set-location $ini.UFOPATH
$ufo=$ini.UFOPATH+'/'+$ini.UFOBINARY
& $ufo | out-null
set-location $PSScriptRoot

.\UploadToUkMon.ps1 $inifname
#pause
