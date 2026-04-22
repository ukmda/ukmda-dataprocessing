# script to re-image the UKMON calc server
# copyright Mark McIntyre, 2026-

$dtstr=(get-date -uformat "%Y%m%d")

$instdetails=(aws ec2 describe-instances --filters Name="tag:Name",Values="calcengine_ub" --profile ukmonshared --region eu-west-2)
$instanceid= (Write-Output $instdetails| convertfrom-json)[0].reservations.instances.instanceid

aws ec2 create-image --instance-id $instanceid --name "calcengine_${dtstr}" --description "Latest Calc Engine image" --profile ukmonshared --region eu-west-2