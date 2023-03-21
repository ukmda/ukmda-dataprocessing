# powershell script to stop docker container

if ($args.count -lt 1) {
    write-output "usage: .\stop.ps1 path\to\config"
    exit 1
}
$configloc=$args[0]

$contid=(get-content ${configloc}/containerid.txt)
docker stop $contid