#Terraform 

## UKMON Terraform Modules
All infrastructure has been built with Terraform. 

For historical reasons the infrastructure is split across two accounts. Data are stored in the "empireelements" account which also manages end-user access, while compute is in the "markmcintyreastro" account. Each is managed by its own set of terraform code. 

### empireelements Account

**S3 Buckets**  
Managed by *s3.tf*:
* *ukmon-live* contains the files uploaded by the ukmon-live process. These are displayed on the main website. 
* *ukmon-shared* contains the daily data uploads from cameras, as well as the data used and produced by consolidation and matching processes.  
* *ukmeteornetworkarchive* contains the Data Archive website.  

Additionally *ukmeteornetwork.co.uk* contains the public UKMON website but this is not managed by Terraform. 

**User Accounts and IAM Rules**  
Managed by *iam.tf*:
* user *s3accessforarchive*. This user has S3FullAccess permissions. 
* user *ukmonarchive*. This user is used to execute the batch processes, and has access to Glue, Athena, DynamoDB, Cost Explorer, S3 and to run Lambdas. 
* role *S3FullAccess* is used by some lambda functions and also granted to the other account. 
* role *lambda_basic_execution* is used by some lambda functions.
* role *dailyReportRole* is used by the Lambda that sends out the daily report. 
* role *fetchECSV-fetchECSVRole-RB0AC508MNLZ* created by Cloudformation for the fetchECSV Lambda and API.
* role *AWSGlueServiceRole-ukmoncrawler* used to create/update Glue catalogues for AWS Athena. 

**IAM Policies**
Managed by *iam.tf*:
(coming soon)

### markmcintyreastro Account
This account holds all compute resources and some APIs. 

