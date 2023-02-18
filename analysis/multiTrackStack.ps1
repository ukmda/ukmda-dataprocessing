param ($cams, $dates, $shwrs="ALL", $outdir="c:/temp", $scalefactor=1)

# multi night multi camera trackstack

push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$PYLIB=$ini['pylib']['pylib']
$RMSLOC=$ini['rms']['rms_loc']
conda activate $ini['rms']['rms_env']
$env:PYTHONPATH="$PYLIB;$RMSLOC"

push-Location $ini['rms']['rms_loc']

python -m usertools.multiTrackStack $cams $dates -s $shwrs -o $outdir -f $scalefactor
Pop-Location


