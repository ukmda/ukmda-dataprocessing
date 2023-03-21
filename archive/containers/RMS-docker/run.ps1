# powershell script to run docker container

if ($args.count -lt 1) {
    write-output "usage: .\run.ps1 path\to\rmsdata"
    exit 1
}
$configloc=$args[0]

$contid=(docker run -v ${configloc}:/root/RMS_data -d -t rms_ubuntu)
Write-Output $contid > ${configloc}/containerid.txt