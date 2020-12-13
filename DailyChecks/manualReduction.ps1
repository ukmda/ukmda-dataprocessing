# script to run manual meteor reduction for the Pi
# args 
#   yymmdd date to copy for 
#   hhmmss time to copy for

if($args.count -lt 3) {
    Write-Output "usage: manuaReduction srcdir srcfile camerainifile"
    Write-Output "eg manuaReduction UK0006.ini 20200703 015505"
    exit
}

$srcdir=$args[0]
$srcfile=$args[1]

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$inifname = $args[0]
$ini=get-inicontent $inifname

$hostname=$ini['camera']['hostname']
$cam=$ini['camera']['camera_name']
$datadir=$ini['camera']['localfolder']
$RMSloc=$ini['rms']['rms_loc']
$rmsenv=$ini['rms']['rms_env']
$rootdir='\\'+$hostname+'\RMS_Share\' 

#crate a folder under the datadir where you'll run manual reduction 
# and make sure its empty if it already existed
$targdir=$datadir+'\manual\'
mkdir -force $targdir | out-null
set-location $targdir
remove-item *.*

# copy the required files from the CapturedFiles folder
write-output 'copying FF file'
$src=$rootdir +"CapturedFiles\"+ $cam+"_"+ $srcdir +"*\FF_"+$cam+"*"+$srcfile+"*.fits"
Copy-item $src $targdir
write-output 'copying bin file if present'
$src=$rootdir +"CapturedFiles\"+ $cam+"_"+ $srcdir +"*\FR_"+$cam+"*"+$srcfile+"*.bin"
Copy-item $src $targdir
write-output 'copying platepar file'
$src=$rootdir +"platepar*.cal"
Copy-item $src $targdir
write-output 'copying config file'
$src=$rootdir +".config"
Copy-item $src $targdir

$ffpath=$targdir+'\FF*.fits'
$ff=(Get-ChildItem $ffpath).fullname

# run the manual reduction process
set-location $RMSloc 
conda activate $rmsenv
python -m Utils.ManualReduction -c . $ff

# find the new FTPfile and the original
$ftppath=$targdir+'\FTPdetectinfo*manual.txt'
$ftp=(Get-ChildItem $ftppath).fullname

$oldftppath=$datadir+"\ArchivedFiles\"+$cam+"_"+$srcdir+"*"+'\FTPdetectinfo*.txt'
$oldftp=((Get-ChildItem $oldftppath).fullname)[0]

msg  /w $env:username "opening windows for you to edit the FTPdetect files - don't forget to change the meteor count!"

notepad $ftp
notepad $oldftp | out-null

msg $env:username "You can now rerun the Confirmation process in CMN_BinViewer if desired"
set-location $psscriptroot