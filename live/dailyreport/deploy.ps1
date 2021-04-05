# powershell script to build and deploy the lambda function
# 
# remember to set AWS credentials  before running this or it'll fail
# $env:AWS_ACCESS_KEY_ID=....
# $env:AWS_SECRET_ACCESS_KEY=....
#

# uncomment these if starting from scratch / updating numpy
#
#Set-Location ..\curate
#compress-archive -path .\pytz -destinationpath .\dailyReport.zip -force
#compress-archive -path .\numpy -destinationpath .\dailyReport.zip -update
#compress-archive -path .\numpy.libs -destinationpath .\dailyReport.zip -update
#Move-Item dailyReport.zip ..\dailyreport
#Set-Location ..\dailyreport
copy-item ..\..\analysis\UFOHandler\ReadUFOCapXML.py .
copy-item ..\curate\xmltodict.py .
compress-archive -path .\*.py -destinationpath .\dailyReport.zip -update
$env:AWS_DEFAULT_REGION="eu-west-1"
aws lambda update-function-code --function-name dailyReport --zip-file fileb://dailyReport.zip
Remove-Item xmltodict.py
Remove-item ReadUFOCapXML.py

