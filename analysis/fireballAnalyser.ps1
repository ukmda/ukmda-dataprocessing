# fireball analyser

# NB NB NB
# this script expects the FF*.fits to already be available 
set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini

$stationdetails=$ini['fireballs']['stationdets']
$fbfldr=$ini['fireballs']['localgolder']

$arcfldr=$args[0]
$cam=$arcfldr.substring(0,6)
$yr=$arcfldr.substring(7,4)
$ym=$arcfldr.substring(7,6)
$yd=$arcfldr.substring(7,8)

$stndet=(select-string -pattern $cam -path $stationdetails | out-string)
$stn=$stndet.split(',')[1]

# set up paths
$targpth = $fbfldr + $cam + "\" + $arcfldr + '_200000'
$srcloc = "s3://ukmon-shared/archive/" + $stn + "/" + $cam + "/" +$yr + "/" + $ym + "/" + $yd
$destloc = "s3://ukmon-shared/archive/" + $stn + "/" + $cam + "/" +$yr + "/" + $ym + "/" + $yd +"_man"

# get required supporting files
if ((test-path $targpth\upload) -eq 0) {mkdir $targpth\upload}

aws s3 cp $srcloc/platepar_cmn2010.cal $targpth
aws s3 cp $srcloc/.config $targpth

write-output "now save the FF file into $targpth"
pause

# run SkyFit to refine the platepar and reduce the path
conda activate $ini['rms']['rms_env']
$env:PYTHONPATH=$ini['rms']['rms_loc']
python -m Utils.SkyFit2 $targpth\$ffname -c $targpth\.config

# copy the Ftpfile
copy-item $targpth\FTPdetect*manual.txt $targpth\upload 

# create the jpeg and copy it
# needs to be run in the target folder so the config file is found
push-location $targpth 
python -m Utils.BatchFFtoImage $targpth jpg
copy-item $targpth\*.jpg $targpth\upload

$ftpname=(Get-ChildItem $targpth\FTP*manual.txt).name
python -m Utils.RMS2UFO $ftpname platepar_cmn2010.cal
pop-location
copy-item $targpth\*.csv $targpth\upload

$ffname=(Get-ChildItem $targpth\FF*.fits).name
copy-item $targpth\$ffname $targpth\upload 

#create a dummy platepars_all_recalibrated
# and set auto_recalibrated to true so the data can be solved
$hdr='{"'+$ffname+'": '
Write-Output $hdr > $targpth/platepars_all_recalibrated.json
(Get-Content -path $targpth/platepar_cmn2010.cal -Raw) -replace '"auto_recalibrated": false','"auto_recalibrated": true' >> $targpth/platepars_all_recalibrated.json
Write-Output "}" >> $targpth/platepars_all_recalibrated.json
Copy-Item $targpth/platepars_all_recalibrated.json $targpth/upload

# finally upload the new data to a _man folder
write-output "upload new files to Archive"
aws s3 cp $targpth\upload\ $destloc/ --recursive --exclude "bkp*" 

# zip up the results in case needed later
compress-archive -path $targpth\upload\* -DestinationPath $targpth\upload.zip
Remove-Item $targpth\upload\*
Remove-Item $targpth\upload