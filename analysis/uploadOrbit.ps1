#
# Powershell script to upload revised fireball data to the website
#

# args : arg1 target orbit eg trajectories\2021\202111\20211117\20211117_054502.196_UK

$loc = Get-Location
if ($args.count -lt 1) {
    write-output "usage: uploadOrbit.ps1 path-to-orbit eg trajectories\2021\202111\20211117\20211117_054502.196_UK"
    exit 1
}

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
$ini=get-inicontent analysis.ini
set-location $loc

$awskey=$ini['website']['awskey']
. $awskey

# copy the trajectory solution over
$srcpath=$args[0]
$targ="ukmonhelper:ukmon-shared/matches/RMSCorrelate/$srcpath"
scp -pr $srcpath $targ

# now invoke the script to build the index page and update the daily index.
$nixpath=$srcpath.replace('\','/')
$cmd="/home/ec2-user/prod/website/createPageIndex.sh" 
$pth="/home/ec2-user/ukmon-shared/matches/RMSCorrelate/$nixpath"
$opt="force"
ssh ukmonhelper "$cmd $pth $opt"

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
ssh ukmonhelper "$cmd $pth"

# finally update the daily index
$cmd="/home/ec2-user/prod/website/createOrbitIndex.sh " 
ssh ukmonhelper "$cmd $yyyymmdd"