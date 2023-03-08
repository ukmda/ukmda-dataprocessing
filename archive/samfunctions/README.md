# SAM APIs and Lambdas 
This folder contains code for the APIs and Lambdas that are deployed as SAM functions.  
SAM is AWS's serverless application model.  

# APIS
## fetchECSV
This code creates an API gateway and lambda to create and download ECSV format files for individual detections. ECSV is the common data format used by multiple networks. 
Created in the EE account.

## matchPickle
This code creates an API Gateway and lambda to provide an interface to retrieve data about matches. 
Created in the EE account.

## searchArchive
This code creates an API gateway and a lambda, to provide an interface to search the archive. The API is exposed via javascript on the website.
Created in the EE account.

# Internal Functions
## getExtraFilesV2
This lambda is used within the data processing pipeline to create extra data about each matched detection. 
Created in the MM  account.

## ftpToUkmon
This lambda is triggered when an FTPdetect file is uploaded and converts the data into the
UKMON internal format.
Created in the EE account.

## Copyright
All code Copyright (C) 2018-2023 Mark McIntyre