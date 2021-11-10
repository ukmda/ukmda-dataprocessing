# fireball analyser

# NB NB NB
# this script expects the data to already be available 
$loc = Get-Location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$stationdetails=$ini['fireballs']['stationdets']
$fbfldr=$ini['fireballs']['localfolder']

# set up paths
$targpth = $fbfldr + '\' + $args[0]
set-location $targpth

conda activate $ini['wmpl']['wmpl_env']
$env:PYTHONPATH=$ini['wmpl']['wmpl_loc']

$solver = read-host -prompt "ECSV or RMS solver? (E/R)"
if ($solver -eq 'E') {
    python -m wmpl.Formats.ECSV  -l -x -w
}
else {
    python -m wmpl.Trajectory.CorrelateRMS . -l 
}
set-location $loc

#pause 
# finally upload the new data to a _man folder
#write-output "upload new files to Archive"
#aws s3 cp $targpth\upload\ $destloc/ --recursive --exclude "bkp*" 

# zip up the results in case needed later
#compress-archive -path $targpth\upload\* -DestinationPath $targpth\upload.zip -Update
#Remove-Item $targpth\upload\*
#Remove-Item $targpth\upload