Set-Location $psscriptroot
. ~/.ssh/ukmon-markmcintyre.ps1
conda activate ukmon-admin
python stationMaint2.py
