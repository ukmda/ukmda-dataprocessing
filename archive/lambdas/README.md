# SAM APIs and Lambdas

This folder contains code for the APIs and Lambdas that are deployed as SAM functions.  
SAM is AWS's serverless application model.  

## Deployment

All config is embedded in the toml files to deploy to the correct regions and accounts.
If there's a `build.ps1` script use that, otherwise so you can build and deploy with

``` bash
sam build
sam deploy
```

## APIS

### fetchECSV

API to download ECSV format files for individual detections. ECSV is the common data format used by multiple networks.

### fireballApi

API for retrieving fireball-specific files

### getLiveImages

API that returns a list of live images matching a date/time pattern.

### matchDataApi

API to retrieve data about matches.

### matchPickle

API to provide an interface to retrieve data about matches.
Uses WMPL and should be rebuilt whenever WMPL is updated.

### searchArchive

API to provide an interface to search the archive. The API is exposed via javascript on the website.

### vidUploader

API to recieve uploaded videos for adding to a solution's webpage.

## Internal Functions

### getExtraFilesV2

Lambda within the data processing pipeline to create extra data about each matched detection.
Uses WMPL and should be rebuilt whenever WMPL is updated.

### monitorLiveFeed

Monitors the livestream, updates Dynamodb etc.

### ftpToUkmon

Lambda that is triggered when an FTPdetect file is uploaded and converts the data into the
UKMON internal format.

### updateDnsRecords

Monitors servers being brought online and adds a DNS record, based on fields in the Terraform script.

## Copyright

All code Copyright (C) 2018-2023 Mark McIntyre
