# powershell script to run docker container

$dockervols="f:\dockervols"
$thiscam="uk0006"

# this folder must exist and must contain a folder "config" containiner
# the platepar, mask and .config file
# the RMS and UKMON ssh and other keys
# the files will be copied to the required locations before RMS is started. 

$contid=(get-content $dockervols/${thiscam}_containerid.txt)

docker exec -it $contid bash