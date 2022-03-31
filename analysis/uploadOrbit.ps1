#
# Powershell script to upload revised fireball data to the website
#

# args : arg1 fbdate arg2 target orbit

$loc = Get-Location
if ($args.count -lt 1) {
    write-output "usage: uploadOrbit.ps1 fbdate orbitname"
    write-output "eg 20220107 20220107-212952.143_UK"
    write-output "eg 20220107  20220107-212952.143488"
    Write-Output "note that the latter format will be renamed with an underscore"
    exit 1
}

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini
set-location $loc

$awskey=$ini['website']['awskey']
. $awskey

$fbfldr=$ini['fireballs']['localfolder']
$fbdate=$args[0]
set-location $fbfldr\$fbdate

$env:PYLIB=$ini['pylib']['pylib']
conda activate $ini['wmpl']['wmpl_env']
$wmplloc=$ini['wmpl']['wmpl_loc']
$env:pythonpath="$wmplloc;$env:pylib"


if ((test-path $args[1]) -eq "True" )
{
    $newname=$args[1].replace('-','_') 
    $newname = $newname.substring(0, $newname.length-3)+"_UK"
    Rename-Item $args[1] $newname
    $yr=$newname.substring(0,4)
    $ym=$newname.substring(0,6)
    $yd=$newname.substring(0,8)
    $srcpath="$fbfldr/$fbdate/$newname"
}else{
    $newname=$args[1]
    $yr=$newname.substring(0,4)
    $ym=$newname.substring(0,6)
    $yd=$newname.substring(0,8)
    $srcpath="$fbfldr/$fbdate/trajectories/$yr/$ym/$yd/$newname"
}

# sort out the jpegs
out-file -filepath $srcpath/extrajpgs.html
$jpgs=(get-item $fbfldr/$fbdate/*.jpg).name
if ($jpgs -is [array]) {
    foreach ($jpg in $jpgs){
        $li = "<a href=""/img/single/${yr}/${ym}/${jpg}""><img src=""/img/single/${yr}/${ym}/${jpg}"" width=""20%""></a>"
        write-output $li  | out-file $srcpath/extrajpgs.html -append
    }
} else {
    $li = "<a href=""/img/single/${yr}/${ym}/${jpgs}""><img src=""/img/single/${yr}/${ym}/${jpgs}"" width=""20%""></a>"
    write-output $li  | out-file $srcpath/extrajpgs.html -append
}

# copy the trajectory solution over
$targ="ukmeteornetworkarchive/reports/$yr/orbits/$ym/$yd/$newname"
aws s3 sync "$srcpath" "s3://$targ" --include "*" --exclude "*.jpg"
$targ="ukmon-shared/matches/RMSCorrelate/trajectories/$yr/$ym/$yd/$newname"
aws s3 sync "$srcpath" "s3://$targ" --exclude "*" --include "*.pickle" --include "*report.txt"

# add row to dailyreport file
$pf=(Get-ChildItem "$srcpath/*.pickle").fullname
$pf=$pf.replace('\','/')
$env:DATADIR="f:/videos/meteorcam/ukmondata"
$newl=(python -c "import reports.reportOfLatestMatches as rml ; print(rml.processLocalFolder('$pf','/home/ec2-user/ukmon-shared/matches/RMSCorrelate'))")

$dlyfile="$yd.txt"
scp "ukmonhelper:prod/data/dailyreports/$dlyfile" .
$x=(select-string $newl $dlyfile)
if ($x.length -eq 0)
{
    add-content $dlyfile $newl
    scp "$dlyfile" "ukmonhelper:prod/data/dailyreports/" 
}

# now invoke the script to build the index page and update the daily index.
$cmd="/home/ec2-user/prod/website/updateIndexPages.sh /home/ec2-user/prod/data/dailyreports/$dlyfile"
ssh ukmonhelper "$cmd"
set-location $loc
