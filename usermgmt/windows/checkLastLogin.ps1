# powershell script to check last access time of a user

$jsonlist=(aws iam list-users --profile ukmon-markmcintyre)
$data=($jsonlist | convertfrom-json)
foreach ($u in $data.Users)
{
    $jj=(aws iam generate-service-last-accessed-details --arn $u.Arn --profile ukmon-markmcintyre)
    $jid=($jj|convertfrom-json).JobId
    $res=(aws iam get-service-last-accessed-details --job-id $jid --profile ukmon-markmcintyre)
    $d = (($res |convertfrom-json).ServicesLastAccessed.LastAuthenticated).tostring('yyyy-MM-dd HH:mm:ss')
    $username = ($u.arn.split('/')[1])
    write-output "$username $d"
}