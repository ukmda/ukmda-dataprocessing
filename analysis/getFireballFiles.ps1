#
# powershell script to grab supporting files for fireball analysis
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

$prvdt=([datetime]::parseexact($dt,'yyyyMMdd',$null).adddays(-1)).ToString('yyyyMMdd')

$prvtf = $cam + '_' + $prvdt + '_180000'
$dumtargpth = "$fbfldr\$dt\$cam\$prvtf"

$stndet=(select-string -pattern $cam -path $stationdetails | out-string)
$stn=$stndet.split(',')[1]
$yr=$dt.substring(0,4)
$ym=$dt.substring(0,6)
$ymd=$dt

set-location $fbfldr
if ((test-path $targpth) -eq 0) {mkdir $targpth\upload}
if ((test-path $dumtargpth) -eq 0) {mkdir $dumtargpth\upload}

scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/platepar_cmn2010.cal $targpth
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/.config $targpth
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/platepars_all_recalibrated.json $targpth
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/FTPdetect*.txt $targpth
(Get-Content -path $targpth/.config) -replace 'gaia_dr2_mag_11.5.npy','BSC5' > $targpth/.config.new
copy-item $targpth/.config.new $targpth/.config
Set-Location $Loc