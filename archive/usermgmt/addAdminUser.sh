#!/bin/bash
# simple script to create a new user-maintenance account
# and save the access key locally. Can only be used by an account with IAM Admin permissions. 
$username = $args[0]
aws iam create-user --user-name $username --profile ukmda_admin
aws iam add-user-to-group --user-name $username --user-group Administrators --profile ukmda_admin
