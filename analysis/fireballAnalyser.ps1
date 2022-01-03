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
    $trajoutdir=$args[0] + '*'

    $d=(Get-ChildItem $trajoutdir).fullname
    if ($d.length -gt 0 )
    {
	foreach($direc in $d){
	    write-output "Getting extra files for $direc"
        python $env:PYLIB/traj/extraDataFiles.py $direc
	}
    }
}
else {
    python -m wmpl.Trajectory.CorrelateRMS . -l 
    if (test-path ".\processed_trajectories.json")
    {
        $json=(get-content ".\processed_trajectories.json" | convertfrom-json)
        $json.trajectories.psobject.properties.name |foreach-object { 
            $picklepath=(split-path $json.trajectories.$_.traj_file_path)
            python $env:PYLIB/traj/extraDataFiles.py $picklepath
        }
    }
}
set-location $loc
