# powershell script to build and deploy the lambda functions
# 
# remember to set AWS credentials and default region before running this or it'll fail
# $env:AWS_ACCESS_KEY_ID=....
# $env:AWS_SECRET_ACCESS_KEY=....
#
set-location $PSScriptRoot

$env:AWS_DEFAULT_REGION="eu-west-1"
#compress-archive -path simplefunctions\dailyReport.py -destinationpath packages\dailyReport.zip -update
#aws lambda update-function-code --function-name dailyReport --zip-file fileb://packages/dailyReport.zip

$env:AWS_DEFAULT_REGION='eu-west-2'
#compress-archive -path simplefunctions\consolidateCSVs.py -destinationpath packages\consolidateCSVs.zip -update
#aws lambda update-function-code --function-name ConsolidateCSVs --zip-file fileb://packages/consolidateCSVs.zip

#compress-archive -path simplefunctions\csvTrigger.py -destinationpath packages\csvTrigger.zip -update
#aws lambda update-function-code --function-name CSVTrigger --zip-file fileb://packages/csvTrigger.zip

#compress-archive -path simplefunctions\consolidateJpgs.py -destinationpath packages\consolidateJpgs.zip -update
#aws lambda update-function-code --function-name consolidateJpgs --zip-file fileb://packages/consolidateJpgs.zip

#compress-archive -path simplefunctions\ftpfileTrigger.py -destinationpath packages\ftpfileTrigger.zip -update
#aws lambda update-function-code --function-name consolidateFTPdetect --zip-file fileb://packages/ftpfileTrigger.zip

#compress-archive -path simplefunctions\consolidateLatest.py -destinationpath packages\consolidateLatest.zip -update
#aws lambda update-function-code --function-name consolidateLatest --zip-file fileb://packages/consolidateLatest.zip

#compress-archive -path simplefunctions\consolidateKmls.py -destinationpath packages\consolidateKmls.zip -update
#aws lambda update-function-code --function-name consolidateKmls --zip-file fileb://packages/consolidateKmls.zip

#compress-archive -path simplefunctions\matchDataApiHandler.py -destinationpath packages\matchDataApiHandler.zip -update
#aws lambda update-function-code --function-name matchDataApiHandler --zip-file fileb://packages/matchDataApiHandler.zip

# cd $PSScriptRoot/samfunctions/fetchECSV
# sam build 
# sam deploy
# cd $PSScriptRoot

$env:AWS_DEFAULT_REGION='eu-west-2'
# cd $PSScriptRoot/samfunctions/searchArchive
# sam build 
# sam deploy
# cd $PSScriptRoot

