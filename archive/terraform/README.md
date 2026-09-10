#Terraform 

## UKMON Terraform Modules
Terraform code to :-  
* build and permission the batch and calculation server
* configure the S3 buckets' security, triggers and rules
* build the ECR and ECS container environments and runtime cluster
* permission users and processes
* create and permission the website (in an S3 bucket)
* create DynamoDB NoSQL database tables
* setup DNS
* log events, accesses and actions
* create the API gateway and front ends
* Create SSM variables that are used by the Python and Bash scripts

Note that the API backend and s3 event trigger lambdas are created via SAM rather than Terraform as this is simpler! 

## Copyright
All code Copyright (C) 2018- Mark McIntyre