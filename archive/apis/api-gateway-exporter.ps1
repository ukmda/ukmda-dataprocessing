#
# Get API gateway definition from dev/test
#
# Note: after reimporting it to prod you need to edit and confirm the Lambda function link

set-location $PSScriptRoot
aws apigateway get-export --parameters extensions='apigateway' --rest-api-id "oaa3lqdkvf" --stage-name prod  --export-type swagger ukmonMatchApi.json --region eu-west-1
aws apigateway get-export --parameters extensions='apigateway' --rest-api-id "lx6dt0krxj" --stage-name prod  --export-type swagger ukmonsearchapi.json --region eu-west-1