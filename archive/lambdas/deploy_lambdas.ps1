# powershell script to build and deploy the lambda functions
# 
set-location $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-1'

# cd $PSScriptRoot/fetchECSV
# sam build 
# sam deploy --profile ukmon-markmcintyre
# cd $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-1'
# cd $PSScriptRoot/searchArchive
# sam build 
# sam deploy --profile ukmon-markmcintyre
# cd $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-2'
# cd $PSScriptRoot/getExtraFilesV2
# sam build 
# sam deploy --profile default
# cd $PSScriptRoot
