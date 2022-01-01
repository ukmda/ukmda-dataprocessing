#
# powershell script to reduce a folder of A.XML files to create a shower map and RMS-compatible FTPdetect file
#

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    write-output "ini file missing, can't continue"
    exit 1
}

$inifname = $args[0]
if ((test-path $inifname) -eq $false) {
    write-output "ini file missing or invalid, can't continue"
    exit 1
}

$ini=get-inicontent $inifname
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']
$locfldr=$ini['camera']['localfolder']
$isufo=$ini['camera']['UFO']

if($isufo -eq 1) {
    conda activate $rms_env
    $env:pythonpath="$rms_loc"

    $fullpath=new-object string[] ($args.count-1)
    for($i=1 ; $i -lt $args.count ; $i++)
    {
        $arg=$args[$i]
        write-output "converting $arg"
        $ymd = [string]$arg
        $yy = $ymd.substring(0, 4)
        $ym = $ymd.substring(0, 6)
        $path = $locfldr + "/" + $yy + "/" + $ym + "/" + $ymd 
        python $PSScriptRoot/UFOAtoFTPdetect.py $path
        $fullpath[$i-1] = $path + "/FTPDetectinfo_UFO.txt"
    }
    set-location $rms_loc
    python $PSScriptRoot/ufoShowerAssoc.py $fullpath[0] $fullpath[1] $fullpath[2] $fullpath[3] $fullpath[4] $fullpath[5] $fullpath[6]
    set-location $PSScriptRoot
}else{
    write-output "not supported for RMS cameras"
}