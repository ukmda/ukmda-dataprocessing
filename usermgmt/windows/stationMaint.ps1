Set-Location $psscriptroot

$env:AWS_PROFILE="ukmon-markmcintyre"

conda activate ukmon-admin
python stationMaint2.py
