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
$fbfldr=$ini['fireballs']['localfolder']

$dt = [string]$args[0]
$cam = $args[1]
$tf = $cam + '_' + $dt + '_180000'
$targpth = "$fbfldr\$dt\$cam\$tf"

$stndet=(select-string -pattern $cam -path $stationdetails | out-string)
$stn=$stndet.split(',')[1]
$yr=$dt.substring(0,4)
$ym=$dt.substring(0,6)
$ymd=$dt

set-location $fbfldr

scp $targpth/platepar_cmn2010.cal ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/
#scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/.config $targpth
#scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/platepars_all_recalibrated.json $targpth
scp $targpth/FTPdetect*manual.txt ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/ 
Set-Location $Loc