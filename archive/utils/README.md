# Utils

This folder contains some utility functions useful for managing the environment.

## Used by the Batch
* cleanupDeletedTrajs.sh - checks for and removes any logically-deleted trajectories eg duplicates
* loadMatchCsvMDB.sh - loads the match data into MariaDB
* loadSingleCsvMDB.sh - loads the single-station data into MariaDB
* loadBrightCsvMDB.sh - loads brightness data into MariaDB
* clearSpace.sh - used by the batch to delete old logs etc
* clearCaches.sh - clears the in-memory cache before and after running memory-intensive jobs.

## Other routine maintenance
* checkAndRollKeys.sh - rolls station AWS Key/Secret pairs periodically to avoid stale keys
* statsToMqtt.sh - posts server space/memory etc statistics to MQ 
* userAudit.sh - performs a user audit and emails a report

## User tools to maintain data  
* deleteOrbit.sh - remove an orbit from the database and website
* updateFireballFlag.sh - marks or unmarks a match as a Fireball
* updateFireballImage.sh - updates the image shown for a fireball 
* stopstartCalcengine.sh - stops/starts the calculation engine server

## Used by the deployment tool
* makeConfig.sh - used by the  deployment process to make the config file
  
## Used in case one of the Lambdas fails
* rerunFTPtoUkMONlambra.sh - reruns FTPtoUKMON lambda
* rerunGetExtraFiles.sh - reruns  GetExtraFiles lambda 
* cftpd_templ.json - template used by the above

## The following are work in progress
* createTestDataSet.sh - work in progress
* getGmnData.sh - pulls GMN datasets from the GMN server

## Copyright
All code Copyright (C) 2018- Mark McIntyre
