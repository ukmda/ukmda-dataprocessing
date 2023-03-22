# powershell script to run docker container

if ($args.count -lt 1) {
    write-output "usage: .\run.ps1 path\to\rmsdata"
    exit 1
}
$configloc=$args[0]
$hostname=(split-path -leaf $configloc) + "-dc"
$portno=(get-content ${configloc}\config\portno)
copy-item configure_container.sh $configloc\config
$contid=(docker run -h $hostname -v ${configloc}:/root/RMS_data -p ${portno}:22 -d -t rms_ubuntu)
Write-Output $contid > ${configloc}/containerid.txt