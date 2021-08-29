# powershell script to build and deploy the lambda functions
# 
# remember to set AWS credentials and default region before running this or it'll fail
# $env:AWS_ACCESS_KEY_ID=....
# $env:AWS_SECRET_ACCESS_KEY=....
#
$env:AWS_DEFAULT_REGION='eu-west-2'
#compress-archive -path .\consolidateCSVs.py -destinationpath .\consolidateCSVs.zip -update
#compress-archive -path .\csvTrigger.py -destinationpath .\csvTrigger.zip -update
#compress-archive -path .\searchArchive.py -destinationpath .\searchArchive.zip -update
#compress-archive -path pytz -destinationpath .\searchArchive.zip -update
#compress-archive -path .\consolidateJpgs.py -destinationpath .\consolidateJpgs.zip -update
#compress-archive -path .\ftpfileTrigger.py -destinationpath .\ftpfileTrigger.zip -update
#compress-archive -path .\consolidateLatest.py -destinationpath .\consolidateLatest.zip -update
compress-archive -path .\consolidateKmls.py -destinationpath .\consolidateKmls.zip -update

#aws lambda update-function-code --function-name ConsolidateCSVs --zip-file fileb://consolidateCSVs.zip
#aws lambda update-function-code --function-name CSVTrigger --zip-file fileb://csvTrigger.zip
#aws lambda update-function-code --function-name searchUKmon --zip-file fileb://searchArchive.zip
#aws lambda update-function-code --function-name consolidateJpgs --zip-file fileb://consolidateJpgs.zip
#aws lambda update-function-code --function-name consolidateFTPdetect --zip-file fileb://ftpfileTrigger.zip
#aws lambda update-function-code --function-name consolidateLatest --zip-file fileb://consolidateLatest.zip
aws lambda update-function-code --function-name consolidateKmls --zip-file fileb://consolidateKmls.zip
