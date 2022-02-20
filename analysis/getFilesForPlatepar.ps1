#
# powershell script to grab supporting files for fireball analysis
#
# args : arg1 date, arg2 stationid
$loc = Get-Location
if ($args.count -lt 2) {
    write-output "usage: getFilesForPlatepar.ps1 UKxxxxx reqdate"
    exit 1
}
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$stationdetails=$ini['fireballs']['stationdets']
$fbfldr=$ini['fireballs']['localfolder']
$ppfldr=$fbfldr+'/../platepars'

# camera ID from commandline
$cam = $args[0]
if($args.Count -gt 1){
    $dt = [string]$args[1]
}
else {
    $dt=(get-date -uformat '+%Y%m%d')    
}
$yr=$dt.substring(0,4)
$ym=$dt.substring(0,6)
$ymd=$dt

# create target path
$targpth = "$ppfldr\$cam\$dt"
if ((test-path $targpth) -eq 0) {mkdir $targpth}

set-location $targpth

# get details of the station and work out the date fields
$stndet=(select-string -pattern $cam -path $stationdetails | out-string)
$stn=$stndet.split(',')[1]

# copy the required files
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/platepar_cmn2010.cal $targpth
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/.config $targpth
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/*.fits $targpth
(Get-Content -path $targpth/.config) -replace 'gaia_dr2_mag_11.5.npy','BSC5' > $targpth/.config.new
copy-item $targpth/.config.new $targpth/.config

# job done
Set-Location $Loc