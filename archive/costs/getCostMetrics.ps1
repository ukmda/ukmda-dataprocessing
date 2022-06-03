$loc = get-location
set-location $PSScriptRoot

$wmpl_loc="E:\dev\meteorhunting\WesternMeteorPyLib"
$PYLIB="E:\dev\meteorhunting\UKmon-shared\ukmon_pylib"

conda activate RMS
$env:PYTHONPATH="$wmpl_loc;$PYLIB"
$env:AWS_DEFAULT_REGION="eu-west-2"
$outdir="F:\videos\MeteorCam\ukmondata\costs"
if ((test-path $outdir) -eq 0) {mkdir $outdir}

. ~/.ssh/mark-creds.ps1
if ($args.count -eq 0) {
    python $PYLIB/metrics/costMetrics.py $outdir eu-west-2
}else{
    python $PYLIB/metrics/costMetrics.py $outdir eu-west-2 $args[0]
}

set-location $loc