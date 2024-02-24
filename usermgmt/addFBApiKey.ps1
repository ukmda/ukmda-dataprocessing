# copyright Mark McIntyre, 2024-

# script to add an api key for a user

$username = $args[0]
aws apigateway create-api-key --name "$username" --region eu-west-1 --profile ukmda_admin --description "key for $username" --enabled