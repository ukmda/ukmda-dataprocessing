# powershell script to grab interesting files from Pi which were 
# not picked up by the automated process for some reason but 
# which you would like to examine. The script takes two parameters,
# date/time you want eg 20200619_023417 and a camera config file
# The datetime does not need to be exact, the script grabs files from +/- 20 seconds
# around the target. The files are converted tp JPG so you can easily check them.

# read the inifile
$curloc=get-location
set-location $PSScriptRoot
if ($args.count -eq 1) {
    $ini=get-content camera1.ini -raw | convertfrom-stringdata
}else {
    $ini=get-content $args[1] -raw | convertfrom-stringdata
}
# datetime of interest in YYYYMMDD_HHMMSS  format
$dtim=[datetime]::parseexact($args[0],'yyyyMMdd_HHmmss', $null)
# data is stored in a folder based on start time.
# so captures after midnight are stored in the prior days folder
$ftim = $dtim
if ($dtim.hour -lt 13 )
{
    $ftim=$dtim.adddays(-1)
}
$srcpath='\\'+$ini.hostname+'\RMS_Share\CapturedFiles\'+$ini.camera_name+'_'+$ftim.tostring('yyyyMMdd')+'*'
$srcpath=(get-childitem $srcpath).fullname

$destpath=$ini.localfolder+'/InterestingFiles/'+$ftim.tostring('yyyyMMdd')
if (-not (test-path $destpath)) {mkdir $destpath | out-null}

write-output "looking in $srcpath"
write-output "saving to $destpath"
$dtim=$dtim.AddSeconds(-20)
for ($i = 0; $i -lt 6; $i++)
{
    $dstr=$dtim.ToString('yyyyMMdd_HHmmss')
    $dstr=$dstr.substring(0,14)+'*.fits'
    $fnam=$srcpath+'\FF_'+$ini.camera_name+'_'+$dstr
    #write-output $fnam
    copy-item $fnam $destpath
    $dtim=$dtim.addseconds(10)
}
set-location $ini.rms_loc
conda activate $ini.rms_env
python -m Utils.BatchFFtoImage $destpath jpg
set-location $curloc
explorer $destpath.replace('/','\')