# Utils

This folder contains some utility functions useful for managing the environment.

## Used by the Batch
* clearSpace.sh - used by the batch to delete old logs etc
* clearCaches.sh - clears the in-memory cache. Not used much.

## User tools to maintain data  
* deleteOrbit.sh - remove an orbit from the database and website
* updateFireballFlag.sh - marks or unmarks a match as a Fireball
* updateFireballImage.sh - updates the image shown for a fireball 
* stopstart-calcengine.sh - stops/starts the calculation engine server

## Used by the deployment tool
* makeConfig.sh - used by the  deployment process to make the config file
  
## Used in case one of the Lambdas fails
* rerunconsolidateFTPdetect.sh - reruns the lambda
* rerunFTPtoUkMONlambra.sh - reruns the lambda
* rerun GetExtraFiles.sh - reruns the lambda
* cftpd_templ.json - template used by the above

## The following are work in progress
* monthlyClearDown.sh - should be run monthly to clear down old data 
* createTestDataSet.sh - work in progress

## Copyright
All code Copyright (C) 2018-2023 Mark McIntyre
