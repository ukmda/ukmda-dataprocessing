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

# copy the trajectory solution over
$targ="ukmon-shared/matches/RMSCorrelate/trajectories/$yr/$ym/$yd/$newname"
aws s3 sync "$srcpath" "s3://$targ" --include "*" --exclude "*.jpg"

# add row to dailyreport file
$env:DATADIR="f:\videos\meteorcam\ukmondata"
$newl=(python -c "import reports.reportOfLatestMatches as rml ; print(rml.processLocalFolder('$srcpath','/home/ec2-user/ukmon-shared/matches/RMSCorrelate'))")

$dlyfile="$yd.txt"
scp "ukmonhelper:prod/data/dailyreports/$dlyfile" .
$x=(select-string $newl $dlyfile)
if ($x.length -eq 0)
{
    add-content $dlyfile $newl
}
scp "$dlyfile" "ukmonhelper:prod/data/dailyreports/" 

# now invoke the script to build the index page and update the daily index.
$cmd="/home/ec2-user/prod/website/updateIndexPages.sh /home/ec2-user/prod/data/dailyreports/$dlyfile"
ssh ukmonhelper "$cmd"
set-location $loc

# update the jpgs file
#$sp = (split-path $srcpath)
#$yyyymmdd=(get-item $sp).name
#$yyyymm=$yyyymmdd.substring(0,6)
#$yyyy=$yyyymmdd.substring(0,4)
#$imgloc="img/single/$yyyy/$yyyymm"
#scp "ukmonhelper:$pth/jpgs.lst" .
#$jpglst=(Get-ChildItem ".\*.jpg").name
#if ($jpg.length -gt 0) {
#    if ($jpglst -is [array])
#    {
#        for ($i=0; $i -lt $jpglst.length ; $i++)
#        {
##            $jpg=$jpglst[$i]
#            write-output "$imgloc/$jpg" >> jpgs.lst
#            aws s3 cp "$jpg" "s3://ukmeteornetworkarchive/$imgloc/"
#        }
#    }
#    else {
#        write-output "$imgloc/$jpglst" >> jpgs.lst
#        aws s3 cp "$jpglst" "s3://ukmeteornetworkarchive/$imgloc/"
#    }
#}
# and copy it back to the server then rebuild the index
#scp jpgs.lst "ukmonhelper:$pth/" 
#ssh ukmonhelper "dos2unix $pth/jpgs.lst"
