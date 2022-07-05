# trigger code-deploy to run deployment into EC2

$appname = "ukmon-archive-ec2"
$depgroup =  "test1" 
$repo= "markmac99/ukmon-shared"

$commitid = $(git rev-parse HEAD)

aws deploy create-deployment --application-name $appname --deployment-group $depgroup --github-location repository=$repo,commitId=$commitid