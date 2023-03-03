# build script for the docker image

$loc = get-location
set-location $psscriptroot

$prof = "default"
$imagename="simpleui"
$accid = (aws sts get-caller-identity --profile $prof | convertfrom-json).account
$region = "eu-west-2"
$registry = "${accid}.dkr.ecr.${region}.amazonaws.com"
$repo = "ukmon/${imagename}"

docker build . -t ${imagename}
if (! $?)
{
    write-output "build failed"
    exit
}
$yn=read-host -prompt "upload to ECR?"
if ($yn.tolower() -eq "y") {
    aws ecr get-login-password --region "$region" --profile $prof | docker login --username AWS --password-stdin "$registry"
    docker tag ${imagename}:latest ${registry}/${repo}:latest
    docker push ${registry}/${repo}:latest
}

write-output "To test the container do docker docker run  -p 8000:80 -d $imagefile" 
write-output "then goto localhost:8000"

set-location $loc
