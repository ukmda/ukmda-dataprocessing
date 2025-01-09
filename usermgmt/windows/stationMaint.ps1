# Copyright (C) 2018-2023 Mark McIntyre
push-Location $psscriptroot

# create conda env if not aleady there
$isadm=(conda env list  | select-string "ukmon-admin")
if ($isadm.count -eq 0) {
    conda env create -n ukmon-admin python=3.8
    pip install -r requirements.txt
}
conda activate ukmon-admin

bash -c "rsync -avz --delete ukmonhelper2:keymgmt/sshkeys/ ./sshkeys"
bash -c "rsync -avz --delete ukmonhelper2:keymgmt/keys/ ./keys"
bash -c "rsync -avz --delete ukmonhelper2:keymgmt/csvkeys/ ./csvkeys"
bash -c "rsync -avz --delete ukmonhelper2:keymgmt/inifs/ ./inifs"

python stationMaint2.py
Pop-Location