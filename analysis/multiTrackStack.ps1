param ($cams, $dates, $shwrs="ALL", $outdir="c:/temp")

# multi night multi camera trackstack

push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$env:PYLIB=$ini['pylib']['pylib']
conda activate $ini['rms']['rms_env']
$env:PYTHONPATH="$PYLIB"
push-Location $ini['rms']['rms_loc']

python -m utils.multiTrackStack $cams $dates $shwrs $outdir
Pop-Location


