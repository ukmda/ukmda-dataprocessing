#
# powershell script to upload improved fit details of fireballs
#
# args : arg1 date, arg2 stationid
$loc = Get-Location
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$stationdetails=$ini['fireballs']['stationdets'] 

$fullftpfile = [string]$args[0]
$targpth = (split-path $fullftpfile)
$ftpname = (split-path $fullftpfile -leaf)
$cam = $ftpname.substring(14,6)
$dt = $ftpname.substring(21,8)

$stndet=(select-string -pattern $cam -path $stationdetails | out-string)
$stn=$stndet.split(',')[1]
$yr=$dt.substring(0,4)
$ym=$dt.substring(0,6)
$ymd=$dt

#scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/platepars_all_recalibrated.json $targpth
Write-Output scp $targpth/$ftpname ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/ 
Set-Location $Loc