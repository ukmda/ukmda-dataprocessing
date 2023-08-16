#Terraform 

## UKMON Terraform Modules
All infrastructure has been built with Terraform. 

For historical reasons the infrastructure is split across three accounts. Data are uploaded to the UKMDA account, but replicated in the EE account for reporting and to provide a backup. The EE account also hosts the archive website. The batch / user admin server are in the MJMM account. 

### EE account
Code in here creates the S3 buckets and adds triggers to execute Lambdas when files are delivered. Only the ukmon-shared, ukmon-live and ukmeteornetworkarchive buckets are managed at present.
The APIs are served out of this account using a mixture of Lambdas and AWS SAM functions. 

### MDA account
This account holds the ECS cluster and container that runs the distributed trajectory solver, plus ECR repos for containers to manage data conversions and gathering for the website, and duplicates of the APIs.  For efficiency and security, data is uploaded to this account from the cameras, and then replicated across to the EE account for reporting and the website. 

This account also hosts the EC2 instance that is used to initiate the trajectory solving process by distributing candidates and then consolidating the results. 

### MM account
This account hosts the EC2 instance used to trigger the batch and for management purposes. 
This is a reserved instance with a lease that expires in 2026. 

## Copyright
All code Copyright (C) 2018-2023 Mark McIntyre