# maintenance

Routines used to maintain and keep data organized

* dataMaintenance.py    - cleardown and space freeing routines
* sortToDateDirs.py     - one off tool to convert the WMPL trajectory database to a new layout
* getNextBatchStart.py  - update the crontab to start the batch at the right time
* rerunFailedLambdas.py - rerun any failed lambdas
* plotStationsOnMap.py  - plot the locations of all stations on a map
* manageTraj.py         - functions to manage the trajectory database
* getUserAndKeyInfo.py  - functions to audit and manage users and keys

getUserAndKeyInfo is used by a scheduled process to roll keys every 90 days, and to 
report on accounts that have been inactive for 90 days. 