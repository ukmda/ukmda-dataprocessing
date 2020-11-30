#
# powershell script to reduce a folder of A.XML files using WMPL
#

# load the helper functions
. ..\..\DailyChecks\helperfunctions.ps1
# read the inifile
$inifname = '../../orbitsolver.ini'
$ini = get-inicontent $inifname
$disablemc = $ini['orbitcalcs']['disablemc']
$timing_offset = $ini['orbitcalcs']['timing_offset']
$plotallspatial = $ini['orbitcalcs']['plotallspatial']
$saveplots = $ini['orbitcalcs']['saveplots']

$wmpl_loc = $ini['wmpl']['wmpl_loc']
$wmpl_env = $ini['wmpl']['wmpl_env']

$here=$psscriptroot

conda activate $wmpl_env

$env:pythonpath="$wmpl_loc;..\"

Write-Output "converting to RMS/CAMS format"
python $here/../FormatConverters/UFOAtoFTPdetect.py $args[0]
Write-Output "solving for the orbit"
# arguments 
#   -x save but don't display graphs, 
#   -np don't save plots after all
#   -i image format eg jpg, png
#   -l generate detailed plots of residuals
#   -d disable monte carlo
#   -r N execute N runs 
#   -t T max timing difference between stations
#   -s solver (original or gural)

$infile=$args[0] + '/FTPdetectinfo_UFO.txt'
python $here/ufoTrajSolver.py $infile $saveplots -x $plotallspatial -t $timing_offset $disablemc
