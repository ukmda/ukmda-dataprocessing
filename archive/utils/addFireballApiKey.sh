#!/bin/bash
# copyright Mark McIntyre, 2024-

# script to add an api key for a user

username=$1

if [ "$username" == ""] ; then 
    echo "Usage ./addFireballApiKey.sh {username}
else
    aws apigateway create-api-key --name "$username" --region eu-west-1 --description "key for $username" --enabled
fi
