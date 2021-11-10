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
$env:PYLIB=$ini['pylib']['pylib']

# set up paths
$targpth = $fbfldr + '\' + $args[0]
set-location $targpth

conda activate $ini['wmpl']['wmpl_env']
$env:PYTHONPATH="$ini['wmpl']['wmpl_loc'];$env:PYLIB"

$solver = read-host -prompt "ECSV or RMS solver? (E/R)"
if ($solver -eq 'E') {
    python -m wmpl.Formats.ECSV . -l -x -w $args[1]
    $d=(dir 20210808*).fullname
    if ($d.length -gt 0 )
    {
        python $env:PYLIB/traj/extraDataFiles.py $d
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

#pause 
# finally upload the new data to a _man folder
#write-output "upload new files to Archive"
#aws s3 cp $targpth\upload\ $destloc/ --recursive --exclude "bkp*" 

# zip up the results in case needed later
#compress-archive -path $targpth\upload\* -DestinationPath $targpth\upload.zip -Update
#Remove-Item $targpth\upload\*
#Remove-Item $targpth\upload