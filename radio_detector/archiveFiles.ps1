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
$arcdir=($ini['host']['archivedir']).replace('/','\')
Set-Location $datadir
$txtdt=[string]$args[0]
$jpgdt=$txtdt.substring(2)

compress-archive -path event_log$txtdt*.txt -DestinationPath event_log$txtdt.zip
Move-Item event_log$txtdt.zip $arcdir
Remove-Item event_log$txtdt*.txt

compress-archive -path screenshots\event$jpgdt*.jpg -DestinationPath screenshots\event$jpgdt.zip
Move-Item screenshots\event$jpgdt.zip $arcdir
Remove-Item screenshots\event$jpgdt*.jpg
set-location $PSScriptRoot
