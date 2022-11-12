Set-Location $psscriptroot

$env:AWS_PROFILE="ukmonshared"

conda activate ukmon-admin
python stationMaint2.py
