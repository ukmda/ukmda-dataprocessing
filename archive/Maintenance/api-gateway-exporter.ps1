#
# Get API gateway definition from dev/test
#
# Note: after reimporting it to prod you need to edit and confirm the Lambda function link

aws apigateway get-export --parameters extensions='apigateway' --rest-api-id "0zbnc358p0" --stage-name test  --export-type swagger ukmonsearchapi.json --region eu-west-1