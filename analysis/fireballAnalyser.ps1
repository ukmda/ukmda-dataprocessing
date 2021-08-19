# fireball analyser

# NB NB NB
# this script expects the FF*.fits to already be available 

$arcfldr=$args[0]
$cam=$arcfldr.substring(0,6)
$yr=$arcfldr.substring(7,4)
$ym=$arcfldr.substring(7,6)
$yd=$arcfldr.substring(7,8)

$stationdetails='E:\dev\meteorhunting\ukmon-keymgmt\caminfo\stationdetails.csv'
$stndet=(select-string -pattern $cam -path $stationdetails | out-string)
$stn=$stndet.split(',')[1]

# set up paths
$fbfldr="F:\videos\MeteorCam\Fireballs\"
$targpth = $fbfldr + $cam + "\" + $arcfldr + '_200000'
$srcloc = "s3://ukmon-shared/archive/" + $stn + "/" + $cam + "/" +$yr + "/" + $ym + "/" + $yd
$destloc = "s3://ukmon-shared/archive/" + $stn + "/" + $cam + "/" +$yr + "/" + $ym + "/" + $yd +"_man"

# get required supporting files
if ((test-path $targpth\upload) -eq 0) {mkdir $targpth\upload}

#aws s3 cp $srcloc/ $targpth\upload --recursive --exclude "*" --include "platepars*"
#aws s3 cp $srcloc/ $targpth\upload --recursive --exclude "*" --include "FTPdetect*"
aws s3 cp $srcloc/platepar_cmn2010.cal $targpth
aws s3 cp $srcloc/.config $targpth

write-output "now save the FF file into $targpth"
pause

# run SkyFit to refine the platepar and reduce the path
conda activate RMS
Push-Location e:\dev\meteorhunting\RMS
python -m Utils.SkyFit2 $targpth\$ffname -c $targpth\.config
Pop-Location

# copy the Ftpfile
copy-item $targpth\FTPdetect*manual.txt $targpth\upload 

# create the jpeg and copy it
python -m Utils.BatchFFtoImage $targpth jpg
copy-item $targpth\*.jpg $targpth\upload

$ffname=(Get-ChildItem $targpth\FF*.fits).name
copy-item $targpth\$ffname $targpth\upload 

#create a dummy platepars_all_recalibrated
# and set auto_recalibrated to true so the dat can be locally solved
$hdr='{"'+$ffname+'": '
Write-Output $hdr > $targpth/platepars_all_recalibrated.json
(Get-Content -path $targpth/platepar_cmn2010.cal -Raw) -replace '"auto_recalibrated": false','"auto_recalibrated": true' >> $targpth/platepars_all_recalibrated.json
Write-Output "}" >> $targpth/platepars_all_recalibrated.json
Copy-Item $targpth/platepars_all_recalibrated.json $targpth/upload

# recombine the platepar and ftp file and upload them
# now edit the original FTP file and append the new data
#
# EDIT: not required, WMPL can process multiple sets of data, provided they 
# are in unique folders 
#
#write-output "now recombine the data"
#$env:PYTHONPATH="e:\dev\meteorhunting\ukmon-shared\ukmon_pylib"
#python -m traj.updateFtpAndPlate $targpth
#pause

# finally re-upload the data, overwriting the previous data
write-output "Ready to upload new files to Archive Press Ctrl-C to abort or "
aws s3 cp $targpth\upload\ $destloc/ --recursive --exclude "bkp*" 

# clean up so that the Correlator can be run safely
compress-archive -path $targpth\upload -DestinationPath upload.zip
Remove-Item upload\*
Remove-Item upload