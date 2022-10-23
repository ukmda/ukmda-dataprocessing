# refreshLocalCopy.ps1

push-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1

$ini=get-inicontent analysis.ini
$localfolder=$ini['ukmondata']['localfolder']
$spls = $localfolder.split(':')
$drv = $spls[0].tolower()
$pth = $spls[1]
$locf = "/mnt/$drv$pth"

if (Test-CommandExists wslx -eq $false) 
{
    Write-Output "sorry, this script requires WSL to be enabled"
}
else {
        write-output bash -c "./refresh_local_copy.sh $locf"
}
pop-location
