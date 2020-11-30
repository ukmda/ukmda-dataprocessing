#
# script to get livestream including bad and fireballs
#

$curloc = get-location
set-location $PSScriptRoot

# load the helper functions
. .\helperfunctions.ps1

# read the inifile
$ini=get-inicontent 'archive.ini'
$keyfile=$ini['live']['keyfile'] 
$remotefolder=$ini['live']['remotefolder'] 
$localfolder=$ini['live']['localfolder'] 
$remotebad=$ini['live']['remotebad'] 
$badfolder=$ini['live']['badfolder'] 
$fbfolder=$ini['live']['fbfolder'] 
#$ffmpeg=$ini['live']['ffmpeg'] 

$oldkey = $Env:AWS_ACCESS_KEY_ID
$oldsec = $env:AWS_SECRET_ACCESS_KEY

$keys=((Get-Content $keyfile)[1]).split(',')
$Env:AWS_ACCESS_KEY_ID = $keys[0]
$env:AWS_SECRET_ACCESS_KEY = $keys[1]

aws s3 sync $remotefolder $localfolder --exclude "*" --include "*.jpg" --include "*.xml" --exclude "*temp*"
aws s3 sync $remotefolder $fbfolder --exclude "*" --include "*.mp4" --exclude "*temp*"
aws s3 sync $remotebad $badfolder --exclude "*" --include "*.jpg" --include "*.xml" --exclude "*temp*"

$Env:AWS_ACCESS_KEY_ID = $oldkey
$env:AWS_SECRET_ACCESS_KEY = $oldsec
set-location $curloc