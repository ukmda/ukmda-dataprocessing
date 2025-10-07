#
# powershell script to launch the fireball data collector tool
# Copyright (C) 2018-2023 Mark McIntyre
#
push-location $PSScriptRoot

$wmpl_env=((select-string .\config.ini -pattern "wmpl_env" -list).line).split('=')[1]
$wmpl_loc=((select-string .\config.ini -pattern "wmpl_loc" -list).line).split('=')[1]

conda activate $wmpl_env

$wmpl_loc = $wmpl_loc.replace('$HOME',$env:userprofile)
$wmpl_loc = $wmpl_loc.replace('\','/')

$env:pythonpath="$wmpl_loc"

if ($args.count -lt 1) {
    python fireballCollector.py
}else {
    python fireballCollector.py -d $args[0]
}

Pop-Location


