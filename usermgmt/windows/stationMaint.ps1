# Copyright (C) 2018-2023 Mark McIntyre
Set-Location $psscriptroot

$env:SRCBUCKET=
$env:AWS_PROFILE=
$env:REMOTEDIR=

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
