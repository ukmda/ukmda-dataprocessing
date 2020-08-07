# a script for doing Pi Camera astrometry with the latest set of data
#
#remember where we were
$here=get-location 
# read the inifile
set-location $PSScriptRoot
# load the helper functions
. helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    $inifname='../TACKLEY_TC.ini'
}
else {
    $inifname = $args[0]
}
$ini=get-inicontent $inifname
$RMSLoc=$ini['rms']['rms_loc']
$localfolder=$ini['camera']['localfolder']
$RMSenv=$ini['rms']['rms_env']

conda activate $RMSenv

# find the latest set of data on the local drive
$destpath=$localfolder+'\ArchivedFiles'
$path=(get-childitem $destpath -directory | sort-object creationtime | select-object -last 1).name
$myf = $destpath + '\'+$path

set-location $rmsloc
python -m RMS.Astrometry.SkyFit --config . $myf

#go back to where we were
set-location $here
