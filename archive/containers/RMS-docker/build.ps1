# build the container
# Copyright (C) Mark McIntyre

# build script for the docker image
# Copyright (C) 2018-2023 Mark McIntyre

$loc = get-location
set-location $psscriptroot

$prof = "ukmonshared"
$imagename="rms_ubuntu"
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
}else {
    write-output "To test the container do "
    write-output "cd f:\dockervols ; docker run --name $name -t $imagename -v ukmon_clean:/root/RMS_data -d"
    Write-Output "where the last arg is a folder in s3://ukmon-shared/matches/distrib"
    Write-Output "that contains candidate pickles"
}
set-location $loc
