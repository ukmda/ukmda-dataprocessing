#
# powershell script to launch the fireball data collector tool
#
push-location $PSScriptRoot

. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$fbfldr=$ini['fireballs']['localfolder']
$env:PYLIB=$ini['pylib']['pylib']

conda activate ukmon-shared
$wmplloc=$ini['wmpl']['wmpl_loc']
$env:pythonpath="$wmplloc;$env:pylib"

set-location python
python fireballCollector.py $args[1]

explorer $fbfldr

Pop-Location

