# powershell script to build and deploy the lambda functions
# 
# remember to set AWS credentials and default region before running this or it'll fail
# $env:AWS_ACCESS_KEY_ID=....
# $env:AWS_SECRET_ACCESS_KEY=....
#
set-location $PSScriptRoot


$env:AWS_DEFAULT_REGION='eu-west-2'

# cd $PSScriptRoot/fetchECSV
# sam build 
# sam deploy
# cd $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-2'
# cd $PSScriptRoot/searchArchive
# sam build 
# sam deploy
# cd $PSScriptRoot

