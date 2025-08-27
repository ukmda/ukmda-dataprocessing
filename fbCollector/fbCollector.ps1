#
# powershell script to launch the fireball data collector tool
# Copyright (C) 2018-2023 Mark McIntyre
#
push-location $PSScriptRoot

. .\helperfunctions.ps1
$ini=get-inicontent .\config.ini

conda activate $ini['solver']['wmpl_env']
$wmplloc = $ini['solver']['wmpl_loc']
$wmplloc = $wmplloc.replace('$HOME',$env:userprofile)

$env:pythonpath="$wmplloc"

if ($args.count -lt 1) {
    python fireballCollector.py
}else {
    python fireballCollector.py -d $args[0]
}

Pop-Location


