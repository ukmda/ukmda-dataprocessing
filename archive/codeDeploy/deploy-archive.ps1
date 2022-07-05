# trigger code-deploy to run deployment into EC2

if ($args.count -lt 1 ){
    write-output "usage: deploy.ps1 prod|dev"
    exit 1
}
if (($args[0].tolower() -ne "dev") -and ($args[0].tolower() -ne "prod")) {
    write-output "usage: deploy.ps1 prod|dev"
    exit 1
}
$targ = $args[0]
$now = (get-date -uformat "%FT%H:%M:%S")
copy-item $PSScriptRoot\appspec-${targ}.yml $PSScriptRoot\..\..\appspec.yml 
git add $PSScriptRoot\..\..\appspec.yml 
git commit -m "${targ} build of ukmon-archive on ${now}"
git push

$appname = "ukmon-archive-ec2"
$depgroup =  "ukmon-archive" 
$repo= "markmac99/ukmon-shared"

$commitid = $(git rev-parse HEAD)

$depid = (aws deploy create-deployment --application-name $appname --deployment-group $depgroup --github-location repository=$repo,commitId=$commitid)

$dep = ($depid |convertfrom-json).deploymentId
sleep 5
(aws deploy get-deployment --deployment-id $dep | convertfrom-json).deploymentInfo