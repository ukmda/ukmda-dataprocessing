# Copyright (C) 2018-2023 Mark McIntyre
Set-Location $psscriptroot

$env:SRCBUCKET="ukmda-shared"
$env:LIVEBUCKET="ukmda-live"
$env:WEBSITEBUCKET="ukmda-website"
$env:LIVE_PROFILE="ukmda_admin"
$env:ARCH_PROFILE="ukmda_admin"
$env:HELPERSERVER="ukmonhelper2"
$env:HELPERIP="3.11.55.160"
$env:REMOTEDIR="/home/ec2-user/prod/data"
$env:PLATEPARDIR=""

# create conda env if not aleady there
$isadm=(conda env list  | select-string "ukmon-admin")
if ($isadm.count -eq 0) {
    conda env create -n ukmon-admin python=3.8
    conda activate ukmon-admin
    pip install -r requirements.txt
}
else
{
    conda activate ukmon-admin
}
python stationMaint2.py
