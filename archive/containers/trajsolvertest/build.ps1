# build script for the docker image

$loc = get-location
set-location $psscriptroot

$imagename="trajsolvertest"
$accid = (aws sts get-caller-identity | convertfrom-json).account
$region = "eu-west-2"
$registry = "${accid}.dkr.ecr.${region}.amazonaws.com"
$repo = "ukmon/${imagename}"

docker build . -t ${imagename}
if (! $?)
{
    write-output "build failed"
    exit
}
set-location $loc
pause
aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$registry"
docker tag ${imagename}:latest ${registry}/${repo}:latest
docker push ${registry}/${repo}:latest

set-location $loc
