# powershell script to build and deploy the lambda function
# 
# remember to set AWS credentials  before running this or it'll fail
# $env:AWS_ACCESS_KEY_ID=....
# $env:AWS_SECRET_ACCESS_KEY=....
#
$env:AWS_DEFAULT_REGION="eu-west-1"

# uncomment these if starting from scratch / updating numpy
#
# compress-archive -path .\pytz -destinationpath .\function.zip -force
# compress-archive -path .\numpy -destinationpath .\function.zip -update
# compress-archive -path .\numpy.libs -destinationpath .\function.zip -update
copy-item ..\..\NewAnalysis\ReadUFOCapXML.py .

compress-archive -path .\*.py -destinationpath .\function.zip -update
aws lambda update-function-code --function-name MonitorLiveFeed --zip-file fileb://function.zip

