# powershell script to build and deploy the lambda functions
# 
# remember to set AWS credentials and default region before running this or it'll fail
# $env:AWS_ACCESS_KEY_ID=....
# $env:AWS_SECRET_ACCESS_KEY=....
#
$env:AWS_DEFAULT_REGION='eu-west-2'
compress-archive -path .\consolidateCSVs.py -destinationpath .\consolidateCSVs.zip -update
compress-archive -path .\csvTrigger.py -destinationpath .\csvTrigger.zip -update
aws lambda update-function-code --function-name ConsolidateCSVs --zip-file fileb://consolidateCSVs.zip
aws lambda update-function-code --function-name CSVTrigger --zip-file fileb://csvTrigger.zip

