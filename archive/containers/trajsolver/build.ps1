# build script for the docker image

$loc = get-location
set-location $psscriptroot
#. ~/.ssh/mark-creds.ps1

$imagename="trajsolver"
$accid = (aws sts get-caller-identity | convertfrom-json).account
$region = "eu-west-2"
$registry = "${accid}.dkr.ecr.${region}.amazonaws.com"
$repo = "ukmon/${imagename}"

#copy-item E:\dev\aws\awskeys\s3accessforarchive.csv .\awskeys

docker build . -t ${imagename}
if (! $?)
{
    write-output "build failed"
    exit
}
aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$registry"
docker tag ${imagename}:latest ${registry}/${repo}:latest
docker push ${registry}/${repo}:latest

set-location $loc
