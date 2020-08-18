#
# powershell script to generate heatmaps and push them to a website
#
set-location $PSScriptRoot
. .\helperfunctions.ps1
$inifname = './station.ini'
if ((test-path $inifname) -eq $false) {
    write-output "station.ini file missing or invalid, can't continue"
    exit 1
}

$ini=get-inicontent $inifname
$datadir=($ini['detector']['datadir']).replace('/','\')
if((test-path $inifname) -eq $false){
    write-output "datadir missing or invalid, can't continue"
    exit 2
}

write-output 'updating colorgrammes'
Set-Location $PSScriptRoot
python .\colorgram.py

write-output "Copying to website..." 

# collect details about your website. 
$sitename=$ini['website']['sitename']
$targetdir=$ini['website']['targetdir']
$userid=$ini['website']['userid']
$key=$ini['website']['key']
$targ= $userid+'@'+$sitename+':'+$targetdir

write-output "copying latest 2d image" 
set-location $datadir
scp -o StrictHostKeyChecking=no -i $key latest2d.jpg $targ

$ssloc=$datadir+'\screenshots'
set-location $ssloc

Write-Output 'copying last capture'
$fnam=(get-childitem  event*.jpg | sort-object lastwritetime).name | select-object -last 1
copy-item $fnam  -destination latestcapture.jpg
scp -o StrictHostKeyChecking=no -i $key latestcapture.jpg $targ

Write-Output 'copying colorgramme file'
#$mmyyyy=((get-date).tostring("MMyyyy"))
$srcfile=$datadir+'\RMOB\RMOB_latest.jpg'
copy-item $srcfile -destination .
$fnam='RMOB_latest.jpg'
scp -o StrictHostKeyChecking=no -i $key $fnam $targ

$srcfile=$datadir+'\RMOB\3months_latest.jpg'
copy-item $srcfile -destination .
$fnam='3months_latest.jpg'
scp -o StrictHostKeyChecking=no -i $key $fnam $targ

$msg=(get-date -uformat '%Y5m%d-%H%M%S')+' done'
write-output $msg
set-location $PSScriptRoot
.\pushToUkmon.ps1
