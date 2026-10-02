#!/bin/bash

branch=$1 
key=$2 
secret=$3 

docker run -e BRANCH=$branch -e AWS_ACCESS_KEY_ID=$key -e AWS_SECRET_ACCESS_KEY=$secret -t markmac99/ukmdatester:latest