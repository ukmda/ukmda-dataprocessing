# a script for doing Pi Camera astrometry with the latest set of data
#
#remember where we were
$here=get-location 
# read the inifile
set-location $PSScriptRoot
if ($args.count -eq 0) {
    $ini=get-content camera1.ini -raw | convertfrom-stringdata
}else {
    $ini=get-content $args[0] -raw | convertfrom-stringdata
}
$RMSloc=$ini.rms_loc

# find the latest set of data on the local drive
$destpath=$ini.localfolder+'\ArchivedFiles'
$path=(get-childitem $destpath -directory | sort-object creationtime | select-object -last 1).name
$myf = $destpath + '\'+$path

set-location $rmsloc
python -m RMS.Astrometry.SkyFit --config . $myf

#go back to where we were
set-location $here
