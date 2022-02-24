# fireball analyser

# NB NB NB
# this script expects the data to already be available 
$loc = Get-Location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

#$stationdetails=$ini['fireballs']['stationdets']
$fbfldr=$ini['fireballs']['localfolder']
$env:PYLIB=$ini['pylib']['pylib']

# set up paths
$targpth = $fbfldr + '\' + $args[0]
set-location $targpth

conda activate $ini['wmpl']['wmpl_env']
$wmplloc=$ini['wmpl']['wmpl_loc']
$env:pythonpath="$wmplloc;$env:pylib"

# Write-Output $env:pythonpath

$solver = read-host -prompt "ECSV or RMS solver? (E/R)"
if ($solver -eq 'E') {
    python -m wmpl.Formats.ECSV . -l -x -w $args[1]
}
else {
    python -m wmpl.Trajectory.CorrelateRMS . -l 
}
set-location $loc
conda deactivate
