# build script for the docker image
# Copyright (C) 2018-2023 Mark McIntyre

$loc = get-location
set-location $psscriptroot

$prof="ukmonshared"
$imagename="trajsolvertest"
$accid = (aws sts get-caller-identity --profile $prof | convertfrom-json).account
$region = "eu-west-2"
$registry = "${accid}.dkr.ecr.${region}.amazonaws.com"
$repo = "ukmon/${imagename}"

$yn=read-host -prompt "update WMPL?"
if ($yn.tolower() -eq "y") { bash -c "./update_wmpl.sh" } 

docker build . -t ${imagename}
if (! $?)
{
    write-output "build failed"
    exit
}
set-location $loc
pause
aws ecr get-login-password --region "$region" --profile $prof | docker login --username AWS --password-stdin "$registry"
docker tag ${imagename}:latest ${registry}/${repo}:latest
docker push ${registry}/${repo}:latest

set-location $loc
