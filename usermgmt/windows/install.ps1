# deploy client-side components

# create target folder
$targ="f:\videos\meteorcam\usermgmt"
if ((test-path $targ) -eq 0 ){ mkdir $targ }

# copy scripts
robocopy $psscriptroot $targ req* *.py station* check* daily*

# create conda env if not aleady there
$isadm=(conda env list  | select-string "ukmon-admin")
if ($isadm.count -eq 0) {
    conda env create -n ukmon-admin python=3-8
    conda activate ukmon-admin
    pip install -r $targ/requirements.txt
}
