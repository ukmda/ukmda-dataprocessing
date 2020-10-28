#
# powershell script to reduce a folder of A.XML files using WMPL
#

# load the helper functions
. .\helperfunctions.ps1
# read the inifile
$inifname = 'orbitsolver.ini'
$ini = get-inicontent $inifname
$outdir = $ini['orbitcalcs']['results']
$wmpl_loc = $ini['wmpl']['wmpl_loc']
$wmpl_env = $ini['wmpl']['wmpl_env']

conda activate $wmpl_env

$env:pythonpath=$wmpl_loc

python ufoTrajSolver.py $outdir $args[0] 