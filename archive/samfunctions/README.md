# SAM APIs and Lambdas 
This folder contains code for the APIs and Lambdas that are deployed as SAM functions.  
SAM is AWS's serverless application model.  

# Deployment
All config is embedded in the toml files to deploy to the correct regions and accounts, so you can deploy with
``` bash
sam build
sam deploy
```

# APIS
## fetchECSV
API to download ECSV format files for individual detections. ECSV is the common data format used by multiple networks. 

## fireballApi
API for retrieving fireball-specific files

## getLiveImages
API that returns a list of live images matching a date/time pattern.

## matchPickle
API to provide an interface to retrieve data about matches. 

## searchArchive
API to provide an interface to search the archive. The API is exposed via javascript on the website.

# Internal Functions
## getExtraFilesV2
Lambda within the data processing pipeline to create extra data about each matched detection. 

## getExtraFilesEE
As above, but used in the EE account to update the main website. 

## ftpToUkmon
Lambda that is triggered when an FTPdetect file is uploaded and converts the data into the
UKMON internal format.

## Copyright
All code Copyright (C) 2018-2023 Mark McIntyre