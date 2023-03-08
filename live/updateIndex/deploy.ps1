# Copyright (C) 2018-2023 Mark McIntyre 

# powershell script to build and deploy the lambda function
# 
# remember to set AWS credentials  before running this or it'll fail
# $env:AWS_ACCESS_KEY_ID=....
# $env:AWS_SECRET_ACCESS_KEY=....
#

# uncomment these if starting from scratch / updating numpy
#
#Set-Location ..\curate
#compress-archive -path .\pytz -destinationpath .\createIndex.zip -force
#compress-archive -path .\numpy -destinationpath .\createIndex.zip -update
#compress-archive -path .\numpy.libs -destinationpath .\createIndex.zip -update
#Move-Item createIndex.zip ..\dailyreport -force
#Set-Location ..\dailyreport

copy-item ..\..\analysis\UFOHandler\ReadUFOCapXML.py .
copy-item ..\curate\xmltodict.py .
compress-archive -path .\*.py -destinationpath .\createIndex.zip -update
$env:AWS_DEFAULT_REGION="eu-west-1"
aws lambda update-function-code --function-name createUkmonLiveIndexes --zip-file fileb://createIndex.zip
Remove-Item xmltodict.py
Remove-item ReadUFOCapXML.py

