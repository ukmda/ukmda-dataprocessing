#Terraform 

## UKMON Terraform Modules
All infrastructure has been built with Terraform. 

For historical reasons the infrastructure is split across two accounts. Data are stored in the "empireelements" account which also manages end-user access and the trajectory solver, while the batch server and system management server are in the "markmcintyreastro" account. Each is managed by its own set of terraform code. 

### empireelements Account (ee)
Code in here creates the S3 buckets and adds triggers to execute Lambdas when files are delivered. Only the ukmon-shared and ukmeteornetworkarchive buckets are managed at present.

This account also holds the ECS cluster and container that runs the distributed trajectory solver, plus ECR repos for containers to manage data conversions and gathering for the website, and the APIs that expose our raw and results data to those interested (note that the containers themselves are built with AWS SAM). 

Finally, this account hosts the EC2 instance that is used to initiate the trajectory solving
process by distributing candidates and then consolidating the results. 

In support of this, there are the usual IAM roles and permissions, security groups, NACLs
and keys.

### markmcintyreastro Account (mm)
This account hosts the EC2 instance used to trigger the batch and for management purposes. 
This is a reserved instance but once the reservation expires we'll relocate it to the EE 
account. 

Additionally, this account hosts a small server used to efficiently back up the data. 

In support of this, there are the usual IAM roles and permissions, security groups, NACLs
and keys.

## Copyright
All code Copyright (C) 2018-2023 Mark McIntyre