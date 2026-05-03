# script to re-image the UKMON calc server
# copyright Mark McIntyre, 2026-

$dtstr=(get-date -uformat "%Y%m%d")

$instdetails=(aws ec2 describe-instances --filters Name="tag:Name",Values="batchserver" --profile ukmonshared --region eu-west-2)
$instanceid= (Write-Output $instdetails| convertfrom-json)[0].reservations.instances.instanceid

aws ec2 create-image --instance-id $instanceid --name "batchserver_${dtstr}" --description "Latest Batchserver image" --profile ukmonshared --region eu-west-2