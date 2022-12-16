# powershell script to build and deploy the lambda functions
# 
set-location $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-1'
# cd $PSScriptRoot/fetchECSV
# sam build --profile ukmonshared
# sam deploy --profile ukmonshared
# cd $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-1'
# cd $PSScriptRoot/searchArchive
# sam build --profile ukmonshared
# sam deploy --profile ukmonshared
# cd $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-1'
# cd $PSScriptRoot/matchPickle
# sam build --profile ukmonshared
# sam deploy --profile ukmonshared
# cd $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-2'
# cd $PSScriptRoot/getExtraFilesV2
# sam build --profile default
# sam deploy --profile default
# cd $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-2'
# cd $PSScriptRoot/ftpToUkmon
# sam build --profile ukmonshared
# sam deploy --profile ukmonshared
# cd $PSScriptRoot
