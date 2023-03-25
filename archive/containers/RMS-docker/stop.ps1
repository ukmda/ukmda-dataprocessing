# powershell script to stop docker container
# Copyright (C) Mark McIntyre

if ($args.count -lt 1) {
    write-output "usage: .\stop.ps1 path\to\rmsdata"
    exit 1
}
$configloc=$args[0]

$contid=(get-content ${configloc}/containerid.txt)
docker stop $contid