# Lambda functions

This folder contains code for the three Lambdas that are deployed as SAM functions.  
SAM is AWS's serverless application model.  Other lambdas as simpler and are deployed via Terraform. 

## searchArchive
This code creates an API gateway and a lambda, to provide an interface to search the archive. The 
API is exposed via javascript on the website.

## fetchECSV
This code creates an API gateway and lambda to create and download ECSV format files for individual detections. ECSV is the common data format used by multiple networks.

## getExtraFilesV2
This lambda is used internally within the data processing pipeline to create extra data about each
matched detection. Its not exposed publically. 
