set-location $PSScriptRoot

$wmpl_loc="E:\dev\meteorhunting\WesternMeteorPyLib"
$PYLIB="E:\dev\meteorhunting\UKmon-shared\ukmon_pylib"

conda activate RMS
$env:PYTHONPATH="$wmpl_loc;$PYLIB"
$env:AWS_DEFAULT_REGION="eu-west-1"


. ~/.ssh/mark-creds.ps1
python $PYLIB/metrics/getMetrics.py . eu-west-1
