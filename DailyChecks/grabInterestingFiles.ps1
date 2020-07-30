# powershell script to grab interesting files from Pi which were 
# not picked up by the automated process for some reason but 
# which you would like to examine. The script takes two parameters,
# date/time you want eg 20200619_023417 and a camera config file
# The datetime does not need to be exact, the script grabs files from +/- 20 seconds
# around the target. The files are converted tp JPG so you can easily check them.

set-location $PSScriptRoot
# load the helper functions
. helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    $inifname='../TACKLEY_TC.ini'
}
else {
    $inifname = $args[0]
}
$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
#$remotefolder=$ini['camera']['remotefolder']
$localfolder=$ini['camera']['localfolder']
$camera_name=$ini['camera']['camera_name']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']

# datetime of interest in YYYYMMDD_HHMMSS  format
$dtim=[datetime]::parseexact($args[0],'yyyyMMdd_HHmmss', $null)
# data is stored in a folder based on start time.
# so captures after midnight are stored in the prior days folder
$ftim = $dtim
if ($dtim.hour -lt 13 )
{
    $ftim=$dtim.adddays(-1)
}
$srcpath='\\'+$hostname+'\RMS_Share\CapturedFiles\'+$camera_name+'_'+$ftim.tostring('yyyyMMdd')+'*'
$srcpath=(get-childitem $srcpath).fullname

$destpath=$localfolder+'/InterestingFiles/'+$ftim.tostring('yyyyMMdd')
if (-not (test-path $destpath)) {mkdir $destpath | out-null}

write-output "looking in $srcpath"
write-output "saving to $destpath"
$dtim=$dtim.AddSeconds(-20)
for ($i = 0; $i -lt 6; $i++)
{
    $dstr=$dtim.ToString('yyyyMMdd_HHmmss')
    $dstr=$dstr.substring(0,14)+'*.fits'
    $fnam=$srcpath+'\FF_'+$camera_name+'_'+$dstr
    #write-output $fnam
    copy-item $fnam $destpath
    $dtim=$dtim.addseconds(10)
}
set-location $rms_loc
conda activate $rms_env
python -m Utils.BatchFFtoImage $destpath jpg
set-location $curloc
explorer $destpath.replace('/','\')