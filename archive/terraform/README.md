#Terraform 

## UKMON Terraform Modules
All infrastructure has been built with Terraform. 

### MDA account
Data from cameras upload to this account in realtime for the Livestream, and each morning for the data analysis and archive. This account holds the marshalling server, ECS cluster and containers that run the distributed trajectory solver, plus ECR repos for containers to manage data conversions and gathering for the website. It also hosts the archive website and the APIs.  

### MM account
This account hosts the EC2 instance used to trigger the batch and for management purposes. 
This is a reserved instance with a lease that expires in 2026, at which point it will be moved to the MDA account. 
This account also holds a backup of key data. 

## Copyright
All code Copyright (C) 2018-2023 Mark McIntyre