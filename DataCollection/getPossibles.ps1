# script to copy potential meteors that were missed by RMS
# this script grabs all the FF files for which there is a corresponding FR file.
# These are events that RMS thought there may have been bright enough, even
# if it was then unable to analyse it further. 
#
# The script copies the files from the Pi, converts them into JPGs then opens an explorer 
# window so you can manually inspect them
#
# Usage: getPossibles.ps1 {inifile} {datestamp}
# eg     getPossibles.ps1 UK0006.ini 20200811
#

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -lt 2) {
    write-output "Usage: getPossibles.ps1 UK0006.ini datestampedfolder"
    exit 1
}
$inifname = $args[0]
if ((test-path $inifname) -eq $false) {
    write-output "ini file missing or invalid, can't continue"
    exit 1
}

$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
$localfolder=$ini['camera']['localfolder']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']

conda activate $rms_env
$srcdir='\\'+$hostname+'\RMS_Share\CapturedFiles\*'+$args[1]+'*'
$srcdir=(get-childitem $srcdir).fullname
$targdir=$localfolder+'/Interesting/'+$args[1]
if ((test-path $targdir) -eq $false) { mkdir $targdir | out-null }

Set-Location $srcdir
$flist=(Get-ChildItem "*.bin").basename
if ($flist.length -gt 0) {
    for ($i=0;$i -lt $flist.length;$i++)
    {
        $fn=$flist[$i]+".fits"
        $fn="FF_"+$fn.substring(3)
        write-output $fn  
        Copy-Item $fn $targdir
    }
    Set-Location $rms_loc
    python -m Utils.BatchFFtoImage $targdir jpg
    Set-Location $PSScriptRoot
#    explorer ($targdir).replace('/','\')
}
else {
    write-output "nothing of interest"
    Set-Location $PSScriptRoot
}