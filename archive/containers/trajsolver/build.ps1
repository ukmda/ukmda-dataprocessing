# build script for the docker image
# Copyright (C) 2018-2023 Mark McIntyre

$loc = get-location
set-location $psscriptroot

$env=$args[0]
$prof="ukmonshared"
$imagename="trajsolver${env}"
$accid = (aws sts get-caller-identity --profile $prof | convertfrom-json).account
$region = "eu-west-2"
$registry = "${accid}.dkr.ecr.${region}.amazonaws.com"
$repo = "ukmon/${imagename}"

write-output "building $imagename"

$yn=read-host -prompt "update WMPL?"
if ($yn.tolower() -eq "y") { bash -c "./update_wmpl.sh $env" } 

if ($env -eq "test") { copy-item awskeys.test awskeys}

docker build . -t ${imagename}
if (! $?)
{
    write-output "build failed"
    exit
}
set-location $loc
if ($env -eq "test") { Remove-Item awskeys}

$yn=read-host -prompt "upload to ECR?"
if ($yn.tolower() -eq "y") {
    aws ecr get-login-password --region "$region" --profile $prof | docker login --username AWS --password-stdin "$registry"
    docker tag ${imagename}:latest ${registry}/${repo}:latest
    docker push ${registry}/${repo}:latest
}else {
    write-output "To test the container do docker run -t $imagename 20220924_01"
    Write-Output "where the last arg is a folder in s3://ukmon-shared/matches/distrib"
    Write-Output "that contains candidate pickles"
}


set-location $loc
