# powershell script to run docker container

if ($args.count -lt 1) {
    write-output "usage: .\run.ps1 path\to\rmsdata"
    exit 1
}
$configloc=$args[0]
$contid=(get-content ${configloc}/containerid.txt)
if ($contid) { 
    docker stop $contid 
    docker rm $contid 
}
$lastnight=(get-childitem $configloc/ArchivedFiles -directory | sort-object creationtime | select-object -last 1).name
if ( "$lastnight" -ne "" ) {
    copy-item $configloc/ArchivedFiles/$lastnight/platepar_cmn2010.cal $configloc/config
} 

$hostname=(split-path -leaf $configloc) + "-dc"
$portno=(get-content ${configloc}\config\portno)
copy-item configure_container.sh $configloc\config

$contid=(docker run --name $hostname -h $hostname -v ${configloc}:/root/RMS_data -p ${portno}:22 -d -t rms_ubuntu)
Write-Output $contid > ${configloc}/containerid.txt