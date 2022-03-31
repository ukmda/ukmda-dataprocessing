#
# powershell script to grab supporting files for fireball analysis
#
# args : arg1 date, arg2 stationid
$loc = Get-Location
if ($args.count -lt 3) {
    write-output "usage: getFireballFiles.ps1 yyyymmdd HHMM UKxxxxx"
    exit 1
}
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$stationdetails=$ini['fireballs']['stationdets']
$fbfldr=$ini['fireballs']['localfolder']
$awskey=$ini['website']['awskey']
set-location $fbfldr

# read date and camera ID from commandline
$dt = [string]$args[0]
$hm = [string]$args[1]
$cam = $args[2]

# create target path
$tf = $cam + '_' + $dt + '_180000'
$targpth = "$fbfldr\$dt\$cam\$tf"
if ((test-path $targpth) -eq 0) {mkdir $targpth\upload}

# create a dummy folder so that the solver operates
$prvdt=([datetime]::parseexact($dt,'yyyyMMdd',$null).adddays(-1)).ToString('yyyyMMdd')
$prvtf = $cam + '_' + $prvdt + '_180000'
$dumtargpth = "$fbfldr\$dt\$cam\$prvtf"
if ((test-path $dumtargpth) -eq 0) {mkdir $dumtargpth}

# get details of the station and work out the date fields
$stndet=(select-string -pattern $cam -path $stationdetails | out-string)
$stn=$stndet.split(',')[1]
$yr=$dt.substring(0,4)
$ym=$dt.substring(0,6)
$ymd=$dt

# copy the required files
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/platepar_cmn2010.cal $targpth
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/.config $targpth
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/platepars_all_recalibrated.json $targpth
scp ukmonhelper:ukmon-shared/archive/$stn/$cam/$yr/$ym/$ymd/FTPdetect*.txt $targpth
(Get-Content -path $targpth/.config) -replace 'gaia_dr2_mag_11.5.npy','BSC5' > $targpth/.config.new
copy-item $targpth/.config.new $targpth/.config

# get JPGs if any
$origdt=$dt
$ftpf=(get-item "$targpth/FTPdetect*.txt")
if ([int]$hm -lt 1200) {
    $dt=([datetime]::parseexact($dt,'yyyyMMdd',$null).adddays(1)).ToString('yyyyMMdd')
}
$fitsf=(select-string $ftpf -pattern "${dt}_${hm}" -list -raw)
if ($fitsf.length -gt 2 ){
    $jpgf=$fitsf.replace('fits','jpg')
    . $awskey
    aws s3 cp s3://ukmeteornetworkarchive/img/single/$yr/$ym/$jpgf $fbfldr/$origdt
}

# job done
Set-Location $Loc