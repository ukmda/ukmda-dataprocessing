#daily upload of Pi data to the UKMON archive

$curloc=get-location
set-location $PSScriptRoot
if ($args.count -eq 0) {
    $ini=get-content camera1.ini -raw | convertfrom-stringdata
}else {
    $ini=get-content $args[0] -raw | convertfrom-stringdata
}

# for this to be useable you must be a UKMON contributor 
# contact us on Facebook to start contributing! 

$ismember=$ini.UKMON_member
if ($ismember -eq 'Yes')
{
    $keyfile=$ini.UKMON_keyfile
    $ukmoncam=$ini.UKMON_camname

    $keys=((Get-Content $keyfile)[1]).split(',')
    $Env:AWS_ACCESS_KEY_ID = $keys[0]
    $env:AWS_SECRET_ACCESS_KEY = $keys[1]
    $yr = (get-date).year

    $srcpath=$ini.localfolder+'/'+$yr+'/'

    $targ= 's3://ukmon-shared/archive/' + $ukmoncam +'/'+$yr+'/'

    if ($ini.UFO -eq 0)
    {
        aws s3 sync $srcpath $targ --include * --exclude *.fits --exclude *.bin --exclude *.gif  --exclude *.bz2 
    }
    else
    {
        aws s3 sync $srcpath $targ --exclude * --include *.csv --include *P.jpg --include *.txt --include *.xml --exclude *detlog.csv
    }
    Write-Output 'checked and uploaded any new files'
}
else {
    Write-Output 'check ini file to make sure ukmon details are set'
    Write-Output 'as this script will only work if you are set up as a contributor'
}
set-location $curloc