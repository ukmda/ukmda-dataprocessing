#Terraform 

## UKMON Terraform Modules
All infrastructure has been built with Terraform. 

Data from cameras upload to this account in realtime for the Livestream, and each morning for the data analysis and archive. This account holds the batch server, calculation server, ECS cluster and containers that run the distributed trajectory solver, plus ECR repos for containers to manage data conversions and gathering for the website. It also hosts the archive website and the APIs.  

## Copyright
All code Copyright (C) 2018-2023 Mark McIntyre