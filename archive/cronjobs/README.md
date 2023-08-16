# cronjobs

This folder contains the batch scripts that are run periodically to keep the archive up to date. 

## nightlyJob
This is the nightly batch job that collects camera data thats been uploaded to S3 and runs it through
the data pipeline to create the matches, and to generate the website data. 

## getIMOWSfile
This script runs periodically to collect the latest Working Showers file from the IMO. The WS file is used
in various reports to display information about showers.

## gatherMonthlyVideos
This script runs monthly to collect the best 100 videos from the previous month, which are then manually
curated and presented via our Youtube channel.

## Copyright
All code Copyright (C) 2018-2023 Mark McIntyre
