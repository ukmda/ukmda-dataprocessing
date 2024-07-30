#!/bin/bash

echo $1 
scp -i ~/.ssh/markskey.pem ~/.ssh/ukmon-shared-keys $1:.ssh
scp -i ~/.ssh/markskey.pem ~/.ssh/markskey.pem $1:.ssh
scp -i ~/.ssh/markskey.pem ~/.ssh/config $1:.ssh
scp -i ~/.ssh/markskey.pem ~/.ssh/gm* $1:.ssh
scp -i ~/.ssh/markskey.pem ~/.ssh/ukmon* $1:.ssh
scp -i ~/.ssh/markskey.pem ~/.ssh/marksk* $1:.ssh
scp -i ~/.ssh/markskey.pem ~/.ssh/s3* $1:.ssh

ssh  -i ~/.ssh/markskey.pem $1 mkdir setup 
ssh  -i ~/.ssh/markskey.pem $1 mkdir data
ssh  -i ~/.ssh/markskey.pem $1 mkdir src

