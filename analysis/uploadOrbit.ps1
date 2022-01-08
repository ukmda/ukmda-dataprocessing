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
    $srcpath="trajectories/$yr/$ym/$yd/$newname"
}
$targ="ukmonhelper:ukmon-shared/matches/RMSCorrelate/trajectories/$yr/$ym/$yd/$newname"

# copy the trajectory solution over
scp -pr $srcpath $targ

# now invoke the script to build the index page and update the daily index.
$nixpath="$yr/$ym/$yd/$newname"
$cmd="/home/ec2-user/prod/website/createPageIndex.sh" 
$pth="/home/ec2-user/ukmon-shared/matches/RMSCorrelate/trajectories/$nixpath"
$opt="force"

# update the jpgs file
$sp = (split-path $srcpath)
$yyyymmdd=(get-item $sp).name
$yyyymm=$yyyymmdd.substring(0,6)
$yyyy=$yyyymmdd.substring(0,4)
$imgloc="img/single/$yyyy/$yyyymm"
scp "ukmonhelper:$pth/jpgs.lst" .
$jpglst=(Get-ChildItem ".\*.jpg").name
if ($jpglst -is [array])
{
    for ($i=0; $i -lt $jpglst.length ; $i++)
    {
        $jpg=$jpglst[$i]
        write-output "$imgloc/$jpg" >> jpgs.lst
        aws s3 cp "$jpg" "s3://ukmeteornetworkarchive/$imgloc/"
    }
}
else {
    write-output "$imgloc/$jpglst" >> jpgs.lst
}
# and copy it back to the server then rebuild the index
scp jpgs.lst "ukmonhelper:$pth/" 
ssh ukmonhelper "dos2unix $pth/jpgs.lst"

ssh ukmonhelper "$cmd $pth $opt"
ssh ukmonhelper "scp $pth/*orbit.csv /home/ec2-user/prod/data/orbits/$yr/csv/"
ssh ukmonhelper "scp $pth/*orbit_extras.csv /home/ec2-user/prod/data/orbits/$yr/extracsv/"

# finally update the daily index
$cmd="/home/ec2-user/prod/website/createOrbitIndex.sh " 
ssh ukmonhelper "$cmd $yyyymmdd"