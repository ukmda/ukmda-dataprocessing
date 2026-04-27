#!/bin/bash
# Copyright (C) 2018- Mark McIntyre

if [ "$1" == "root" ]  then 
    passwd=$(aws ssm get-parameters --names prod_rootdbpw --with-decryption --region eu-west-1 | jq .Parameters[0].Value)
else
    passwd=$(aws ssm get-parameters --names prod_dbpw --with-decryption --region eu-west-1 | jq .Parameters[0].Value)
fi 
echo $passwd
unset passwd
